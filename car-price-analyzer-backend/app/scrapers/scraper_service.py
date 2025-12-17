"""
Scraper Service - Manages data collection and database population
"""
import asyncio
from datetime import datetime
from typing import List, Dict
from app.database import database, listings
from app.scrapers.detailed_olx_scraper import detailed_olx_scraper


class ScraperService:
    """Service to manage scraping and database updates"""

    def __init__(self):
        self.scraper = detailed_olx_scraper

    async def populate_listings(self, search_queries: List[Dict]) -> Dict:
        """
        Populate database with listings from RSS feeds

        Args:
            search_queries: List of {'marca': 'BMW', 'model': 'Seria 3'}

        Returns:
            Status dict with counts
        """
        print("\n=== Starting RSS Scraping ===\n")

        # Fetch listings from OLX
        new_listings = await self.scraper.bulk_search(search_queries)

        if not new_listings:
            return {
                'success': False,
                'total_found': 0,
                'total_saved': 0,
                'duplicates': 0,
                'message': 'No listings found'
            }

        # Save to database
        saved_count = 0
        duplicate_count = 0

        for listing in new_listings:
            try:
                # Check if listing already exists (by URL)
                existing = await database.fetch_one(
                    listings.select().where(listings.c.url == listing['url'])
                )

                if existing:
                    duplicate_count += 1
                    print(f"Duplicate: {listing['url']}")
                    continue

                # Insert new listing with detailed specs
                await database.execute(listings.insert().values(
                    source=listing['source'],
                    url=listing['url'],
                    marca=listing['marca'],
                    model=listing['model'],
                    model_series=listing.get('model_series'),
                    model_variant=listing.get('model_variant'),
                    an=listing['an'],
                    km=listing['km'],
                    pret=listing['pret'],
                    combustibil=listing['combustibil'],
                    putere_cp=listing.get('putere_cp'),
                    capacitate_cilindrica=listing.get('capacitate_cilindrica'),
                    transmisie=listing.get('transmisie'),
                    tractiune=listing.get('tractiune'),
                    caroserie=listing.get('caroserie'),
                    locatie=listing['locatie'],
                    dotari=listing['dotari'],
                    imagini=listing['imagini'],
                    descriere=listing['descriere'],
                    data_publicare=listing['data_publicare'],
                    zile_pe_piata=listing['zile_pe_piata'],
                    este_activ=listing['este_activ'],
                    data_scrape=datetime.now()
                ))

                saved_count += 1
                print(f"Saved: {listing['marca']} {listing['model']} - EUR {listing['pret']:,}")

            except Exception as e:
                print(f"Error saving listing: {e}")
                continue

        result = {
            'success': True,
            'total_found': len(new_listings),
            'total_saved': saved_count,
            'duplicates': duplicate_count,
            'message': f'Successfully saved {saved_count} new listings ({duplicate_count} duplicates skipped)'
        }

        print(f"\n=== Scraping Complete ===")
        print(f"Total found: {result['total_found']}")
        print(f"Total saved: {result['total_saved']}")
        print(f"Duplicates: {result['duplicates']}\n")

        return result

    async def update_popular_models(self) -> Dict:
        """
        Update database with popular car models
        Searches for most common cars in Romania
        """
        # Most popular cars in Romania (2023-2024 data)
        popular_searches = [
            # German brands
            {'marca': 'BMW', 'model': 'Seria 3'},
            {'marca': 'BMW', 'model': 'Seria 5'},
            {'marca': 'BMW', 'model': 'X3'},
            {'marca': 'BMW', 'model': 'X5'},
            {'marca': 'Mercedes-Benz', 'model': 'C-Class'},
            {'marca': 'Mercedes-Benz', 'model': 'E-Class'},
            {'marca': 'Mercedes-Benz', 'model': 'GLC'},
            {'marca': 'Audi', 'model': 'A4'},
            {'marca': 'Audi', 'model': 'A6'},
            {'marca': 'Audi', 'model': 'Q5'},
            {'marca': 'Volkswagen', 'model': 'Golf'},
            {'marca': 'Volkswagen', 'model': 'Passat'},
            {'marca': 'Volkswagen', 'model': 'Tiguan'},

            # French brands
            {'marca': 'Renault', 'model': 'Clio'},
            {'marca': 'Renault', 'model': 'Megane'},
            {'marca': 'Dacia', 'model': 'Logan'},
            {'marca': 'Dacia', 'model': 'Duster'},
            {'marca': 'Peugeot', 'model': '308'},
            {'marca': 'Peugeot', 'model': '3008'},

            # Japanese brands
            {'marca': 'Toyota', 'model': 'Corolla'},
            {'marca': 'Toyota', 'model': 'RAV4'},
            {'marca': 'Honda', 'model': 'Civic'},
            {'marca': 'Mazda', 'model': '3'},
            {'marca': 'Nissan', 'model': 'Qashqai'},

            # American brands
            {'marca': 'Ford', 'model': 'Focus'},
            {'marca': 'Ford', 'model': 'Fiesta'},

            # Korean brands
            {'marca': 'Hyundai', 'model': 'i30'},
            {'marca': 'Kia', 'model': 'Sportage'},

            # Italian brands
            {'marca': 'Fiat', 'model': '500'},

            # Czech brands
            {'marca': 'Skoda', 'model': 'Octavia'},
            {'marca': 'Skoda', 'model': 'Fabia'}
        ]

        return await self.populate_listings(popular_searches)

    async def update_specific_model(self, marca: str, model: str = None) -> Dict:
        """
        Update database for a specific car model

        Args:
            marca: Car brand
            model: Car model (optional)

        Returns:
            Status dict
        """
        search_queries = [{'marca': marca, 'model': model}]
        return await self.populate_listings(search_queries)

    async def cleanup_inactive_listings(self, max_age_days: int = 60) -> int:
        """
        Mark listings as inactive if they're too old
        (likely sold or removed from OLX)

        Args:
            max_age_days: Maximum age before marking inactive

        Returns:
            Number of listings marked inactive
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        # Update old listings
        query = listings.update().where(
            (listings.c.data_publicare < cutoff_date) &
            (listings.c.este_activ == True)
        ).values(este_activ=False)

        result = await database.execute(query)

        print(f"Marked {result} listings as inactive (older than {max_age_days} days)")
        return result


# Global instance
scraper_service = ScraperService()
