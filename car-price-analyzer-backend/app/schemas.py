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
    """Request pentru analiză mașină - EXTENDED cu filtre OLX"""
    marca: str = Field(..., min_length=2, max_length=50, description="Marca mașinii")
    model: str = Field(..., min_length=1, max_length=100, description="Modelul mașinii")
    an: int = Field(..., ge=1990, le=2025, description="Anul fabricației")
    km: int = Field(..., ge=0, le=1000000, description="Kilometri parcurși")
    combustibil: str = Field(..., description="Tipul de combustibil")

    # NEW FIELDS for smart filtering
    transmisie: Optional[str] = Field(default=None, description="Transmisie: manuala/automata")
    tractiune: Optional[str] = Field(default=None, description="Tracțiune: fata/spate/4x4")
    caroserie: Optional[str] = Field(default=None, description="Caroserie: sedan/hatchback/break/suv/coupe")

    @validator('combustibil')
    def validate_combustibil(cls, v):
        allowed = ['benzina', 'diesel', 'electric', 'hybrid', 'gpl']
        if v.lower() not in allowed:
            raise ValueError(f'Combustibil trebuie să fie unul din: {", ".join(allowed)}')
        return v.lower()

    @validator('transmisie')
    def validate_transmisie(cls, v):
        if v is None or v == '':
            return None
        allowed = ['manuala', 'automata']
        if v.lower() not in allowed:
            raise ValueError(f'Transmisie trebuie să fie: manuala sau automata')
        return v.lower()

    @validator('tractiune')
    def validate_tractiune(cls, v):
        if v is None or v == '':
            return None
        allowed = ['fata', 'spate', '4x4']
        if v.lower() not in allowed:
            raise ValueError(f'Tracțiune trebuie să fie: fata, spate sau 4x4')
        return v.lower()

    @validator('caroserie')
    def validate_caroserie(cls, v):
        if v is None or v == '':
            return None
        allowed = ['sedan', 'hatchback', 'break', 'coupe', 'suv', 'cabrio']
        if v.lower() not in allowed:
            raise ValueError(f'Caroserie trebuie să fie unul din: {", ".join(allowed)}')
        return v.lower()

    @validator('marca', 'model')
    def validate_text(cls, v):
        if not v or v.strip() == '':
            raise ValueError('Câmpul nu poate fi gol')
        return v.strip().title()

    class Config:
        schema_extra = {
            "example": {
                "marca": "BMW",
                "model": "Seria 3",
                "an": 2013,
                "km": 200000,
                "combustibil": "diesel",
                "transmisie": "automata",
                "tractiune": "fata",
                "caroserie": "sedan"
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
    """Response pentru analiză piață - FLEXIBIL pentru noul sistem"""
    # Required fields (always present)
    source: str  # 'database_exact', 'database_similar', 'generic_formula'
    confidence: int  # 60-95%
    description: str  # Human-readable description
    sample_size: int  # Number of listings used (0 for generic)

    # Optional fields (only when database data available)
    total_listings: Optional[int] = 0
    price_mean: Optional[float] = 0.0
    price_median: Optional[float] = 0.0
    price_std: Optional[float] = 0.0
    price_min: Optional[float] = 0.0
    price_max: Optional[float] = 0.0
    percentile_25: Optional[float] = 0.0
    percentile_75: Optional[float] = 0.0
    days_on_market_avg: Optional[float] = 0.0
    regional_distribution: Optional[dict] = {}

    class Config:
        schema_extra = {
            "example": {
                "source": "generic_formula",
                "confidence": 60,
                "description": "Calcul bazat pe formula standard de depreciere",
                "sample_size": 0,
                "total_listings": 0,
                "price_mean": 0.0
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