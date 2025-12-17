"""
Test BMW Series Detection and Variants
"""
import asyncio
from app.scrapers.detailed_olx_scraper import detailed_olx_scraper


async def test():
    print("\n=== Testing BMW Seria 3 ===\n")

    listings = await detailed_olx_scraper.search_cars("BMW", "Seria 3", max_pages=1)

    print(f"\nFound {len(listings)} detailed listings\n")

    for i, listing in enumerate(listings[:10], 1):
        print(f"{i}. {listing['marca']} {listing['model_series']} {listing['model_variant'] or ''}")
        print(f"   Year: {listing['an']} | KM: {listing['km']:,} | Price: EUR {listing['pret']:,}")
        if listing['putere_cp']:
            print(f"   Power: {listing['putere_cp']} CP", end='')
        if listing['capacitate_cilindrica']:
            print(f" | Engine: {listing['capacitate_cilindrica']} cm3", end='')
        print()
        print(f"   Trans: {listing['transmisie']} | Drive: {listing['tractiune']} | Body: {listing['caroserie']}")
        print(f"   Fuel: {listing['combustibil']} | Location: {listing['locatie']}")
        print()

    await detailed_olx_scraper.close()


if __name__ == "__main__":
    asyncio.run(test())
