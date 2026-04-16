from sqlalchemy.orm import declarative_base

# =========================================================
# database.py
# Archivo de compatibilidad temporal para mantener imports
# mientras migramos toda la app de conexión directa a API.
# =========================================================

engine = None
SessionLocal = None

Base = declarative_base()