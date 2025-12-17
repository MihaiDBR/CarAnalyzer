"""
Test OLX Filtered Scraper - Using native OLX filters
"""
import asyncio
from app.scrapers.olx_filtered_scraper import olx_filtered_scraper


async def test():
    print("\n=== Testing OLX Filtered Scraper ===\n")
    print("Using exact filters from your URL:")
    print("- BMW Seria 3")
    print("- Year: 2012-2015")
    print("- KM: 120,000-300,000")
    print("- Engine: 1998-2230 cm3")
    print("- Fuel: Diesel")
    print("- Body: Sedan")
    print("- Transmission: Automatic")
    print("- Price: 10,000-30,000 EUR\n")

    listings = await olx_filtered_scraper.search_cars_filtered(
        marca="BMW",
        model="Seria 3",
        year_from=2012,
        year_to=2015,
        km_from=120000,
        km_to=300000,
        fuel_type="diesel",
        body_type="sedan",
        transmission="automata",
        price_from=10000,
        price_to=30000,
        max_pages=2
    )

    print(f"\n=== RESULTS ===")
    print(f"Found {len(listings)} listings\n")

    for i, listing in enumerate(listings, 1):
        print(f"{i}. {listing['marca']} {listing['model']}")
        print(f"   Year: {listing['an']} | KM: {listing['km']:,} | Price: EUR {listing['pret']:,}")
        print(f"   Fuel: {listing['combustibil']} | Trans: {listing['transmisie']} | Body: {listing['caroserie']}")
        print(f"   Location: {listing['locatie']}")
        print(f"   URL: {listing['url']}")
        print()

    if listings:
        avg_price = sum(l['pret'] for l in listings) / len(listings)
        min_price = min(l['pret'] for l in listings)
        max_price = max(l['pret'] for l in listings)

        print(f"\n=== PRICE ANALYSIS ===")
        print(f"Average: EUR {avg_price:,.2f}")
        print(f"Range: EUR {min_price:,.2f} - EUR {max_price:,.2f}")

    await olx_filtered_scraper.close()


if __name__ == "__main__":
    asyncio.run(test())
