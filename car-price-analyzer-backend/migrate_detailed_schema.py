"""
Database Migration - Add detailed car specifications columns
"""
import asyncio
from app.database import database, DATABASE_URL
import sqlalchemy


async def migrate():
    print("\n=== Database Migration: Add Detailed Specs ===\n")

    await database.connect()

    # Add new columns to listings table
    new_columns = [
        "ALTER TABLE listings ADD COLUMN IF NOT EXISTS model_series VARCHAR(50)",
        "ALTER TABLE listings ADD COLUMN IF NOT EXISTS model_variant VARCHAR(50)",
        "ALTER TABLE listings ADD COLUMN IF NOT EXISTS putere_cp INTEGER",
        "ALTER TABLE listings ADD COLUMN IF NOT EXISTS capacitate_cilindrica INTEGER",
        "ALTER TABLE listings ADD COLUMN IF NOT EXISTS transmisie VARCHAR(20)",
        "ALTER TABLE listings ADD COLUMN IF NOT EXISTS tractiune VARCHAR(20)",
        "ALTER TABLE listings ADD COLUMN IF NOT EXISTS caroserie VARCHAR(30)",
        "ALTER TABLE listings ADD COLUMN IF NOT EXISTS data_scrape TIMESTAMP",
        "ALTER TABLE listings ADD COLUMN IF NOT EXISTS zile_pe_piata INTEGER DEFAULT 0",
    ]

    for sql in new_columns:
        try:
            await database.execute(sql)
            print(f"[OK] {sql.split('ADD COLUMN')[1].split()[2] if 'ADD COLUMN' in sql else 'Executed'}")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print(f"[SKIP] Column already exists")
            else:
                print(f"[ERROR] {e}")

    await database.disconnect()
    print("\n[SUCCESS] Migration complete!\n")


if __name__ == "__main__":
    asyncio.run(migrate())
