from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

from app.database import database
from app.routers import scraping, analysis, listings

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    print("✓ Database connected")
    yield
    await database.disconnect()
    print("✓ Database disconnected")

app = FastAPI(
    title="Car Price Analyzer API",
    description="API pentru analiză prețuri mașini",
    version="1.0.0",
    lifespan=lifespan
)

origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# IMPORTANT - Acestea 3 linii!!!
app.include_router(scraping.router, prefix="/api", tags=["Scraping"])
app.include_router(analysis.router, prefix="/api", tags=["Analysis"])
app.include_router(listings.router, prefix="/api", tags=["Listings"])

@app.get("/")
async def root():
    return {
        "message": "Car Price Analyzer API",
        "status": "online",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    try:
        await database.fetch_one("SELECT 1")
        return {
            "status": "healthy",
            "database": "connected"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )