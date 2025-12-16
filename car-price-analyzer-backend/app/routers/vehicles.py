"""
Vehicle Data Router
Endpoints for fetching makes, models, and specifications from external APIs
"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Dict
from app.services.vehicle_data_service import vehicle_data_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("/makes")
async def get_makes(force_refresh: bool = Query(False, description="Force refresh from API")) -> List[Dict]:
    """
    Get all available car makes/brands

    Returns:
        List of makes with display names and countries
    """
    try:
        makes = await vehicle_data_service.get_makes(force_refresh=force_refresh)
        return makes
    except Exception as e:
        logger.error(f"Error fetching makes: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching makes: {str(e)}")


@router.get("/models/{make}")
async def get_models(
    make: str,
    year: Optional[int] = Query(None, description="Filter by year"),
    force_refresh: bool = Query(False, description="Force refresh from API")
) -> List[Dict]:
    """
    Get all models for a specific make

    Args:
        make: Car make (e.g., "BMW", "Volkswagen")
        year: Optional year filter
        force_refresh: Force refresh from API

    Returns:
        List of models with year ranges
    """
    try:
        models = await vehicle_data_service.get_models_for_make(
            make=make,
            year=year,
            force_refresh=force_refresh
        )
        return models
    except Exception as e:
        logger.error(f"Error fetching models for {make}: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching models: {str(e)}")


@router.get("/specs/{make}/{model}")
async def get_vehicle_specs(
    make: str,
    model: str,
    year: int = Query(..., description="Model year")
) -> Dict:
    """
    Get detailed specifications for a specific vehicle

    Args:
        make: Car make
        model: Car model
        year: Model year

    Returns:
        Detailed vehicle specifications including engine, transmission, etc.
    """
    try:
        specs = await vehicle_data_service.get_vehicle_specs(
            make=make,
            model=model,
            year=year
        )

        if not specs:
            raise HTTPException(
                status_code=404,
                detail=f"No specifications found for {make} {model} ({year})"
            )

        return specs
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching specs for {make} {model} ({year}): {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching specifications: {str(e)}")


@router.post("/refresh-cache")
async def refresh_cache() -> Dict:
    """
    Refresh all cached data from APIs

    Returns:
        Status message
    """
    try:
        # Refresh makes
        makes = await vehicle_data_service.get_makes(force_refresh=True)

        return {
            "status": "success",
            "message": f"Cache refreshed successfully. {len(makes)} makes cached."
        }
    except Exception as e:
        logger.error(f"Error refreshing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Error refreshing cache: {str(e)}")
