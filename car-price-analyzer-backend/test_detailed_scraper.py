"""
Test Detailed Scraper - Compare Golf 7 base vs GTI
"""
import asyncio
from app.scrapers.detailed_olx_scraper import detailed_olx_scraper


async def test_golf():
    print("\n=== Testing Detailed Scraper: VW Golf 7 ===\n")

    listings = await detailed_olx_scraper.search_cars("Volkswagen", "Golf 7", max_pages=1)

    print(f"\nFound {len(listings)} listings\n")

    # Separate base vs GTI
    base_models = []
    gti_models = []

    for listing in listings:
        if listing['model_variant'] and 'gti' in listing['model_variant'].lower():
            gti_models.append(listing)
        else:
            base_models.append(listing)

    print(f"=== BASE Golf 7 ({len(base_models)} listings) ===\n")
    for i, listing in enumerate(base_models[:3], 1):
        print(f"{i}. {listing['marca']} {listing['model']} {listing['model_variant'] or 'Base'}")
        print(f"   Year: {listing['an']} | KM: {listing['km']:,}")
        print(f"   Price: EUR {listing['pret']:,}")
        print(f"   Power: {listing['putere_cp']} CP | Engine: {listing['capacitate_cilindrica']} cm3")
        print(f"   Transmission: {listing['transmisie']} | Drive: {listing['tractiune']}")
        print(f"   Body: {listing['caroserie']} | Fuel: {listing['combustibil']}")
        print()

    print(f"\n=== GTI Golf 7 ({len(gti_models)} listings) ===\n")
    for i, listing in enumerate(gti_models[:3], 1):
        print(f"{i}. {listing['marca']} {listing['model']} {listing['model_variant']}")
        print(f"   Year: {listing['an']} | KM: {listing['km']:,}")
        print(f"   Price: EUR {listing['pret']:,}")
        print(f"   Power: {listing['putere_cp']} CP | Engine: {listing['capacitate_cilindrica']} cm3")
        print(f"   Transmission: {listing['transmisie']} | Drive: {listing['tractiune']}")
        print(f"   Body: {listing['caroserie']} | Fuel: {listing['combustibil']}")
        print()

    # Calculate price difference
    if base_models and gti_models:
        avg_base = sum(l['pret'] for l in base_models) / len(base_models)
        avg_gti = sum(l['pret'] for l in gti_models) / len(gti_models)
        diff = avg_gti - avg_base
        diff_pct = (diff / avg_base) * 100

        print(f"\n=== PRICE COMPARISON ===")
        print(f"Average Base Golf 7: EUR {avg_base:,.2f}")
        print(f"Average GTI Golf 7: EUR {avg_gti:,.2f}")
        print(f"Difference: EUR {diff:,.2f} ({diff_pct:.1f}% more expensive)")

    await detailed_olx_scraper.close()


if __name__ == "__main__":
    asyncio.run(test_golf())
