"""
Concrete Repository Implementation for Recurso
Implementación concreta del repositorio de recursos usando SQLAlchemy
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
import json

from domain.models.recurso import Recurso, TipoRecurso
from domain.repositories.recurso_repository import RecursoRepository
from infrastructure.database.models import RecursoORM


class SQLAlchemyRecursoRepository(RecursoRepository):
    """
    Implementación concreta del repositorio de recursos usando SQLAlchemy
    """
    
    def __init__(self, db: Session):
        """
        Inicializar el repositorio con la sesión de base de datos
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    def save(self, recurso: Recurso) -> Recurso:
        """
        Guardar un recurso en la base de datos
        
        Args:
            recurso: Recurso a guardar
            
        Returns:
            Recurso guardado
        """
        # Convertir especialidades a JSON string
        especialidades_json = json.dumps(recurso.especialidades) if recurso.especialidades else None
        
        # Buscar si ya existe
        db_recurso = self.db.query(RecursoORM).filter(RecursoORM.nombre == recurso.nombre).first()
        
        if db_recurso:
            # Actualizar recurso existente
            db_recurso.tipo = recurso.tipo.value
            db_recurso.capacidad_maxima = recurso.capacidad_maxima
            db_recurso.capacidad_actual = recurso.capacidad_actual
            db_recurso.disponible = recurso.disponible
            db_recurso.costo_por_hora = recurso.costo_por_hora
            db_recurso.especialidades = especialidades_json
            db_recurso.fecha_actualizacion = func.now()
        else:
            # Crear nuevo recurso
            db_recurso = RecursoORM(
                nombre=recurso.nombre,
                tipo=recurso.tipo.value,
                capacidad_maxima=recurso.capacidad_maxima,
                capacidad_actual=recurso.capacidad_actual,
                disponible=recurso.disponible,
                costo_por_hora=recurso.costo_por_hora,
                especialidades=especialidades_json
            )
            self.db.add(db_recurso)
        
        self.db.commit()
        self.db.refresh(db_recurso)
        
        return self._to_domain(db_recurso)
    
    def find_by_id(self, recurso_id: int) -> Optional[Recurso]:
        """
        Buscar recurso por ID
        
        Args:
            recurso_id: ID del recurso
            
        Returns:
            Recurso encontrado o None
        """
        db_recurso = self.db.query(RecursoORM).filter(RecursoORM.id == recurso_id).first()
        return self._to_domain(db_recurso) if db_recurso else None
    
    def find_by_nombre(self, nombre: str) -> Optional[Recurso]:
        """
        Buscar recurso por nombre
        
        Args:
            nombre: Nombre del recurso
            
        Returns:
            Recurso encontrado o None
        """
        db_recurso = self.db.query(RecursoORM).filter(RecursoORM.nombre == nombre).first()
        return self._to_domain(db_recurso) if db_recurso else None
    
    def find_all(self) -> List[Recurso]:
        """
        Obtener todos los recursos
        
        Returns:
            Lista de recursos
        """
        db_recursos = self.db.query(RecursoORM).all()
        return [self._to_domain(r) for r in db_recursos]
    
    def find_by_tipo(self, tipo: TipoRecurso) -> List[Recurso]:
        """
        Buscar recursos por tipo
        
        Args:
            tipo: Tipo de recurso a buscar
            
        Returns:
            Lista de recursos del tipo especificado
        """
        db_recursos = self.db.query(RecursoORM).filter(
            RecursoORM.tipo == tipo.value
        ).all()
        return [self._to_domain(r) for r in db_recursos]
    
    def find_disponibles(self) -> List[Recurso]:
        """
        Obtener recursos disponibles
        
        Returns:
            Lista de recursos disponibles
        """
        db_recursos = self.db.query(RecursoORM).filter(
            RecursoORM.disponible == True
        ).all()
        return [self._to_domain(r) for r in db_recursos]
    
    def delete(self, recurso_id: int) -> bool:
        """
        Eliminar recurso por ID
        
        Args:
            recurso_id: ID del recurso a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        db_recurso = self.db.query(RecursoORM).filter(RecursoORM.id == recurso_id).first()
        if db_recurso:
            self.db.delete(db_recurso)
            self.db.commit()
            return True
        return False
    
    def count(self) -> int:
        """
        Contar el número total de recursos
        
        Returns:
            Número total de recursos
        """
        return self.db.query(RecursoORM).count()
    
    def _to_domain(self, db_recurso: RecursoORM) -> Recurso:
        """
        Convertir modelo ORM a entidad de dominio
        
        Args:
            db_recurso: Recurso ORM
            
        Returns:
            Recurso de dominio
        """
        especialidades = []
        if db_recurso.especialidades:
            try:
                especialidades = json.loads(db_recurso.especialidades)
            except json.JSONDecodeError:
                especialidades = []
        
        return Recurso(
            nombre=db_recurso.nombre,
            tipo=TipoRecurso(db_recurso.tipo),
            capacidad_maxima=db_recurso.capacidad_maxima,
            capacidad_actual=db_recurso.capacidad_actual,
            disponible=db_recurso.disponible,
            costo_por_hora=db_recurso.costo_por_hora,
            especialidades=especialidades
        )
