# ============================================
# BACKEND - app/database.py
# Configurare bază de date
# ============================================

import os
import databases
import sqlalchemy
from sqlalchemy import MetaData
from dotenv import load_dotenv

load_dotenv()

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)

# Databases instance
database = databases.Database(DATABASE_URL)

# SQLAlchemy metadata
metadata = MetaData()

# ============================================
# DEFINIRE TABELE
# ============================================

# Tabel pentru mărci și modele
car_models = sqlalchemy.Table(
    "car_models",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("marca", sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column("model", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("pret_baza_nou", sqlalchemy.Float),
    sqlalchemy.Column("an_lansare", sqlalchemy.Integer),
    sqlalchemy.Column("depreciere_an", sqlalchemy.Float),
    sqlalchemy.Column("popularitate_score", sqlalchemy.Float),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, onupdate=sqlalchemy.func.now()),
)

# Tabel pentru dotări
dotari = sqlalchemy.Table(
    "dotari",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("nume", sqlalchemy.String(100), nullable=False, unique=True),
    sqlalchemy.Column("valoare_medie", sqlalchemy.Float),
    sqlalchemy.Column("impact_vanzare", sqlalchemy.Float),
    sqlalchemy.Column("depreciere_an", sqlalchemy.Float),
    sqlalchemy.Column("categorie", sqlalchemy.String(50)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
)

# Tabel pentru anunțuri scraped
listings = sqlalchemy.Table(
    "listings",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("source", sqlalchemy.String(50), nullable=False),
    sqlalchemy.Column("url", sqlalchemy.String(500), unique=True, nullable=False),
    sqlalchemy.Column("marca", sqlalchemy.String(50)),
    sqlalchemy.Column("model", sqlalchemy.String(100)),
    sqlalchemy.Column("model_series", sqlalchemy.String(50)),  # NEW: "Seria 1", "Golf", etc.
    sqlalchemy.Column("model_variant", sqlalchemy.String(50)),  # NEW: "GTI", "R", "M", "AMG", etc.
    sqlalchemy.Column("an", sqlalchemy.Integer),
    sqlalchemy.Column("km", sqlalchemy.Integer),
    sqlalchemy.Column("pret", sqlalchemy.Float),
    sqlalchemy.Column("combustibil", sqlalchemy.String(20)),
    sqlalchemy.Column("putere_cp", sqlalchemy.Integer),  # NEW: Putere în CP
    sqlalchemy.Column("capacitate_cilindrica", sqlalchemy.Integer),  # NEW: cm3
    sqlalchemy.Column("transmisie", sqlalchemy.String(20)),  # NEW: "manuala", "automata"
    sqlalchemy.Column("tractiune", sqlalchemy.String(20)),  # NEW: "fata", "spate", "4x4"
    sqlalchemy.Column("caroserie", sqlalchemy.String(30)),  # NEW: "hatchback", "sedan", "break", "coupe", "suv"
    sqlalchemy.Column("locatie", sqlalchemy.String(100)),
    sqlalchemy.Column("dotari", sqlalchemy.JSON),
    sqlalchemy.Column("imagini", sqlalchemy.JSON),
    sqlalchemy.Column("descriere", sqlalchemy.Text),
    sqlalchemy.Column("telefon", sqlalchemy.String(20)),
    sqlalchemy.Column("data_publicare", sqlalchemy.DateTime),
    sqlalchemy.Column("data_scraping", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("data_scrape", sqlalchemy.DateTime),  # Alias for compatibility
    sqlalchemy.Column("este_activ", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("vizualizari", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("zile_pe_piata", sqlalchemy.Integer, default=0),  # For compatibility
)

# Tabel pentru istoricul prețurilor
price_history = sqlalchemy.Table(
    "price_history",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("listing_id", sqlalchemy.Integer, sqlalchemy.ForeignKey("listings.id")),
    sqlalchemy.Column("pret", sqlalchemy.Float),
    sqlalchemy.Column("data_modificare", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
)

# Tabel pentru analize salvate
saved_analyses = sqlalchemy.Table(
    "saved_analyses",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("marca", sqlalchemy.String(50)),
    sqlalchemy.Column("model", sqlalchemy.String(100)),
    sqlalchemy.Column("an", sqlalchemy.Integer),
    sqlalchemy.Column("km", sqlalchemy.Integer),
    sqlalchemy.Column("dotari", sqlalchemy.JSON),
    sqlalchemy.Column("pret_optim", sqlalchemy.Float),
    sqlalchemy.Column("rezultat_complet", sqlalchemy.JSON),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
)

# Tabel pentru cache-uirea makes din API-uri
api_makes_cache = sqlalchemy.Table(
    "api_makes_cache",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("make_name", sqlalchemy.String(100), nullable=False, unique=True),
    sqlalchemy.Column("make_display", sqlalchemy.String(100)),
    sqlalchemy.Column("make_country", sqlalchemy.String(50)),
    sqlalchemy.Column("source", sqlalchemy.String(20)),  # 'carquery', 'nhtsa'
    sqlalchemy.Column("cached_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, onupdate=sqlalchemy.func.now()),
)

# Tabel pentru cache-uirea models din API-uri
api_models_cache = sqlalchemy.Table(
    "api_models_cache",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("make_name", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("model_name", sqlalchemy.String(200), nullable=False),
    sqlalchemy.Column("model_year_min", sqlalchemy.Integer),
    sqlalchemy.Column("model_year_max", sqlalchemy.Integer),
    sqlalchemy.Column("body_type", sqlalchemy.String(50)),
    sqlalchemy.Column("fuel_type", sqlalchemy.String(50)),
    sqlalchemy.Column("source", sqlalchemy.String(20)),  # 'carquery', 'nhtsa'
    sqlalchemy.Column("cached_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, onupdate=sqlalchemy.func.now()),
    sqlalchemy.Index("idx_make_model", "make_name", "model_name"),
)

# Tabel pentru specificații complete vehicule (cache NHTSA/CarQuery)
vehicle_specs_cache = sqlalchemy.Table(
    "vehicle_specs_cache",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("make", sqlalchemy.String(100), nullable=False),
    sqlalchemy.Column("model", sqlalchemy.String(200), nullable=False),
    sqlalchemy.Column("year", sqlalchemy.Integer),
    sqlalchemy.Column("trim", sqlalchemy.String(200)),
    sqlalchemy.Column("engine", sqlalchemy.String(200)),
    sqlalchemy.Column("horsepower", sqlalchemy.Integer),
    sqlalchemy.Column("transmission", sqlalchemy.String(100)),
    sqlalchemy.Column("drive_type", sqlalchemy.String(50)),
    sqlalchemy.Column("fuel_type", sqlalchemy.String(50)),
    sqlalchemy.Column("body_type", sqlalchemy.String(50)),
    sqlalchemy.Column("doors", sqlalchemy.Integer),
    sqlalchemy.Column("seats", sqlalchemy.Integer),
    sqlalchemy.Column("standard_equipment", sqlalchemy.JSON),
    sqlalchemy.Column("optional_equipment", sqlalchemy.JSON),
    sqlalchemy.Column("source", sqlalchemy.String(20)),
    sqlalchemy.Column("source_id", sqlalchemy.String(100)),
    sqlalchemy.Column("cached_at", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("updated_at", sqlalchemy.DateTime, onupdate=sqlalchemy.func.now()),
    sqlalchemy.Index("idx_make_model_year", "make", "model", "year"),
)

# Create engine
engine = sqlalchemy.create_engine(DATABASE_URL)

# Creare tabele
def create_tables():
    metadata.create_all(engine)
    print("Tables created successfully")

# Drop tabele (folosește cu grijă!)
def drop_tables():
    metadata.drop_all(engine)
    print("Tables dropped successfully")