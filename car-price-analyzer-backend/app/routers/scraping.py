# ============================================
# BACKEND - app/routers/scraping.py
# Router pentru operații de scraping
# ============================================

from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from typing import List

from app.schemas import ScrapeRequest, ScrapeStatusResponse
from app.scrapers.autovit import AutovitScraper
from app.scrapers.olx import OLXScraper
from app.database import database, listings

router = APIRouter()

# Cache pentru status-ul scraping-ului
scraping_status = {}

async def scrape_task(request: ScrapeRequest, task_id: str):
    """Task de scraping care rulează în background"""
    try:
        scraping_status[task_id] = {
            "status": "running",
            "progress": 0,
            "sources": {}
        }
        
        results = {
            "autovit": [],
            "olx": []
        }
        
        # Scraping Autovit
        scraping_status[task_id]["progress"] = 25
        autovit_scraper = AutovitScraper()
        try:
            autovit_listings = await autovit_scraper.search_cars(
                request.marca, 
                request.model,
                request.an_min,
                request.an_max
            )
            results["autovit"] = autovit_listings
            scraping_status[task_id]["sources"]["autovit"] = len(autovit_listings)
        except Exception as e:
            print(f"Eroare Autovit: {e}")
            scraping_status[task_id]["sources"]["autovit"] = 0
        finally:
            autovit_scraper.close()
        
        # Scraping OLX
        scraping_status[task_id]["progress"] = 50
        olx_scraper = OLXScraper()
        try:
            olx_listings = await olx_scraper.search_cars(
                request.marca,
                request.model
            )
            results["olx"] = olx_listings
            scraping_status[task_id]["sources"]["olx"] = len(olx_listings)
        except Exception as e:
            print(f"Eroare OLX: {e}")
            scraping_status[task_id]["sources"]["olx"] = 0
        
        # Salvare în baza de date
        scraping_status[task_id]["progress"] = 75
        all_listings = results["autovit"] + results["olx"]
        saved_count = 0
        
        for listing in all_listings:
            try:
                query = listings.insert().values(
                    source=listing.source,
                    url=listing.url,
                    marca=listing.marca,
                    model=listing.model,
                    an=listing.an,
                    km=listing.km,
                    pret=listing.price,
                    combustibil=listing.combustibil,
                    locatie=listing.locatie,
                    dotari=listing.dotari,
                    imagini=listing.imagini,
                    descriere=listing.descriere,
                    telefon=listing.telefon,
                    data_publicare=listing.data_publicare,
                    data_scraping=datetime.now(),
                    este_activ=True
                )
                await database.execute(query)
                saved_count += 1
            except Exception as e:
                # Skip duplicates
                continue
        
        # Finalizare
        scraping_status[task_id]["progress"] = 100
        scraping_status[task_id]["status"] = "completed"
        scraping_status[task_id]["total_saved"] = saved_count
        scraping_status[task_id]["completed_at"] = datetime.now().isoformat()
        
    except Exception as e:
        scraping_status[task_id]["status"] = "failed"
        scraping_status[task_id]["error"] = str(e)

@router.post("/scrape", response_model=ScrapeStatusResponse)
async def start_scraping(
    request: ScrapeRequest,
    background_tasks: BackgroundTasks
):
    """
    Pornește procesul de scraping pentru o mașină
    
    Returns:
        - task_id: ID pentru tracking
        - status: status initial
    """
    # Generează task ID
    task_id = f"{request.marca}_{request.model}_{datetime.now().timestamp()}"
    
    # Pornește task în background
    background_tasks.add_task(scrape_task, request, task_id)
    
    return ScrapeStatusResponse(
        success=True,
        total_found=0,
        sources={},
        message=f"Scraping started. Track progress with task_id: {task_id}"
    )

@router.get("/scrape/status/{task_id}")
async def get_scraping_status(task_id: str):
    """
    Obține status-ul unui task de scraping
    """
    if task_id not in scraping_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return scraping_status[task_id]

@router.post("/scrape/sync", response_model=ScrapeStatusResponse)
async def scrape_synchronous(request: ScrapeRequest):
    """
    Scraping sincron (așteaptă să se termine)
    Folosește doar pentru testing sau anunțuri puține
    """
    try:
        results = {
            "autovit": [],
            "olx": []
        }
        
        # Autovit
        autovit_scraper = AutovitScraper()
        try:
            autovit_listings = await autovit_scraper.search_cars(
                request.marca,
                request.model,
                request.an_min,
                request.an_max
            )
            results["autovit"] = autovit_listings
        finally:
            autovit_scraper.close()
        
        # OLX
        olx_scraper = OLXScraper()
        try:
            olx_listings = await olx_scraper.search_cars(
                request.marca,
                request.model
            )
            results["olx"] = olx_listings
        except:
            pass
        
        # Salvare
        all_listings = results["autovit"] + results["olx"]
        saved_count = 0
        
        for listing in all_listings:
            try:
                query = listings.insert().values(
                    source=listing.source,
                    url=listing.url,
                    marca=listing.marca,
                    model=listing.model,
                    an=listing.an,
                    km=listing.km,
                    pret=listing.price,
                    combustibil=listing.combustibil,
                    locatie=listing.locatie,
                    dotari=listing.dotari,
                    imagini=listing.imagini,
                    descriere=listing.descriere,
                    data_publicare=listing.data_publicare,
                    data_scraping=datetime.now(),
                    este_activ=True
                )
                await database.execute(query)
                saved_count += 1
            except:
                continue
        
        return ScrapeStatusResponse(
            success=True,
            total_found=len(all_listings),
            sources={
                "autovit": len(results["autovit"]),
                "olx": len(results["olx"])
            },
            message=f"Successfully scraped and saved {saved_count} listings"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))