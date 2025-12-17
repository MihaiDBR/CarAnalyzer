# ============================================
# BACKEND - app/routers/scraping.py
# Router pentru operații de scraping
# ============================================

from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from typing import List, Optional

from app.schemas import ScrapeRequest, ScrapeStatusResponse
from app.scrapers.scraper_service import scraper_service
from app.database import database, listings

router = APIRouter()

# Cache pentru status-ul scraping-ului
scraping_status = {}

async def scrape_task(marca: str, model: Optional[str], task_id: str):
    """Task de scraping care rulează în background"""
    try:
        scraping_status[task_id] = {
            "status": "running",
            "progress": 0,
            "sources": {}
        }

        # Use scraper service
        result = await scraper_service.update_specific_model(marca, model)

        # Update status
        scraping_status[task_id]["progress"] = 100
        scraping_status[task_id]["status"] = "completed"
        scraping_status[task_id]["total_found"] = result['total_found']
        scraping_status[task_id]["total_saved"] = result['total_saved']
        scraping_status[task_id]["sources"] = {'olx': result['total_saved']}
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
    Uses OLX RSS feeds (100% legal)

    Returns:
        - task_id: ID pentru tracking
        - status: status initial
    """
    # Generează task ID
    task_id = f"{request.marca}_{request.model}_{datetime.now().timestamp()}"

    # Pornește task în background
    background_tasks.add_task(scrape_task, request.marca, request.model, task_id)

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
    Uses OLX RSS feeds - 100% legal
    """
    try:
        result = await scraper_service.update_specific_model(
            marca=request.marca,
            model=request.model
        )

        return ScrapeStatusResponse(
            success=result['success'],
            total_found=result['total_found'],
            sources={'olx': result['total_saved']},
            message=result['message']
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape/popular")
async def scrape_popular_models(background_tasks: BackgroundTasks):
    """
    Scrape popular car models in Romania
    Uses OLX RSS feeds (100% legal)
    Runs in background to avoid timeout
    """
    try:
        # Run in background for large scraping operations
        task_id = f"popular_{datetime.now().timestamp()}"

        scraping_status[task_id] = {
            "status": "running",
            "progress": 0,
            "message": "Scraping popular models..."
        }

        async def popular_task():
            try:
                result = await scraper_service.update_popular_models()
                scraping_status[task_id]["status"] = "completed"
                scraping_status[task_id]["progress"] = 100
                scraping_status[task_id]["result"] = result
            except Exception as e:
                scraping_status[task_id]["status"] = "failed"
                scraping_status[task_id]["error"] = str(e)

        background_tasks.add_task(popular_task)

        return {
            'success': True,
            'task_id': task_id,
            'message': 'Scraping popular models in background. Check status with /scrape/status/{task_id}'
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare scraping: {str(e)}")


@router.get("/scrape/stats")
async def get_scraping_stats():
    """
    Get current database statistics
    """
    try:
        # Total listings
        total_query = "SELECT COUNT(*) as count FROM listings"
        total_result = await database.fetch_one(total_query)
        total_listings = total_result['count'] if total_result else 0

        # Active listings
        active_query = "SELECT COUNT(*) as count FROM listings WHERE este_activ = true"
        active_result = await database.fetch_one(active_query)
        active_listings = active_result['count'] if active_result else 0

        # Listings by source
        source_query = "SELECT source, COUNT(*) as count FROM listings GROUP BY source"
        source_results = await database.fetch_all(source_query)
        sources = {row['source']: row['count'] for row in source_results}

        # Recent listings (last 7 days)
        from datetime import timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_query = "SELECT COUNT(*) as count FROM listings WHERE data_scrape >= :week_ago"
        recent_result = await database.fetch_one(recent_query, {'week_ago': week_ago})
        recent_listings = recent_result['count'] if recent_result else 0

        # Top brands
        brands_query = """
            SELECT marca, COUNT(*) as count
            FROM listings
            WHERE este_activ = true
            GROUP BY marca
            ORDER BY count DESC
            LIMIT 10
        """
        brands_results = await database.fetch_all(brands_query)
        top_brands = {row['marca']: row['count'] for row in brands_results}

        return {
            'total_listings': total_listings,
            'active_listings': active_listings,
            'recent_listings_7d': recent_listings,
            'sources': sources,
            'top_brands': top_brands,
            'last_updated': datetime.now().isoformat()
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare status: {str(e)}")