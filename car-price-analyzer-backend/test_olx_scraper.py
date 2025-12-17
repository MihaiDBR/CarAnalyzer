"""
Test OLX HTML Scraper
"""
import asyncio
from app.scrapers.olx_scraper import olx_scraper


async def test():
    print("\n=== Testing OLX HTML Scraper ===\n")
    print("Searching for: BMW Seria 3")
    print("This will take ~10 seconds due to rate limiting\n")

    try:
        listings = await olx_scraper.search_cars("BMW", "Seria 3", max_pages=1)

        print(f"\nFound {len(listings)} listings\n")

        if listings:
            print("First 5 results:\n")
            for i, listing in enumerate(listings[:5], 1):
                print(f"{i}. {listing['marca']} {listing['model']}")
                if listing['an']:
                    print(f"   Year: {listing['an']}")
                print(f"   Price: EUR {listing['pret']:,}")
                if listing['km']:
                    print(f"   KM: {listing['km']:,}")
                print(f"   Location: {listing['locatie']}")
                print(f"   Fuel: {listing['combustibil']}")
                print(f"   URL: {listing['url']}")
                print()
        else:
            print("No listings found.")
            print("This might be due to:")
            print("  1. OLX changed their HTML structure")
            print("  2. No listings available for this search")
            print("  3. OLX blocking scraper access")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        await olx_scraper.close()


if __name__ == "__main__":
    asyncio.run(test())
