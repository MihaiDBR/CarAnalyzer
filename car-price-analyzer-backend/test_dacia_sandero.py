"""
Test Dacia Sandero 2019, 200000 km, Diesel, Manual
Shows exact search parameters and expected results
"""
import asyncio
from app.scrapers.olx_filtered_scraper import olx_filtered_scraper


async def test():
    print("\n" + "="*60)
    print("TEST: Dacia Sandero 2019, 200,000 km, Diesel, Manual")
    print("="*60)

    # Calculate SMART ranges (same logic as backend)
    an = 2019
    km = 200000

    # Year range: 2019 >= 2015, so ±1 year
    year_range = 1
    an_min = an - year_range  # 2018
    an_max = an + year_range  # 2020

    # KM range: 200k > 150k, so ±20k
    km_range = 20000
    km_min = km - km_range  # 180,000
    km_max = km + km_range  # 220,000

    print(f"\n📊 SEARCH PARAMETERS:")
    print(f"   User input: Year {an}, KM {km:,}")
    print(f"   Search range: Year {an_min}-{an_max}, KM {km_min:,}-{km_max:,}")
    print(f"   Filters: Diesel, Manual")
    print(f"\n🔍 OLX URL will be:")
    print(f"   https://www.olx.ro/autoturisme/dacia/?")
    print(f"   - model: sandero")
    print(f"   - year: {an_min}-{an_max}")
    print(f"   - km: {km_min:,}-{km_max:,}")
    print(f"   - fuel: diesel")
    print(f"   - transmission: manual")

    print(f"\n⏳ Scraping OLX... (this may take 10-30 seconds)")
    print("-" * 60)

    listings = await olx_filtered_scraper.search_cars_filtered(
        marca="Dacia",
        model="Sandero",
        year_from=an_min,
        year_to=an_max,
        km_from=km_min,
        km_to=km_max,
        fuel_type="diesel",
        transmission="manuala",
        max_pages=2
    )

    print("\n" + "="*60)
    print(f"📈 RESULTS: Found {len(listings)} listings")
    print("="*60)

    if listings:
        # Sort by price
        listings_sorted = sorted(listings, key=lambda x: x['pret'])

        print("\n📋 ALL LISTINGS (sorted by price):")
        print("-" * 60)
        for i, listing in enumerate(listings_sorted, 1):
            print(f"{i:2}. EUR {listing['pret']:>8,.0f} | {listing['an']} | {listing['km']:>7,} km | {listing['locatie']}")

        # Calculate statistics
        prices = [l['pret'] for l in listings]
        prices.sort()
        n = len(prices)

        price_min = prices[0]
        price_p25 = prices[int(n * 0.25)]
        price_median = prices[n // 2]
        price_avg = sum(prices) / n
        price_p75 = prices[int(n * 0.75)]
        price_max = prices[-1]

        print("\n" + "="*60)
        print("💰 PRICE STATISTICS:")
        print("="*60)
        print(f"   Total listings: {n}")
        print(f"   Minimum:        EUR {price_min:>8,.0f}")
        print(f"   25th percentile: EUR {price_p25:>8,.0f}  (Preț Rapid)")
        print(f"   Median:         EUR {price_median:>8,.0f}  (Preț Optim)")
        print(f"   Average:        EUR {price_avg:>8,.0f}  (Preț Negociere)")
        print(f"   75th percentile: EUR {price_p75:>8,.0f}  (Preț Maxim)")
        print(f"   Maximum:        EUR {price_max:>8,.0f}")
        print(f"\n   Price range:    EUR {price_min:,.0f} - EUR {price_max:,.0f}")
        print(f"   Std deviation:  EUR {(sum((p - price_avg)**2 for p in prices) / n)**0.5:,.0f}")

        print("\n" + "="*60)
        print("✅ FINAL PRICES USER WILL SEE:")
        print("="*60)
        print(f"   🔴 Vânzare Rapidă:     EUR {price_p25:>8,.0f}")
        print(f"   🟢 Preț Optim:         EUR {price_median:>8,.0f}")
        print(f"   🔵 Cu Negociere:       EUR {price_avg:>8,.0f}")
        print(f"   🟣 Preț Premium:       EUR {price_p75:>8,.0f}")

        # Year distribution
        years = {}
        for l in listings:
            year = l['an']
            if year not in years:
                years[year] = []
            years[year].append(l['pret'])

        print("\n" + "="*60)
        print("📅 DISTRIBUTION BY YEAR:")
        print("="*60)
        for year in sorted(years.keys()):
            count = len(years[year])
            avg_price = sum(years[year]) / count
            print(f"   {year}: {count:2} listings | Avg: EUR {avg_price:>8,.0f}")

        # Location distribution
        locations = {}
        for l in listings:
            loc = l['locatie']
            if loc not in locations:
                locations[loc] = []
            locations[loc].append(l['pret'])

        print("\n" + "="*60)
        print("📍 DISTRIBUTION BY LOCATION:")
        print("="*60)
        for loc in sorted(locations.keys(), key=lambda x: -len(locations[x]))[:10]:
            count = len(locations[loc])
            avg_price = sum(locations[loc]) / count
            print(f"   {loc:20}: {count:2} listings | Avg: EUR {avg_price:>8,.0f}")

    else:
        print("\n❌ NO LISTINGS FOUND!")
        print("\nPossible reasons:")
        print("1. No Dacia Sandero Diesel Manual in this year/km range on OLX")
        print("2. Search parameters too narrow")
        print("3. OLX structure changed (scraper needs update)")

    await olx_filtered_scraper.close()


if __name__ == "__main__":
    asyncio.run(test())
