# ============================================
# BACKEND - app/routers/listings.py
# Router pentru gestionarea anunțurilor
# ============================================

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from datetime import datetime, timedelta

from app.schemas import ListingResponse
from app.database import database, listings

router = APIRouter()

@router.get("/listings/{marca}/{model}", response_model=List[ListingResponse])
async def get_listings(
    marca: str,
    model: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    an_min: Optional[int] = None,
    an_max: Optional[int] = None,
    pret_min: Optional[float] = None,
    pret_max: Optional[float] = None,
    locatie: Optional[str] = None,
    sort_by: str = Query("data_scraping", regex="^(pret|an|km|data_scraping)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """
    Obține anunțuri pentru o marcă și model
    
    Query params:
        - limit: număr maxim de rezultate (1-200)
        - offset: pentru paginare
        - an_min, an_max: filtrare după an
        - pret_min, pret_max: filtrare după preț
        - locatie: filtrare după locație
        - sort_by: sortare după (pret|an|km|data_scraping)
        - sort_order: ordine (asc|desc)
    """
    try:
        # Construiește query
        query = listings.select().where(
            (listings.c.marca == marca) &
            (listings.c.model == model) &
            (listings.c.este_activ == True)
        )
        
        # Filtre opționale
        if an_min:
            query = query.where(listings.c.an >= an_min)
        if an_max:
            query = query.where(listings.c.an <= an_max)
        if pret_min:
            query = query.where(listings.c.pret >= pret_min)
        if pret_max:
            query = query.where(listings.c.pret <= pret_max)
        if locatie:
            query = query.where(listings.c.locatie.ilike(f"%{locatie}%"))
        
        # Sortare
        sort_column = getattr(listings.c, sort_by)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Paginare
        query = query.limit(limit).offset(offset)
        
        # Execută query
        results = await database.fetch_all(query)
        
        # Calculează zile pe piață
        now = datetime.now()
        listings_with_days = []
        for r in results:
            listing_dict = dict(r)
            if listing_dict['data_publicare']:
                days_diff = (now - listing_dict['data_publicare']).days
                listing_dict['zile_pe_piata'] = days_diff
            listings_with_days.append(listing_dict)
        
        return listings_with_days
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/listings/detail/{listing_id}", response_model=ListingResponse)
async def get_listing_detail(listing_id: int):
    """
    Obține detalii complete despre un anunț specific
    """
    query = listings.select().where(listings.c.id == listing_id)
    result = await database.fetch_one(query)
    
    if not result:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    listing_dict = dict(result)
    
    # Calculează zile pe piață
    if listing_dict['data_publicare']:
        days_diff = (datetime.now() - listing_dict['data_publicare']).days
        listing_dict['zile_pe_piata'] = days_diff
    
    # Incrementează vizualizări
    update_query = listings.update().where(
        listings.c.id == listing_id
    ).values(
        vizualizari=listings.c.vizualizari + 1
    )
    await database.execute(update_query)
    
    return listing_dict

@router.get("/listings/recent")
async def get_recent_listings(
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(7, ge=1, le=30)
):
    """
    Obține anunțurile adăugate în ultimele X zile
    """
    cutoff_date = datetime.now() - timedelta(days=days)
    
    query = listings.select().where(
        (listings.c.data_scraping >= cutoff_date) &
        (listings.c.este_activ == True)
    ).order_by(
        listings.c.data_scraping.desc()
    ).limit(limit)
    
    results = await database.fetch_all(query)
    return [dict(r) for r in results]

@router.get("/listings/popular")
async def get_popular_listings(
    limit: int = Query(20, ge=1, le=100)
):
    """
    Obține anunțurile cele mai vizualizate
    """
    query = listings.select().where(
        listings.c.este_activ == True
    ).order_by(
        listings.c.vizualizari.desc()
    ).limit(limit)
    
    results = await database.fetch_all(query)
    return [dict(r) for r in results]

@router.get("/brands")
async def get_available_brands():
    """
    Obține lista de mărci disponibile în baza de date
    """
    query = """
        SELECT DISTINCT marca, COUNT(*) as count
        FROM listings
        WHERE este_activ = true
        GROUP BY marca
        ORDER BY count DESC
    """
    
    results = await database.fetch_all(query)
    return [{"marca": r['marca'], "count": r['count']} for r in results]

@router.get("/models/{marca}")
async def get_models_for_brand(marca: str):
    """
    Obține lista de modele pentru o marcă
    """
    query = """
        SELECT DISTINCT model, COUNT(*) as count
        FROM listings
        WHERE marca = :marca AND este_activ = true
        GROUP BY model
        ORDER BY count DESC
    """
    
    results = await database.fetch_all(query, values={"marca": marca})
    return [{"model": r['model'], "count": r['count']} for r in results]

@router.get("/equipment")
async def get_available_equipment():
    """
    Obține lista de dotări disponibile
    """
    from app.database import dotari
    
    query = dotari.select().order_by(dotari.c.valoare_medie.desc())
    results = await database.fetch_all(query)
    
    return [dict(r) for r in results]

@router.delete("/listings/{listing_id}")
async def deactivate_listing(listing_id: int):
    """
    Dezactivează un anunț (soft delete)
    """
    query = listings.update().where(
        listings.c.id == listing_id
    ).values(
        este_activ=False
    )
    
    await database.execute(query)
    
    return {
        "success": True,
        "message": f"Listing {listing_id} deactivated"
    }

@router.get("/listings/stats/summary")
async def get_listings_summary():
    """
    Obține statistici generale despre anunțuri
    """
    query = """
        SELECT 
            COUNT(*) as total_active,
            AVG(pret) as avg_price,
            MIN(pret) as min_price,
            MAX(pret) as max_price,
            COUNT(DISTINCT marca) as total_brands,
            COUNT(DISTINCT model) as total_models,
            COUNT(DISTINCT source) as total_sources
        FROM listings
        WHERE este_activ = true
    """
    
    result = await database.fetch_one(query)
    
    return dict(result)