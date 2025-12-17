"""
Simple RSS Test - Quick verification
"""
import asyncio
from app.scrapers.olx_rss_scraper import olx_scraper


async def test():
    print("\n=== Quick RSS Test ===\n")
    print("Searching OLX RSS for: BMW Seria 3\n")

    listings = await olx_scraper.search_cars("BMW", "Seria 3")

    print(f"Found {len(listings)} listings\n")

    if listings:
        print("First 3 results:\n")
        for i, listing in enumerate(listings[:3], 1):
            print(f"{i}. {listing['marca']} {listing['model']} - {listing['an']}")
            print(f"   EUR {listing['pret']:,} | {listing['km']:,} km")
            print(f"   {listing['locatie']} | {listing['combustibil']}")
            print(f"   {listing['url']}\n")
    else:
        print("No listings found. Check RSS feed availability.")


if __name__ == "__main__":
    asyncio.run(test())
