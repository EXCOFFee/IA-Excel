"""
Database Models
Modelos ORM para la persistencia de datos
"""

from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from infrastructure.database.config import Base


class ProcesoORM(Base):
    """
    Modelo ORM para la entidad Proceso
    """
    __tablename__ = "procesos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    tiempo_estimado = Column(Float, nullable=False)
    recursos_necesarios = Column(Text, nullable=True)  # JSON string
    prioridad = Column(String(20), nullable=False)
    estado = Column(String(20), nullable=False)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    recursos = relationship("RecursoORM", back_populates="proceso")


class RecursoORM(Base):
    """
    Modelo ORM para la entidad Recurso
    """
    __tablename__ = "recursos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    tipo = Column(String(50), nullable=False)
    capacidad_maxima = Column(Float, nullable=False)
    capacidad_actual = Column(Float, default=0.0)
    disponible = Column(Boolean, default=True)
    costo_por_hora = Column(Float, default=0.0)
    especialidades = Column(Text, nullable=True)  # JSON string
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relaciones
    proceso_id = Column(Integer, ForeignKey("procesos.id"))
    proceso = relationship("ProcesoORM", back_populates="recursos")


class AsignacionORM(Base):
    """
    Modelo ORM para las asignaciones de recursos a procesos
    """
    __tablename__ = "asignaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    proceso_id = Column(Integer, ForeignKey("procesos.id"), nullable=False)
    recurso_id = Column(Integer, ForeignKey("recursos.id"), nullable=False)
    fecha_asignacion = Column(DateTime, nullable=False)
    fecha_fin_estimada = Column(DateTime, nullable=True)
    fecha_fin_real = Column(DateTime, nullable=True)
    horas_estimadas = Column(Float, nullable=False)
    horas_reales = Column(Float, nullable=True)
    estado = Column(String(20), nullable=False)
    notas = Column(Text, nullable=True)
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())


class PlanificacionORM(Base):
    """
    Modelo ORM para las planificaciones generadas
    """
    __tablename__ = "planificaciones"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(200), nullable=False)
    descripcion = Column(Text, nullable=True)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    estado = Column(String(20), nullable=False)
    algoritmo_usado = Column(String(50), nullable=False)
    parametros = Column(Text, nullable=True)  # JSON string
    resultados = Column(Text, nullable=True)  # JSON string
    fecha_creacion = Column(DateTime, default=func.now())
    fecha_actualizacion = Column(DateTime, default=func.now(), onupdate=func.now())
