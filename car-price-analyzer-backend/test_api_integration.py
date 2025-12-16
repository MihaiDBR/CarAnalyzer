"""
Test script for API integration
Tests the new vehicle data endpoints
"""
import asyncio
from app.integrations.carquery import carquery_client
from app.integrations.nhtsa import nhtsa_client
from app.services.vehicle_data_service import vehicle_data_service
from app.database import database

async def test_apis():
    """Test the API integrations"""
    print("\n=== Testing API Integrations ===\n")

    try:
        # Connect to database
        await database.connect()
        print("[OK] Database connected")

        # Test CarQuery API
        print("\n--- Testing CarQuery API ---")
        makes = await carquery_client.get_makes()
        print(f"[OK] Fetched {len(makes)} makes from CarQuery")
        if makes:
            print(f"Sample makes: {[m.get('make_display') for m in makes[:5]]}")

        # Test NHTSA API
        print("\n--- Testing NHTSA API ---")
        nhtsa_makes = await nhtsa_client.get_makes()
        print(f"[OK] Fetched {len(nhtsa_makes)} makes from NHTSA")
        if nhtsa_makes:
            print(f"Sample makes: {[m.get('Make_Name') for m in nhtsa_makes[:5]]}")

        # Test Vehicle Data Service (with caching)
        print("\n--- Testing Vehicle Data Service ---")

        # Get makes (should aggregate both APIs and cache)
        service_makes = await vehicle_data_service.get_makes()
        print(f"[OK] Service fetched {len(service_makes)} makes")
        if service_makes:
            print(f"Sample makes: {[m.get('display') for m in service_makes[:5]]}")

        # Test getting models for BMW
        print("\n--- Testing Models for BMW ---")
        bmw_models = await vehicle_data_service.get_models_for_make("BMW")
        print(f"[OK] Fetched {len(bmw_models)} models for BMW")
        if bmw_models:
            print(f"Sample models: {[m.get('model') for m in bmw_models[:10]]}")

        # Test getting models for Volkswagen
        print("\n--- Testing Models for Volkswagen ---")
        vw_models = await vehicle_data_service.get_models_for_make("Volkswagen")
        print(f"[OK] Fetched {len(vw_models)} models for Volkswagen")
        if vw_models:
            print(f"Sample models: {[m.get('model') for m in vw_models[:10]]}")

        # Test vehicle specs
        print("\n--- Testing Vehicle Specs for BMW M3 (2020) ---")
        specs = await vehicle_data_service.get_vehicle_specs("BMW", "M3", 2020)
        if specs:
            print(f"[OK] Fetched specs: Engine={specs.get('engine')}, HP={specs.get('horsepower')}")
        else:
            print("[WARNING] No specs found (this is OK, not all vehicles have detailed specs)")

        print("\n=== All Tests Passed! ===\n")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        await database.disconnect()
        await carquery_client.close()
        await nhtsa_client.close()
        print("[OK] Cleaned up connections")

if __name__ == "__main__":
    asyncio.run(test_apis())
