"""
Test RSS Scraper - Verify OLX scraping works
"""
import asyncio
from app.scrapers.olx_rss_scraper import olx_scraper
from app.scrapers.scraper_service import scraper_service
from app.database import database


async def test_single_search():
    """Test single car search"""
    print("\n=== Testing Single Car Search ===\n")

    await database.connect()

    # Test with BMW Seria 3
    print("Searching OLX for: BMW Seria 3")
    listings = await olx_scraper.search_cars("BMW", "Seria 3")

    print(f"\nFound {len(listings)} listings:\n")

    for i, listing in enumerate(listings[:5], 1):  # Show first 5
        print(f"{i}. {listing['marca']} {listing['model']} ({listing['an']})")
        print(f"   Price: EUR {listing['pret']:,}")
        print(f"   KM: {listing['km']:,}")
        print(f"   Location: {listing['locatie']}")
        print(f"   Fuel: {listing['combustibil']}")
        print(f"   URL: {listing['url']}")
        print(f"   Days on market: {listing['zile_pe_piata']}")
        print()

    await database.disconnect()


async def test_database_population():
    """Test populating database"""
    print("\n=== Testing Database Population ===\n")

    await database.connect()

    # Test with a few car models
    result = await scraper_service.update_specific_model("BMW", "Seria 3")

    print(f"\n[RESULT]")
    print(f"  Success: {result['success']}")
    print(f"  Total found: {result['total_found']}")
    print(f"  Total saved: {result['total_saved']}")
    print(f"  Duplicates: {result['duplicates']}")
    print(f"  Message: {result['message']}")

    await database.disconnect()


async def test_popular_models():
    """Test scraping popular models"""
    print("\n=== Testing Popular Models Scraping ===\n")
    print("WARNING: This will take several minutes due to rate limiting!")
    print("Press Ctrl+C to cancel\n")

    await asyncio.sleep(3)

    await database.connect()

    result = await scraper_service.update_popular_models()

    print(f"\n[RESULT]")
    print(f"  Success: {result['success']}")
    print(f"  Total found: {result['total_found']}")
    print(f"  Total saved: {result['total_saved']}")
    print(f"  Duplicates: {result['duplicates']}")

    await database.disconnect()


async def main():
    """Main test runner"""
    print("\n" + "="*60)
    print("  RSS Scraper Test Suite")
    print("="*60)

    tests = {
        '1': ('Single Search (BMW Seria 3)', test_single_search),
        '2': ('Database Population (BMW Seria 3)', test_database_population),
        '3': ('Popular Models (30+ models, takes 5-10 min)', test_popular_models)
    }

    print("\nAvailable tests:")
    for key, (name, _) in tests.items():
        print(f"  {key}. {name}")

    choice = input("\nSelect test (1-3): ").strip()

    if choice in tests:
        name, test_func = tests[choice]
        print(f"\nRunning: {name}\n")
        await test_func()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
