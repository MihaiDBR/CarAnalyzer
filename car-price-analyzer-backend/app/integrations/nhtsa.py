"""
NHTSA Vehicle API Client
Free, public API from US National Highway Traffic Safety Administration
API Docs: https://vpic.nhtsa.dot.gov/api/
"""
import aiohttp
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

class NHTSAClient:
    BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"

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

    async def get_makes(self) -> List[Dict]:
        """
        Get all vehicle makes from NHTSA

        Returns:
            List of dicts: [{"Make_ID": 440, "Make_Name": "BMW"}, ...]
        """
        await self._ensure_session()

        url = f"{self.BASE_URL}/GetAllMakes?format=json"

        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                if data and "Results" in data:
                    makes = data["Results"]
                    logger.info(f"Fetched {len(makes)} makes from NHTSA")
                    return makes

                return []

        except Exception as e:
            logger.error(f"Error fetching makes from NHTSA: {e}")
            return []

    async def get_models_for_make(self, make: str) -> List[Dict]:
        """
        Get all models for a specific make

        Args:
            make: Make name (e.g., "BMW", "Volkswagen")

        Returns:
            List of dicts with model info
        """
        await self._ensure_session()

        url = f"{self.BASE_URL}/GetModelsForMake/{make}?format=json"

        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                if data and "Results" in data:
                    models = data["Results"]
                    logger.info(f"Fetched {len(models)} models for {make} from NHTSA")
                    return models

                return []

        except Exception as e:
            logger.error(f"Error fetching models for {make} from NHTSA: {e}")
            return []

    async def get_models_for_make_year(self, make: str, year: int) -> List[Dict]:
        """
        Get models for a specific make and year

        Args:
            make: Make name
            year: Model year

        Returns:
            List of dicts with model info for that year
        """
        await self._ensure_session()

        url = f"{self.BASE_URL}/GetModelsForMakeYear/make/{make}/modelyear/{year}?format=json"

        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                if data and "Results" in data:
                    models = data["Results"]
                    logger.info(f"Fetched {len(models)} models for {make} ({year}) from NHTSA")
                    return models

                return []

        except Exception as e:
            logger.error(f"Error fetching models for {make} ({year}) from NHTSA: {e}")
            return []

    async def decode_vin(self, vin: str) -> Optional[Dict]:
        """
        Decode a VIN to get complete vehicle specifications

        Args:
            vin: 17-character VIN

        Returns:
            Dict with all vehicle specifications
        """
        await self._ensure_session()

        url = f"{self.BASE_URL}/DecodeVin/{vin}?format=json"

        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                if data and "Results" in data:
                    logger.info(f"Decoded VIN {vin}")
                    return data["Results"]

                return None

        except Exception as e:
            logger.error(f"Error decoding VIN {vin}: {e}")
            return None

    async def get_vehicle_variable_list(self) -> List[Dict]:
        """
        Get all available vehicle variables (specifications) that NHTSA tracks

        Returns:
            List of all vehicle data variables
        """
        await self._ensure_session()

        url = f"{self.BASE_URL}/GetVehicleVariableList?format=json"

        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                if data and "Results" in data:
                    variables = data["Results"]
                    logger.info(f"Fetched {len(variables)} vehicle variables from NHTSA")
                    return variables

                return []

        except Exception as e:
            logger.error(f"Error fetching vehicle variables from NHTSA: {e}")
            return []

    async def get_equipment_plant_codes(self, year: int) -> List[Dict]:
        """
        Get equipment plant codes for a specific year

        Args:
            year: Model year

        Returns:
            List of equipment codes
        """
        await self._ensure_session()

        url = f"{self.BASE_URL}/GetEquipmentPlantCodes/{year}?format=json"

        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                data = await response.json()

                if data and "Results" in data:
                    return data["Results"]

                return []

        except Exception as e:
            logger.error(f"Error fetching equipment codes for {year}: {e}")
            return []


# Global instance
nhtsa_client = NHTSAClient()
