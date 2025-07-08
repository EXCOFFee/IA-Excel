"""
Database Configuration
Configuración de la base de datos SQLAlchemy
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Generator
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./planificador.db")

# Crear el motor de la base de datos
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

# Crear la sesión
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos ORM
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency para obtener la sesión de la base de datos
    
    Yields:
        Session: Sesión de la base de datos
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """
    Crear todas las tablas en la base de datos
    """
    # Importar los modelos aquí para asegurar que estén registrados
    from infrastructure.database.models import ProcesoORM, RecursoORM, AsignacionORM, PlanificacionORM
    
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """
    Eliminar todas las tablas de la base de datos
    """
    Base.metadata.drop_all(bind=engine)
