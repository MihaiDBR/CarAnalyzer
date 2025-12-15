# ============================================
# populate_db.py
# Script pentru popularea inițială a bazei de date
# Rulează cu: python populate_db.py
# ============================================

import asyncio
from app.database import database, car_models, dotari, create_tables

# Date reale pentru mărci și modele populare
CAR_DATA = [
    {
        "marca": "Volkswagen",
        "model": "Golf 7",
        "pret_baza_nou": 20000,
        "an_lansare": 2012,
        "depreciere_an": 0.12,
        "popularitate_score": 9.2
    },
    {
        "marca": "Volkswagen",
        "model": "Passat B8",
        "pret_baza_nou": 28000,
        "an_lansare": 2014,
        "depreciere_an": 0.13,
        "popularitate_score": 8.5
    },
    {
        "marca": "BMW",
        "model": "Seria 3 F30",
        "pret_baza_nou": 35000,
        "an_lansare": 2012,
        "depreciere_an": 0.15,
        "popularitate_score": 8.8
    },
    {
        "marca": "BMW",
        "model": "Seria 5 F10",
        "pret_baza_nou": 45000,
        "an_lansare": 2010,
        "depreciere_an": 0.16,
        "popularitate_score": 8.3
    },
    {
        "marca": "Mercedes",
        "model": "C-Class W204",
        "pret_baza_nou": 38000,
        "an_lansare": 2007,
        "depreciere_an": 0.14,
        "popularitate_score": 8.6
    },
    {
        "marca": "Mercedes",
        "model": "E-Class W212",
        "pret_baza_nou": 48000,
        "an_lansare": 2009,
        "depreciere_an": 0.15,
        "popularitate_score": 8.4
    },
    {
        "marca": "Audi",
        "model": "A4 B8",
        "pret_baza_nou": 32000,
        "an_lansare": 2008,
        "depreciere_an": 0.13,
        "popularitate_score": 8.7
    },
    {
        "marca": "Audi",
        "model": "A6 C7",
        "pret_baza_nou": 42000,
        "an_lansare": 2011,
        "depreciere_an": 0.14,
        "popularitate_score": 8.2
    },
    {
        "marca": "Skoda",
        "model": "Octavia 3",
        "pret_baza_nou": 18000,
        "an_lansare": 2013,
        "depreciere_an": 0.11,
        "popularitate_score": 9.0
    },
    {
        "marca": "Skoda",
        "model": "Superb 3",
        "pret_baza_nou": 25000,
        "an_lansare": 2015,
        "depreciere_an": 0.12,
        "popularitate_score": 8.4
    },
    {
        "marca": "Dacia",
        "model": "Logan",
        "pret_baza_nou": 9000,
        "an_lansare": 2012,
        "depreciere_an": 0.10,
        "popularitate_score": 8.8
    },
    {
        "marca": "Dacia",
        "model": "Duster",
        "pret_baza_nou": 13000,
        "an_lansare": 2010,
        "depreciere_an": 0.11,
        "popularitate_score": 9.1
    },
    {
        "marca": "Ford",
        "model": "Focus 3",
        "pret_baza_nou": 17000,
        "an_lansare": 2010,
        "depreciere_an": 0.13,
        "popularitate_score": 8.3
    },
    {
        "marca": "Ford",
        "model": "Mondeo 4",
        "pret_baza_nou": 24000,
        "an_lansare": 2007,
        "depreciere_an": 0.14,
        "popularitate_score": 7.9
    },
    {
        "marca": "Opel",
        "model": "Astra J",
        "pret_baza_nou": 16000,
        "an_lansare": 2009,
        "depreciere_an": 0.13,
        "popularitate_score": 8.1
    },
    {
        "marca": "Toyota",
        "model": "Corolla",
        "pret_baza_nou": 19000,
        "an_lansare": 2013,
        "depreciere_an": 0.10,
        "popularitate_score": 9.3
    },
    {
        "marca": "Toyota",
        "model": "RAV4",
        "pret_baza_nou": 28000,
        "an_lansare": 2013,
        "depreciere_an": 0.11,
        "popularitate_score": 8.9
    },
    {
        "marca": "Honda",
        "model": "Civic",
        "pret_baza_nou": 18000,
        "an_lansare": 2012,
        "depreciere_an": 0.11,
        "popularitate_score": 8.6
    },
    {
        "marca": "Mazda",
        "model": "3",
        "pret_baza_nou": 17500,
        "an_lansare": 2013,
        "depreciere_an": 0.12,
        "popularitate_score": 8.4
    },
    {
        "marca": "Mazda",
        "model": "6",
        "pret_baza_nou": 24000,
        "an_lansare": 2012,
        "depreciere_an": 0.13,
        "popularitate_score": 8.2
    }
]

# Dotări comune și valorile lor
EQUIPMENT_DATA = [
    {
        "nume": "Interior piele",
        "valoare_medie": 2000,
        "impact_vanzare": 15,
        "depreciere_an": 0.08,
        "categorie": "interior"
    },
    {
        "nume": "Sistem navigație",
        "valoare_medie": 1500,
        "impact_vanzare": 12,
        "depreciere_an": 0.15,
        "categorie": "tehnologie"
    },
    {
        "nume": "Faruri Xenon/LED",
        "valoare_medie": 1200,
        "impact_vanzare": 10,
        "depreciere_an": 0.05,
        "categorie": "exterior"
    },
    {
        "nume": "Senzori parcare",
        "valoare_medie": 800,
        "impact_vanzare": 8,
        "depreciere_an": 0.10,
        "categorie": "siguranta"
    },
    {
        "nume": "Cameră marsarier",
        "valoare_medie": 600,
        "impact_vanzare": 8,
        "depreciere_an": 0.12,
        "categorie": "siguranta"
    },
    {
        "nume": "Scaune încălzite",
        "valoare_medie": 700,
        "impact_vanzare": 7,
        "depreciere_an": 0.08,
        "categorie": "confort"
    },
    {
        "nume": "Climatronic",
        "valoare_medie": 900,
        "impact_vanzare": 9,
        "depreciere_an": 0.10,
        "categorie": "confort"
    },
    {
        "nume": "Jante aliaj",
        "valoare_medie": 500,
        "impact_vanzare": 5,
        "depreciere_an": 0.07,
        "categorie": "exterior"
    },
    {
        "nume": "Cruise control",
        "valoare_medie": 400,
        "impact_vanzare": 6,
        "depreciere_an": 0.10,
        "categorie": "confort"
    },
    {
        "nume": "Keyless entry",
        "valoare_medie": 800,
        "impact_vanzare": 7,
        "depreciere_an": 0.12,
        "categorie": "siguranta"
    },
    {
        "nume": "Trapă/Teto panoramic",
        "valoare_medie": 1800,
        "impact_vanzare": 14,
        "depreciere_an": 0.08,
        "categorie": "confort"
    },
    {
        "nume": "Pachet sport",
        "valoare_medie": 2500,
        "impact_vanzare": 18,
        "depreciere_an": 0.10,
        "categorie": "performanta"
    },
    {
        "nume": "Sistem audio premium",
        "valoare_medie": 1000,
        "impact_vanzare": 8,
        "depreciere_an": 0.15,
        "categorie": "entertainment"
    },
    {
        "nume": "Volan piele/multifunctional",
        "valoare_medie": 300,
        "impact_vanzare": 5,
        "depreciere_an": 0.10,
        "categorie": "interior"
    },
    {
        "nume": "Start/Stop",
        "valoare_medie": 200,
        "impact_vanzare": 3,
        "depreciere_an": 0.10,
        "categorie": "performanta"
    },
    {
        "nume": "Bluetooth/USB",
        "valoare_medie": 150,
        "impact_vanzare": 4,
        "depreciere_an": 0.20,
        "categorie": "tehnologie"
    },
    {
        "nume": "Oglinzi electrice/incalzite",
        "valoare_medie": 200,
        "impact_vanzare": 3,
        "depreciere_an": 0.08,
        "categorie": "confort"
    },
    {
        "nume": "Geamuri electrice",
        "valoare_medie": 250,
        "impact_vanzare": 4,
        "depreciere_an": 0.08,
        "categorie": "confort"
    },
    {
        "nume": "Pilot automat adaptiv",
        "valoare_medie": 1200,
        "impact_vanzare": 12,
        "depreciere_an": 0.12,
        "categorie": "siguranta"
    },
    {
        "nume": "Head-up display",
        "valoare_medie": 800,
        "impact_vanzare": 9,
        "depreciere_an": 0.15,
        "categorie": "tehnologie"
    }
]

async def populate_database():
    """Populează baza de date cu date inițiale"""
    
    print("🚀 Începe popularea bazei de date...")
    
    try:
        # Conectare la baza de date
        await database.connect()
        print("✓ Conectat la baza de date")
        
        # Creează tabelele dacă nu există
        create_tables()
        print("✓ Tabele create/verificate")
        
        # Populează mărci și modele
        print("\n📊 Populare mărci și modele...")
        for car in CAR_DATA:
            try:
                query = car_models.insert().values(**car)
                await database.execute(query)
                print(f"  ✓ {car['marca']} {car['model']}")
            except Exception as e:
                print(f"  ⚠ Skip {car['marca']} {car['model']}: {e}")
        
        # Populează dotări
        print("\n🔧 Populare dotări...")
        for equipment in EQUIPMENT_DATA:
            try:
                query = dotari.insert().values(**equipment)
                await database.execute(query)
                print(f"  ✓ {equipment['nume']}")
            except Exception as e:
                print(f"  ⚠ Skip {equipment['nume']}: {e}")
        
        print("\n✅ Baza de date a fost populată cu succes!")
        print(f"   - {len(CAR_DATA)} mărci/modele adăugate")
        print(f"   - {len(EQUIPMENT_DATA)} dotări adăugate")
        
    except Exception as e:
        print(f"\n❌ Eroare: {e}")
    finally:
        await database.disconnect()
        print("\n✓ Deconectat de la baza de date")

if __name__ == "__main__":
    asyncio.run(populate_database())