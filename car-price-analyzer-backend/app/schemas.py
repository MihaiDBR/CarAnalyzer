# ============================================
# BACKEND - app/schemas.py
# Pydantic schemas pentru validare date
# ============================================

from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


# ============================================
# REQUEST SCHEMAS
# ============================================

class CarAnalysisRequest(BaseModel):
    """Request pentru analiză mașină"""
    marca: str = Field(..., min_length=2, max_length=50, description="Marca mașinii")
    model: str = Field(..., min_length=1, max_length=100, description="Modelul mașinii")
    an: int = Field(..., ge=1990, le=2025, description="Anul fabricației")
    km: int = Field(..., ge=0, le=1000000, description="Kilometri parcurși")
    combustibil: str = Field(..., description="Tipul de combustibil")
    dotari: List[str] = Field(default=[], description="Lista dotărilor")
    locatie: str = Field(default="bucuresti", description="Locația mașinii")

    @validator('combustibil')
    def validate_combustibil(cls, v):
        allowed = ['benzina', 'diesel', 'electric', 'hybrid', 'gpl']
        if v.lower() not in allowed:
            raise ValueError(f'Combustibil trebuie să fie unul din: {", ".join(allowed)}')
        return v.lower()

    @validator('marca', 'model')
    def validate_text(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Câmpul nu poate fi gol')
        return v.strip().title()

    class Config:
        schema_extra = {
            "example": {
                "marca": "Volkswagen",
                "model": "Golf 7",
                "an": 2018,
                "km": 85000,
                "combustibil": "diesel",
                "dotari": ["piele", "navigatie", "xenon"],
                "locatie": "bucuresti"
            }
        }


class ScrapeRequest(BaseModel):
    """Request pentru scraping"""
    marca: str
    model: str
    an_min: Optional[int] = None
    an_max: Optional[int] = None
    pret_min: Optional[float] = None
    pret_max: Optional[float] = None
    locatie: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "marca": "BMW",
                "model": "Seria 3",
                "an_min": 2015,
                "an_max": 2020,
                "pret_min": 10000,
                "pret_max": 25000,
                "locatie": "bucuresti"
            }
        }


# ============================================
# RESPONSE SCHEMAS
# ============================================

class ListingResponse(BaseModel):
    """Response pentru un anunț"""
    id: int
    source: str
    url: str
    marca: str
    model: str
    an: int
    km: int
    pret: float
    combustibil: str
    locatie: str
    dotari: List[str]
    imagini: Optional[List[str]] = []
    descriere: Optional[str] = ""
    data_publicare: datetime
    zile_pe_piata: Optional[int] = None

    class Config:
        orm_mode = True


class MarketAnalysisResponse(BaseModel):
    """Response pentru analiză piață"""
    total_listings: int
    price_mean: float
    price_median: float
    price_std: float
    price_min: float
    price_max: float
    percentile_25: float
    percentile_75: float
    days_on_market_avg: float
    regional_distribution: dict

    class Config:
        schema_extra = {
            "example": {
                "total_listings": 123,
                "price_mean": 15500.50,
                "price_median": 15000.00,
                "price_std": 2500.00,
                "price_min": 8000.00,
                "price_max": 25000.00,
                "percentile_25": 12500.00,
                "percentile_75": 18000.00,
                "days_on_market_avg": 45.2,
                "regional_distribution": {
                    "bucuresti": 45,
                    "cluj": 23,
                    "timisoara": 18
                }
            }
        }


class PricingStrategy(BaseModel):
    """O strategie de pricing"""
    valoare: float
    timp: str
    probabilitate: int
    descriere: str


class PriceAnalysisResponse(BaseModel):
    """Response complet pentru analiză preț"""
    pret_rapid: PricingStrategy
    pret_optim: PricingStrategy
    pret_negociere: PricingStrategy
    pret_maxim: PricingStrategy
    valoare_dotari: float
    market_data: MarketAnalysisResponse
    timestamp: datetime

    class Config:
        schema_extra = {
            "example": {
                "pret_rapid": {
                    "valoare": 13500,
                    "timp": "1-2 săptămâni",
                    "probabilitate": 95,
                    "descriere": "Vânzare garantată rapid"
                },
                "pret_optim": {
                    "valoare": 15000,
                    "timp": "3-5 săptămâni",
                    "probabilitate": 85,
                    "descriere": "Cel mai bun raport"
                },
                "valoare_dotari": 2500,
                "timestamp": "2024-12-15T10:30:00"
            }
        }


class ScrapeStatusResponse(BaseModel):
    """Status scraping"""
    success: bool
    total_found: int
    sources: dict
    message: str

    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "total_found": 123,
                "sources": {
                    "autovit": 45,
                    "olx": 32,
                    "autoscout24": 28,
                    "mobile_de": 18
                },
                "message": "Scraping completed successfully"
            }
        }


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    database: str
    redis: Optional[str] = None
    timestamp: datetime


class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime