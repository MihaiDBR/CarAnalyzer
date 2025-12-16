"""
Test filtered makes - only major manufacturers
"""
import asyncio
from app.services.vehicle_data_service import vehicle_data_service
from app.database import database
from app.integrations.carquery import carquery_client
from app.integrations.nhtsa import nhtsa_client

async def test_filtered():
    print("\n=== Testing Filtered Makes (Only Major Manufacturers) ===\n")

    try:
        await database.connect()

        # Clear cache to force fresh fetch
        print("Fetching makes with filter...")
        makes = await vehicle_data_service.get_makes(force_refresh=True)

        print(f"\n[OK] Fetched {len(makes)} MAJOR manufacturers (filtered from 12,000+)")
        print("\nMajor manufacturers list:")
        for i, make in enumerate(makes, 1):
            print(f"  {i}. {make['display']}")

        # Test BMW models
        print("\n--- Testing BMW 3-Series Models ---")
        bmw_models = await vehicle_data_service.get_models_for_make("BMW")
        print(f"[OK] Found {len(bmw_models)} BMW models")

        # Filter for 340i or similar
        matching_models = [m for m in bmw_models if '340' in m['model'].lower() or '3 series' in m['model'].lower()]
        if matching_models:
            print(f"\nModels matching '340' or '3 Series':")
            for model in matching_models[:10]:
                print(f"  - {model['model']}")

        # Test with specific year
        print("\n--- Testing BMW Models for 2018 ---")
        bmw_2018 = await vehicle_data_service.get_models_for_make("BMW", year=2018)
        print(f"[OK] Found {len(bmw_2018)} BMW models for 2018")
        if bmw_2018:
            print(f"Sample models: {[m['model'] for m in bmw_2018[:10]]}")

        print("\n=== Test Complete! ===\n")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

    finally:
        await database.disconnect()
        await carquery_client.close()
        await nhtsa_client.close()

if __name__ == "__main__":
    asyncio.run(test_filtered())
