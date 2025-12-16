"""
CarQuery API Client
Free, public API for vehicle makes, models, and specifications
API Docs: http://www.carqueryapi.com/api/0.3/
"""
import aiohttp
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class CarQueryClient:
    BASE_URL = "https://www.carqueryapi.com/api/0.3/"

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        """Ensure aiohttp session exists"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def get_makes(self, year: Optional[int] = None) -> List[Dict]:
        """
        Get all car makes (brands)

        Args:
            year: Optional year to filter makes

        Returns:
            List of dicts with make info: [{"make_id": "bmw", "make_display": "BMW", "make_country": "Germany"}, ...]
        """
        await self._ensure_session()

        params = {
            "cmd": "getMakes"
        }

        if year:
            params["year"] = year

        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                if data and "Makes" in data:
                    makes = data["Makes"]
                    logger.info(f"Fetched {len(makes)} makes from CarQuery")
                    return makes

                return []

        except Exception as e:
            logger.error(f"Error fetching makes from CarQuery: {e}")
            return []

    async def get_models(self, make: str, year: Optional[int] = None) -> List[Dict]:
        """
        Get all models for a specific make

        Args:
            make: Car make (e.g., "bmw", "volkswagen")
            year: Optional year to filter models

        Returns:
            List of dicts with model info: [{"model_name": "M3", "model_trim": "Competition", ...}, ...]
        """
        await self._ensure_session()

        params = {
            "cmd": "getModels",
            "make": make.lower()
        }

        if year:
            params["year"] = year

        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                if data and "Models" in data:
                    models = data["Models"]
                    logger.info(f"Fetched {len(models)} models for {make} from CarQuery")
                    return models

                return []

        except Exception as e:
            logger.error(f"Error fetching models for {make} from CarQuery: {e}")
            return []

    async def get_trims(self, make: str, model: str, year: Optional[int] = None) -> List[Dict]:
        """
        Get all trims/variants for a specific make and model

        Args:
            make: Car make (e.g., "bmw")
            model: Car model (e.g., "M3")
            year: Optional year

        Returns:
            List of dicts with detailed trim info including specs
        """
        await self._ensure_session()

        params = {
            "cmd": "getTrims",
            "make": make.lower(),
            "model": model
        }

        if year:
            params["year"] = year

        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                if data and "Trims" in data:
                    trims = data["Trims"]
                    logger.info(f"Fetched {len(trims)} trims for {make} {model} from CarQuery")
                    return trims

                return []

        except Exception as e:
            logger.error(f"Error fetching trims for {make} {model} from CarQuery: {e}")
            return []

    async def get_model_details(self, model_id: str) -> Optional[Dict]:
        """
        Get detailed specifications for a specific model by ID

        Args:
            model_id: The model_id from CarQuery

        Returns:
            Dict with complete model specifications
        """
        await self._ensure_session()

        params = {
            "cmd": "getModel",
            "model": model_id
        }

        try:
            async with self.session.get(self.BASE_URL, params=params) as response:
                response.raise_for_status()
                data = await response.json()

                if data:
                    logger.info(f"Fetched details for model {model_id}")
                    return data[0] if isinstance(data, list) and len(data) > 0 else data

                return None

        except Exception as e:
            logger.error(f"Error fetching model details for {model_id}: {e}")
            return None


# Global instance
carquery_client = CarQueryClient()
