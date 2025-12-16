"""
Database Migration Script
Creates new tables for API caching without dropping existing data
"""
from app.database import create_tables, database
import asyncio

async def migrate():
    """Run database migration"""
    print("Starting database migration...")

    try:
        # Connect to database
        await database.connect()
        print("Connected to database")

        # Create new tables (will skip existing tables)
        create_tables()
        print("Created new tables (api_makes_cache, api_models_cache, vehicle_specs_cache)")

        # Disconnect
        await database.disconnect()
        print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(migrate())
