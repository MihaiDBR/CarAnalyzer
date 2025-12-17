"""
Quick Database Population - Popular premium models
"""
import asyncio
from app.scrapers.scraper_service import scraper_service
from app.database import database


async def populate():
    print("\n=== Quick Database Population ===\n")

    await database.connect()

    # Popular premium models (2 pages each for faster testing)
    popular_queries = [
        # BMW
        {'marca': 'BMW', 'model': 'Seria 3'},
        {'marca': 'BMW', 'model': 'Seria 5'},
        {'marca': 'BMW', 'model': 'X3'},

        # Mercedes
        {'marca': 'Mercedes', 'model': 'C-Class'},
        {'marca': 'Mercedes', 'model': 'E-Class'},

        # Audi
        {'marca': 'Audi', 'model': 'A4'},
        {'marca': 'Audi', 'model': 'A6'},

        # VW
        {'marca': 'Volkswagen', 'model': 'Golf'},
        {'marca': 'Volkswagen', 'model': 'Passat'},
    ]

    result = await scraper_service.populate_listings(popular_queries)

    print(f"\n=== FINAL RESULT ===")
    print(f"Total found: {result['total_found']}")
    print(f"Total saved: {result['total_saved']}")
    print(f"Duplicates: {result['duplicates']}")
    print(f"Success: {result['success']}")

    await database.disconnect()


if __name__ == "__main__":
    asyncio.run(populate())
