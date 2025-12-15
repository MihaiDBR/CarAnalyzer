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
    sqlalchemy.Column("an", sqlalchemy.Integer),
    sqlalchemy.Column("km", sqlalchemy.Integer),
    sqlalchemy.Column("pret", sqlalchemy.Float),
    sqlalchemy.Column("combustibil", sqlalchemy.String(20)),
    sqlalchemy.Column("locatie", sqlalchemy.String(100)),
    sqlalchemy.Column("dotari", sqlalchemy.JSON),
    sqlalchemy.Column("imagini", sqlalchemy.JSON),
    sqlalchemy.Column("descriere", sqlalchemy.Text),
    sqlalchemy.Column("telefon", sqlalchemy.String(20)),
    sqlalchemy.Column("data_publicare", sqlalchemy.DateTime),
    sqlalchemy.Column("data_scraping", sqlalchemy.DateTime, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column("este_activ", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("vizualizari", sqlalchemy.Integer, default=0),
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

# Create engine
engine = sqlalchemy.create_engine(DATABASE_URL)

# Creare tabele
def create_tables():
    metadata.create_all(engine)
    print("✓ Tables created successfully")

# Drop tabele (folosește cu grijă!)
def drop_tables():
    metadata.drop_all(engine)
    print("✓ Tables dropped successfully")