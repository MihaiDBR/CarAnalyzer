from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas import CarAnalysisRequest, PriceAnalysisResponse, PricingStrategy, MarketAnalysisResponse
from app.analysis.price_analyzer import PriceAnalyzer
from app.analysis.flexible_price_analyzer import flexible_analyzer
from app.analysis.smart_price_analyzer import smart_analyzer
from app.database import database, saved_analyses

router = APIRouter()

@router.post("/analyze", response_model=PriceAnalysisResponse)
async def analyze_car_price(request: CarAnalysisRequest):
    """
    Analizează prețul optim pentru o mașină
    Folosește SMART ANALYZER cu auto-scraping:
    1. Verifică DB pentru date recente
    2. Dacă lipsesc → trigger scraping automat
    3. Returnează prețuri realiste din piața reală
    """
    try:
        # Use SMART analyzer with auto-scraping!

        # Calculate SMART year range (±1 year for newer cars, ±2 for older)
        if request.an >= 2020:
            year_range = 1  # Newer cars: stricter range
        elif request.an >= 2015:
            year_range = 1  # Recent cars: ±1 year
        else:
            year_range = 2  # Older cars: ±2 years

        an_min = max(1990, request.an - year_range)
        an_max = min(2025, request.an + year_range)

        # Calculate SMART km range (tighter ranges for better results)
        km_center = request.km
        if km_center <= 50000:
            # Low km: ±5k range
            km_range = 5000
        elif km_center <= 100000:
            # Medium km: ±10k range
            km_range = 10000
        elif km_center <= 150000:
            # High km: ±15k range
            km_range = 15000
        else:
            # Very high km: ±20k range
            km_range = 20000

        km_min = max(0, km_center - km_range) if km_center > 0 else 0
        km_max = km_center + km_range if km_center > 0 else 500000

        print(f"\n=== Search Parameters ===")
        print(f"Car: {request.marca} {request.model}")
        print(f"User input: Year {request.an}, KM {request.km:,}")
        print(f"Search range: Year {an_min}-{an_max}, KM {km_min:,}-{km_max:,}")
        print(f"Filters: {request.combustibil}, {request.transmisie or 'any'}, {request.caroserie or 'any'}")

        result = await smart_analyzer.analyze_with_auto_scraping(
            marca=request.marca,
            model=request.model,
            an_min=an_min,
            an_max=an_max,
            km_min=km_min,
            km_max=km_max,
            combustibil=request.combustibil,
            transmisie=request.transmisie,
            caroserie=request.caroserie,
        )

        response = PriceAnalysisResponse(
            pret_rapid=PricingStrategy(**result['pret_rapid']),
            pret_optim=PricingStrategy(**result['pret_optim']),
            pret_negociere=PricingStrategy(**result['pret_negociere']),
            pret_maxim=PricingStrategy(**result['pret_maxim']),
            valoare_dotari=result['valoare_dotari'],
            market_data=MarketAnalysisResponse(**result['market_data']),
            timestamp=datetime.now()
        )

        return response

    except Exception as e:
        # This should NEVER happen with flexible analyzer, but just in case
        raise HTTPException(status_code=500, detail=f"Eroare neașteptată: {str(e)}")