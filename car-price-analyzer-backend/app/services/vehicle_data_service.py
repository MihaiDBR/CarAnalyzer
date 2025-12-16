"""
Vehicle Data Service
Aggregates data from multiple APIs (CarQuery, NHTSA) and caches results in database
"""
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from app.integrations.carquery import carquery_client
from app.integrations.nhtsa import nhtsa_client
from app.database import database, api_makes_cache, api_models_cache, vehicle_specs_cache
from app.config.major_manufacturers import is_major_manufacturer, normalize_make_name

logger = logging.getLogger(__name__)

class VehicleDataService:
    CACHE_DURATION_DAYS = 30  # Cache data for 30 days

    async def get_makes(self, force_refresh: bool = False) -> List[Dict]:
        """
        Get all car makes, with intelligent caching

        Args:
            force_refresh: Force refresh from API even if cache exists

        Returns:
            List of makes: [{"make": "BMW", "display": "BMW", "country": "Germany"}, ...]
        """
        if not force_refresh:
            # Check cache first
            cached_makes = await self._get_cached_makes()
            if cached_makes:
                logger.info(f"Returning {len(cached_makes)} makes from cache")
                return cached_makes

        # Fetch from both APIs
        logger.info("Fetching makes from APIs...")
        carquery_makes = await carquery_client.get_makes()
        nhtsa_makes = await nhtsa_client.get_makes()

        # Merge and deduplicate
        makes_dict = {}

        # Process CarQuery makes
        for make in carquery_makes:
            make_id = make.get("make_id", "").lower()
            if make_id and is_major_manufacturer(make_id):
                normalized_name = normalize_make_name(make.get("make_display", make_id.capitalize()))
                makes_dict[make_id] = {
                    "make": make_id.capitalize(),
                    "display": normalized_name,
                    "country": make.get("make_country", ""),
                    "source": "carquery"
                }

        # Process NHTSA makes (merge with existing) - FILTER only major manufacturers
        for make in nhtsa_makes:
            make_name = make.get("Make_Name", "")
            if make_name and is_major_manufacturer(make_name):
                make_id = make_name.lower()
                normalized_name = normalize_make_name(make_name)

                if make_id not in makes_dict:
                    makes_dict[make_id] = {
                        "make": normalized_name,
                        "display": normalized_name,
                        "country": "",
                        "source": "nhtsa"
                    }

        # Convert to list and sort alphabetically
        makes_list = sorted(makes_dict.values(), key=lambda x: x["display"])

        # Cache results in database
        await self._cache_makes(makes_list)

        logger.info(f"Fetched and cached {len(makes_list)} makes")
        return makes_list

    async def get_models_for_make(self, make: str, year: Optional[int] = None, force_refresh: bool = False) -> List[Dict]:
        """
        Get all models for a specific make

        Args:
            make: Car make (e.g., "BMW", "Volkswagen")
            year: Optional year filter
            force_refresh: Force refresh from API

        Returns:
            List of models: [{"model": "M3 Competition", "year_min": 2018, "year_max": 2024}, ...]
        """
        if not force_refresh:
            # Check cache
            cached_models = await self._get_cached_models(make, year)
            if cached_models:
                logger.info(f"Returning {len(cached_models)} models for {make} from cache")
                return cached_models

        # Fetch from APIs
        logger.info(f"Fetching models for {make} from APIs...")

        models_dict = {}

        # Try CarQuery first
        carquery_models = await carquery_client.get_models(make, year)
        for model in carquery_models:
            model_name = model.get("model_name", "")
            if model_name:
                model_key = model_name.lower()
                if model_key not in models_dict:
                    models_dict[model_key] = {
                        "model": model_name,
                        "year_min": model.get("model_year_min"),
                        "year_max": model.get("model_year_max"),
                        "body_type": model.get("model_body", ""),
                        "source": "carquery"
                    }

        # Try NHTSA
        if year:
            nhtsa_models = await nhtsa_client.get_models_for_make_year(make, year)
        else:
            nhtsa_models = await nhtsa_client.get_models_for_make(make)

        for model in nhtsa_models:
            model_name = model.get("Model_Name", "")
            if model_name:
                model_key = model_name.lower()
                if model_key not in models_dict:
                    models_dict[model_key] = {
                        "model": model_name,
                        "year_min": None,
                        "year_max": None,
                        "body_type": "",
                        "source": "nhtsa"
                    }

        # Convert to list and sort
        models_list = sorted(models_dict.values(), key=lambda x: x["model"])

        # Cache results
        await self._cache_models(make, models_list)

        logger.info(f"Fetched and cached {len(models_list)} models for {make}")
        return models_list

    async def get_vehicle_specs(self, make: str, model: str, year: int) -> Optional[Dict]:
        """
        Get detailed specifications for a specific vehicle

        Args:
            make: Car make
            model: Car model
            year: Model year

        Returns:
            Dict with specifications or None
        """
        # Check cache
        cached_specs = await self._get_cached_specs(make, model, year)
        if cached_specs:
            logger.info(f"Returning specs for {make} {model} ({year}) from cache")
            return cached_specs

        # Fetch from CarQuery (more detailed for specs)
        logger.info(f"Fetching specs for {make} {model} ({year}) from APIs...")

        trims = await carquery_client.get_trims(make, model, year)

        if trims and len(trims) > 0:
            # Use first trim as default
            trim = trims[0]

            specs = {
                "make": make,
                "model": model,
                "year": year,
                "trim": trim.get("model_trim", ""),
                "engine": trim.get("model_engine_type", ""),
                "horsepower": trim.get("model_engine_power_hp"),
                "transmission": trim.get("model_transmission_type", ""),
                "drive_type": trim.get("model_drive", ""),
                "fuel_type": trim.get("model_fuel_type", ""),
                "body_type": trim.get("model_body", ""),
                "doors": trim.get("model_doors"),
                "seats": trim.get("model_seats"),
                "source": "carquery"
            }

            # Cache it
            await self._cache_specs(specs)

            return specs

        return None

    # ==================== PRIVATE CACHE METHODS ====================

    async def _get_cached_makes(self) -> List[Dict]:
        """Get makes from cache if not expired"""
        cutoff_date = datetime.now() - timedelta(days=self.CACHE_DURATION_DAYS)

        query = api_makes_cache.select().where(
            api_makes_cache.c.cached_at > cutoff_date
        )

        rows = await database.fetch_all(query)

        if rows:
            return [
                {
                    "make": row["make_name"],
                    "display": row["make_display"] or row["make_name"],
                    "country": row["make_country"] or "",
                    "source": row["source"]
                }
                for row in rows
            ]

        return []

    async def _cache_makes(self, makes: List[Dict]):
        """Cache makes in database"""
        # Delete old cache
        await database.execute(api_makes_cache.delete())

        # Insert new cache
        for make_data in makes:
            query = api_makes_cache.insert().values(
                make_name=make_data["make"],
                make_display=make_data["display"],
                make_country=make_data.get("country", ""),
                source=make_data.get("source", "unknown")
            )
            await database.execute(query)

    async def _get_cached_models(self, make: str, year: Optional[int] = None) -> List[Dict]:
        """Get models from cache if not expired"""
        cutoff_date = datetime.now() - timedelta(days=self.CACHE_DURATION_DAYS)

        query = api_models_cache.select().where(
            (api_models_cache.c.make_name == make.lower()) &
            (api_models_cache.c.cached_at > cutoff_date)
        )

        rows = await database.fetch_all(query)

        if rows:
            models = []
            for row in rows:
                # Filter by year if specified
                if year:
                    year_min = row["model_year_min"]
                    year_max = row["model_year_max"]
                    if year_min and year_max:
                        if year < year_min or year > year_max:
                            continue

                models.append({
                    "model": row["model_name"],
                    "year_min": row["model_year_min"],
                    "year_max": row["model_year_max"],
                    "body_type": row["body_type"] or "",
                    "source": row["source"]
                })

            return models

        return []

    async def _cache_models(self, make: str, models: List[Dict]):
        """Cache models in database"""
        # Delete old cache for this make
        delete_query = api_models_cache.delete().where(
            api_models_cache.c.make_name == make.lower()
        )
        await database.execute(delete_query)

        # Insert new cache
        for model_data in models:
            query = api_models_cache.insert().values(
                make_name=make.lower(),
                model_name=model_data["model"],
                model_year_min=model_data.get("year_min"),
                model_year_max=model_data.get("year_max"),
                body_type=model_data.get("body_type", ""),
                fuel_type=model_data.get("fuel_type", ""),
                source=model_data.get("source", "unknown")
            )
            await database.execute(query)

    async def _get_cached_specs(self, make: str, model: str, year: int) -> Optional[Dict]:
        """Get vehicle specs from cache"""
        cutoff_date = datetime.now() - timedelta(days=self.CACHE_DURATION_DAYS)

        query = vehicle_specs_cache.select().where(
            (vehicle_specs_cache.c.make == make) &
            (vehicle_specs_cache.c.model == model) &
            (vehicle_specs_cache.c.year == year) &
            (vehicle_specs_cache.c.cached_at > cutoff_date)
        )

        row = await database.fetch_one(query)

        if row:
            return dict(row)

        return None

    async def _cache_specs(self, specs: Dict):
        """Cache vehicle specs in database"""
        query = vehicle_specs_cache.insert().values(
            make=specs["make"],
            model=specs["model"],
            year=specs["year"],
            trim=specs.get("trim"),
            engine=specs.get("engine"),
            horsepower=specs.get("horsepower"),
            transmission=specs.get("transmission"),
            drive_type=specs.get("drive_type"),
            fuel_type=specs.get("fuel_type"),
            body_type=specs.get("body_type"),
            doors=specs.get("doors"),
            seats=specs.get("seats"),
            standard_equipment=specs.get("standard_equipment"),
            optional_equipment=specs.get("optional_equipment"),
            source=specs.get("source", "unknown"),
            source_id=specs.get("source_id")
        )
        await database.execute(query)


# Global instance
vehicle_data_service = VehicleDataService()
