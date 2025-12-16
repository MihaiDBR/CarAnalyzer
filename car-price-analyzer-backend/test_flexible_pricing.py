"""
Test Flexible Pricing System
Should work for ANY car, no exceptions!
"""
import asyncio
from app.analysis.flexible_price_analyzer import flexible_analyzer
from app.database import database

async def test_pricing():
    print("\n=== Testing Flexible Pricing System ===\n")

    await database.connect()

    test_cases = [
        {
            'name': 'BMW 340i (should work)',
            'marca': 'BMW',
            'model': '340i',
            'an': 2018,
            'km': 85000,
            'dotari': ['piele', 'navigatie', 'xenon']
        },
        {
            'name': 'Bentley Bentayga (exotic, should work)',
            'marca': 'Bentley',
            'model': 'Bentayga',
            'an': 2020,
            'km': 30000,
            'dotari': ['piele', 'trapa', 'sport']
        },
        {
            'name': 'Dacia Logan (budget, should work)',
            'marca': 'Dacia',
            'model': 'Logan',
            'an': 2019,
            'km': 95000,
            'dotari': ['clima']
        },
        {
            'name': 'Mercedes S-Class (luxury, should work)',
            'marca': 'Mercedes-Benz',
            'model': 'S-Class',
            'an': 2021,
            'km': 25000,
            'dotari': ['piele', 'trapa', 'navigatie', 'sport']
        },
        {
            'name': 'VW Golf (mass market, should work)',
            'marca': 'Volkswagen',
            'model': 'Golf',
            'an': 2017,
            'km': 120000,
            'dotari': ['clima', 'senzori']
        }
    ]

    for test in test_cases:
        print(f"\n--- Testing: {test['name']} ---")
        try:
            result = await flexible_analyzer.calculate_price_with_fallback(
                marca=test['marca'],
                model=test['model'],
                an=test['an'],
                km=test['km'],
                dotari_list=test['dotari']
            )

            print(f"[OK] SUCCESS!")
            print(f"   Pret Optim: EUR {result['pret_optim']['valoare']:,}")
            print(f"   Pret Rapid: EUR {result['pret_rapid']['valoare']:,}")
            print(f"   Pret Maxim: EUR {result['pret_maxim']['valoare']:,}")
            print(f"   Valoare Dotari: EUR {result['valoare_dotari']:,}")
            print(f"   Sursa: {result['market_data']['source']}")
            print(f"   Incredere: {result['market_data']['confidence']}%")
            print(f"   Descriere: {result['market_data']['description']}")

        except Exception as e:
            print(f"[ERROR] FAILED: {e}")
            import traceback
            traceback.print_exc()

    await database.disconnect()

    print("\n=== Test Complete! ===\n")

if __name__ == "__main__":
    asyncio.run(test_pricing())
