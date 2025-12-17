"""
Smart Price Analyzer - Auto-scraping when data is missing
Checks DB first, triggers scraping if needed, returns realistic prices
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from app.database import database, listings
from app.scrapers.olx_filtered_scraper import olx_filtered_scraper
from app.scrapers.scraper_service import scraper_service


class SmartPriceAnalyzer:
    """
    Intelligent analyzer that:
    1. Checks DB for recent data (< 24h old)
    2. If insufficient data → triggers scraping with user's filters
    3. Calculates realistic price range from real market data
    """

    MIN_LISTINGS_REQUIRED = 5  # Minimum listings needed for analysis
    DATA_FRESHNESS_HOURS = 24  # Consider data fresh if < 24h old

    async def analyze_with_auto_scraping(
        self,
        marca: str,
        model: str,
        an_min: int,
        an_max: int,
        km_min: Optional[int] = None,
        km_max: Optional[int] = None,
        combustibil: Optional[str] = None,
        transmisie: Optional[str] = None,
        caroserie: Optional[str] = None,
    ) -> Dict:
        """
        Smart analysis with auto-scraping

        Args:
            marca: Brand (BMW, Dacia, etc.)
            model: Model series (Seria 3, Logan, etc.)
            an_min: Min year
            an_max: Max year
            km_min: Min km (optional)
            km_max: Max km (optional)
            combustibil: Fuel type (diesel, benzina, etc.)
            transmisie: Transmission (manuala, automata)
            caroserie: Body type (sedan, hatchback, etc.)

        Returns:
            Dict with price analysis and market data
        """
        print(f"\n=== Smart Price Analysis ===")
        print(f"Car: {marca} {model} ({an_min}-{an_max})")

        # Step 1: Check DB for existing data
        db_listings = await self._get_db_listings(
            marca, model, an_min, an_max, km_min, km_max,
            combustibil, transmisie, caroserie
        )

        print(f"Found {len(db_listings)} listings in DB")

        # Step 2: Check if data is fresh and sufficient
        fresh_listings = self._filter_fresh_listings(db_listings)
        print(f"Fresh listings (< {self.DATA_FRESHNESS_HOURS}h): {len(fresh_listings)}")

        # Step 3: If insufficient data → trigger scraping
        if len(fresh_listings) < self.MIN_LISTINGS_REQUIRED:
            print(f"⚠️ Insufficient data! Triggering scraping...")

            scraping_result = await self._trigger_scraping(
                marca, model, an_min, an_max, km_min, km_max,
                combustibil, transmisie, caroserie
            )

            print(f"✅ Scraping complete: {scraping_result['total_saved']} new listings")

            # Re-fetch DB listings after scraping
            db_listings = await self._get_db_listings(
                marca, model, an_min, an_max, km_min, km_max,
                combustibil, transmisie, caroserie
            )

        # Step 4: Calculate price range from real data
        if len(db_listings) >= self.MIN_LISTINGS_REQUIRED:
            return await self._calculate_price_range(db_listings, marca, model)
        else:
            # Fallback to generic formula if still no data
            return await self._fallback_generic_price(marca, model, an_min, an_max, km_min or 150000)

    async def _get_db_listings(
        self,
        marca: str,
        model: str,
        an_min: int,
        an_max: int,
        km_min: Optional[int],
        km_max: Optional[int],
        combustibil: Optional[str],
        transmisie: Optional[str],
        caroserie: Optional[str],
    ) -> List[Dict]:
        """Query DB for matching listings"""
        query = """
            SELECT *
            FROM listings
            WHERE
                LOWER(marca) = LOWER(:marca)
                AND (LOWER(model_series) = LOWER(:model) OR LOWER(model) LIKE :model_like)
                AND an BETWEEN :an_min AND :an_max
                AND este_activ = true
        """

        params = {
            'marca': marca,
            'model': model,
            'model_like': f'%{model}%',
            'an_min': an_min,
            'an_max': an_max,
        }

        # Add optional filters
        if km_min and km_max:
            query += " AND km BETWEEN :km_min AND :km_max"
            params['km_min'] = km_min
            params['km_max'] = km_max

        if combustibil:
            query += " AND LOWER(combustibil) = LOWER(:combustibil)"
            params['combustibil'] = combustibil

        if transmisie:
            query += " AND LOWER(transmisie) = LOWER(:transmisie)"
            params['transmisie'] = transmisie

        if caroserie:
            query += " AND LOWER(caroserie) = LOWER(:caroserie)"
            params['caroserie'] = caroserie

        query += " ORDER BY pret"

        result = await database.fetch_all(query, params)
        return [dict(row) for row in result]

    def _filter_fresh_listings(self, listings: List[Dict]) -> List[Dict]:
        """Filter listings that are fresh (< 24h old)"""
        cutoff = datetime.now() - timedelta(hours=self.DATA_FRESHNESS_HOURS)
        fresh = []

        for listing in listings:
            scrape_date = listing.get('data_scrape') or listing.get('data_scraping')
            if scrape_date and scrape_date > cutoff:
                fresh.append(listing)

        return fresh

    async def _trigger_scraping(
        self,
        marca: str,
        model: str,
        an_min: int,
        an_max: int,
        km_min: Optional[int],
        km_max: Optional[int],
        combustibil: Optional[str],
        transmisie: Optional[str],
        caroserie: Optional[str],
    ) -> Dict:
        """Trigger OLX scraping with user's filters"""
        print(f"🔍 Scraping OLX for: {marca} {model}")

        # Use filtered scraper with exact user filters
        new_listings = await olx_filtered_scraper.search_cars_filtered(
            marca=marca,
            model=model,
            year_from=an_min,
            year_to=an_max,
            km_from=km_min,
            km_to=km_max,
            fuel_type=combustibil,
            body_type=caroserie,
            transmission=transmisie,
            max_pages=2  # Scrape 2 pages max (fast)
        )

        # Save to database
        saved_count = 0
        for listing in new_listings:
            try:
                # Check duplicates
                existing = await database.fetch_one(
                    listings.select().where(listings.c.url == listing['url'])
                )
                if existing:
                    continue

                # Insert
                await database.execute(listings.insert().values(**listing))
                saved_count += 1
            except Exception as e:
                print(f"Error saving: {e}")
                continue

        return {
            'total_found': len(new_listings),
            'total_saved': saved_count
        }

    async def _calculate_price_range(
        self,
        db_listings: List[Dict],
        marca: str,
        model: str
    ) -> Dict:
        """Calculate realistic price range from DB listings"""
        prices = [l['pret'] for l in db_listings if l.get('pret')]

        if not prices:
            return await self._fallback_generic_price(marca, model, 2015, 2020, 150000)

        prices.sort()

        # Calculate percentiles
        n = len(prices)
        price_min = prices[int(n * 0.10)]  # 10th percentile
        price_p25 = prices[int(n * 0.25)]  # 25th percentile
        price_avg = sum(prices) / n
        price_median = prices[n // 2]
        price_p75 = prices[int(n * 0.75)]  # 75th percentile
        price_max = prices[int(n * 0.90)]  # 90th percentile

        return {
            'pret_rapid': {
                'valoare': round(price_p25, 2),
                'descriere': 'Vânzare rapidă (sub medie)',
                'durata_estimata': '1-2 săptămâni'
            },
            'pret_optim': {
                'valoare': round(price_median, 2),
                'descriere': 'Preț optim (median piață)',
                'durata_estimata': '2-4 săptămâni'
            },
            'pret_negociere': {
                'valoare': round(price_avg, 2),
                'descriere': 'Preț de pornire negociere',
                'durata_estimata': '1-2 luni'
            },
            'pret_maxim': {
                'valoare': round(price_p75, 2),
                'descriere': 'Preț maxim realist',
                'durata_estimata': '2-3 luni'
            },
            'valoare_dotari': 0,  # Calculated separately if needed
            'market_data': {
                'source': 'database_filtered',
                'confidence': min(95, 60 + (len(prices) * 2)),  # More data = higher confidence
                'description': f'Analiză bazată pe {len(prices)} anunțuri reale',
                'sample_size': len(prices),
                'total_listings': len(db_listings),
                'price_mean': round(price_avg, 2),
                'price_median': round(price_median, 2),
                'price_min': round(price_min, 2),
                'price_max': round(price_max, 2),
                'price_p25': round(price_p25, 2),
                'price_p75': round(price_p75, 2),
            }
        }

    async def _fallback_generic_price(
        self,
        marca: str,
        model: str,
        an_min: int,
        an_max: int,
        km: int
    ) -> Dict:
        """Fallback to generic formula if no data available"""
        # Use flexible_analyzer as fallback
        from app.analysis.flexible_price_analyzer import flexible_analyzer

        avg_year = (an_min + an_max) // 2
        result = await flexible_analyzer.calculate_price_with_fallback(
            marca, model, avg_year, km, []
        )

        return result


# Global instance
smart_analyzer = SmartPriceAnalyzer()
