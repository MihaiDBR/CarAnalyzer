from fastapi import APIRouter, HTTPException
from datetime import datetime

from app.schemas import CarAnalysisRequest, PriceAnalysisResponse, PricingStrategy, MarketAnalysisResponse
from app.analysis.price_analyzer import PriceAnalyzer
from app.analysis.flexible_price_analyzer import flexible_analyzer
from app.database import database, saved_analyses

router = APIRouter()

@router.post("/analyze", response_model=PriceAnalysisResponse)
async def analyze_car_price(request: CarAnalysisRequest):
    """
    Analizează prețul optim pentru o mașină
    Folosește sistemul FLEXIBIL care funcționează pentru ORICE mașină!
    """
    try:
        # Use flexible analyzer - ALWAYS returns a result, never throws error!
        result = await flexible_analyzer.calculate_price_with_fallback(
            request.marca,
            request.model,
            request.an,
            request.km,
            request.dotari
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