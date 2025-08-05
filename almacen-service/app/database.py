"""
Configuración de la base de datos
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

# Crear engine de SQLAlchemy
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.debug  # Mostrar SQL queries en modo debug
)

# Crear SessionLocal
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener la sesión de base de datos
def get_db():
    """Obtener sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
