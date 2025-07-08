"""
Domain repository interface for Recurso
Interfaz del repositorio de recursos
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.recurso import Recurso, TipoRecurso


class RecursoRepository(ABC):
    """
    Interfaz del repositorio de recursos
    Define las operaciones de persistencia para los recursos
    """
    
    @abstractmethod
    def save(self, recurso: Recurso) -> Recurso:
        """
        Guardar un recurso
        
        Args:
            recurso: Recurso a guardar
            
        Returns:
            Recurso guardado
        """
        pass
    
    @abstractmethod
    def find_by_id(self, recurso_id: int) -> Optional[Recurso]:
        """
        Buscar recurso por ID
        
        Args:
            recurso_id: ID del recurso
            
        Returns:
            Recurso encontrado o None
        """
        pass
    
    @abstractmethod
    def find_by_nombre(self, nombre: str) -> Optional[Recurso]:
        """
        Buscar recurso por nombre
        
        Args:
            nombre: Nombre del recurso
            
        Returns:
            Recurso encontrado o None
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[Recurso]:
        """
        Obtener todos los recursos
        
        Returns:
            Lista de recursos
        """
        pass
    
    @abstractmethod
    def find_by_tipo(self, tipo: TipoRecurso) -> List[Recurso]:
        """
        Buscar recursos por tipo
        
        Args:
            tipo: Tipo de recurso a buscar
            
        Returns:
            Lista de recursos del tipo especificado
        """
        pass
    
    @abstractmethod
    def find_disponibles(self) -> List[Recurso]:
        """
        Obtener recursos disponibles
        
        Returns:
            Lista de recursos disponibles
        """
        pass
    
    @abstractmethod
    def delete(self, recurso_id: int) -> bool:
        """
        Eliminar recurso por ID
        
        Args:
            recurso_id: ID del recurso a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Contar el número total de recursos
        
        Returns:
            Número total de recursos
        """
        pass
