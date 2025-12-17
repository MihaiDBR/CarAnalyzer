"""
Car Catalog Router - Hierarchical brands and models
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.services.car_catalog_service import car_catalog_service

router = APIRouter()


@router.get("/catalog/brands")
async def get_brands():
    """
    Get all available brands with premium brands first

    Returns:
        [
            {"value": "audi", "label": "Audi", "isPremium": true},
            {"value": "bmw", "label": "BMW", "isPremium": true},
            ...
        ]
    """
    try:
        brands = await car_catalog_service.get_brands()
        return {
            'success': True,
            'brands': brands
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog/models/{marca}")
async def get_model_series(marca: str):
    """
    Get hierarchical model series for a brand

    For BMW: Returns Seria 1, Seria 2, Seria 3, etc.
    For VW: Returns Golf, Polo, Passat, etc.

    Returns:
        [
            {
                "series": "Seria 3",
                "count": 45,
                "variants": ["316d", "318d", "320d", "M3"]
            },
            ...
        ]
    """
    try:
        series_list = await car_catalog_service.get_model_series(marca)
        return {
            'success': True,
            'series': series_list
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog/year-range/{marca}/{model_series}")
async def get_year_range(marca: str, model_series: str):
    """Get available year range for a model series"""
    try:
        year_range = await car_catalog_service.get_year_range(marca, model_series)
        return {
            'success': True,
            'yearRange': year_range
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/catalog/variants/{marca}/{model_series}")
async def get_variants(marca: str, model_series: str):
    """Get performance variants for a model series"""
    try:
        variants = await car_catalog_service.get_variants_for_series(marca, model_series)
        return {
            'success': True,
            'variants': variants
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
