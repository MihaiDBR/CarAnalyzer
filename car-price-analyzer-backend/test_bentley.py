"""
Test Bentley Bentayga scraping
"""
import asyncio
from app.scrapers.olx_scraper import olx_scraper


async def test():
    print("\n=== Testing Bentley Bentayga ===\n")

    try:
        listings = await olx_scraper.search_cars("Bentley", "Bentayga", max_pages=1)

        print(f"\nFound {len(listings)} listings\n")

        for i, listing in enumerate(listings, 1):
            print(f"{i}. {listing['marca']} {listing['model']}")
            if listing['an']:
                print(f"   Year: {listing['an']}")
            print(f"   Price: EUR {listing['pret']:,}")
            if listing['km']:
                print(f"   KM: {listing['km']:,}")
            print(f"   Location: {listing['locatie']}")
            print(f"   URL: {listing['url']}")
            print()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await olx_scraper.close()


if __name__ == "__main__":
    asyncio.run(test())
