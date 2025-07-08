"""
Repositorio de Procesos - Interfaz de Dominio

Esta interfaz define el contrato para acceder a los datos de procesos.
Siguiendo el patrón Repository, proporciona una abstracción que permite
acceder a los procesos sin depender de la implementación específica
de almacenamiento de datos.

Principios SOLID aplicados:
- Single Responsibility: Solo define operaciones para procesos
- Open/Closed: Extensible para nuevas operaciones
- Dependency Inversion: Define abstracción, no implementación
- Interface Segregation: Interface específica para procesos

Autor: Equipo de Desarrollo
Fecha: 2025-07-07
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from domain.models.proceso import Proceso, EstadoProceso, TipoProceso, NivelPrioridad


class ProcesoRepository(ABC):
    """
    Interfaz del repositorio de procesos.
    
    Define las operaciones básicas para acceder y manipular
    los datos de procesos en el sistema de persistencia.
    
    Esta interfaz sigue el patrón Repository Pattern, proporcionando
    una abstracción entre la lógica de dominio y la capa de datos.
    """
    
    @abstractmethod
    def crear_proceso(self, proceso: Proceso) -> Proceso:
        """
        Crea un nuevo proceso en el repositorio.
        
        Args:
            proceso: Proceso a crear
            
        Returns:
            Proceso: Proceso creado con ID asignado
            
        Raises:
            RepositoryError: Si ocurre un error al crear el proceso
        """
        pass
    
    @abstractmethod
    def obtener_por_id(self, proceso_id: str) -> Optional[Proceso]:
        """
        Obtiene un proceso por su ID.
        
        Args:
            proceso_id: ID del proceso a buscar
            
        Returns:
            Optional[Proceso]: Proceso encontrado o None si no existe
            
        Raises:
            RepositoryError: Si ocurre un error al buscar el proceso
        """
        pass
    
    @abstractmethod
    def obtener_todos(self) -> List[Proceso]:
        """
        Obtiene todos los procesos del repositorio.
        
        Returns:
            List[Proceso]: Lista de todos los procesos
            
        Raises:
            RepositoryError: Si ocurre un error al obtener los procesos
        """
        pass
    
    @abstractmethod
    def obtener_por_estado(self, estado: EstadoProceso) -> List[Proceso]:
        """
        Obtiene procesos filtrados por estado.
        
        Args:
            estado: Estado de los procesos a buscar
            
        Returns:
            List[Proceso]: Lista de procesos con el estado especificado
            
        Raises:
            RepositoryError: Si ocurre un error al buscar los procesos
        """
        pass
    
    @abstractmethod
    def obtener_por_tipo(self, tipo: TipoProceso) -> List[Proceso]:
        """
        Obtiene procesos filtrados por tipo.
        
        Args:
            tipo: Tipo de los procesos a buscar
            
        Returns:
            List[Proceso]: Lista de procesos del tipo especificado
            
        Raises:
            RepositoryError: Si ocurre un error al buscar los procesos
        """
        pass
    
    @abstractmethod
    def obtener_por_prioridad(self, prioridad: NivelPrioridad) -> List[Proceso]:
        """
        Obtiene procesos filtrados por prioridad.
        
        Args:
            prioridad: Prioridad de los procesos a buscar
            
        Returns:
            List[Proceso]: Lista de procesos con la prioridad especificada
            
        Raises:
            RepositoryError: Si ocurre un error al buscar los procesos
        """
        pass
    
    @abstractmethod
    def obtener_por_usuario(self, usuario: str) -> List[Proceso]:
        """
        Obtiene procesos asignados a un usuario.
        
        Args:
            usuario: Usuario asignado a los procesos
            
        Returns:
            List[Proceso]: Lista de procesos asignados al usuario
            
        Raises:
            RepositoryError: Si ocurre un error al buscar los procesos
        """
        pass
    
    @abstractmethod
    def obtener_por_fecha_limite(self, fecha_desde: datetime, fecha_hasta: datetime) -> List[Proceso]:
        """
        Obtiene procesos con fecha límite en un rango específico.
        
        Args:
            fecha_desde: Fecha de inicio del rango
            fecha_hasta: Fecha de fin del rango
            
        Returns:
            List[Proceso]: Lista de procesos con fecha límite en el rango
            
        Raises:
            RepositoryError: Si ocurre un error al buscar los procesos
        """
        pass
    
    @abstractmethod
    def obtener_procesos_activos(self) -> List[Proceso]:
        """
        Obtiene procesos que están activos (pendientes o en progreso).
        
        Returns:
            List[Proceso]: Lista de procesos activos
            
        Raises:
            RepositoryError: Si ocurre un error al buscar los procesos
        """
        pass
    
    @abstractmethod
    def obtener_procesos_vencidos(self) -> List[Proceso]:
        """
        Obtiene procesos que están vencidos.
        
        Returns:
            List[Proceso]: Lista de procesos vencidos
            
        Raises:
            RepositoryError: Si ocurre un error al buscar los procesos
        """
        pass
    
    @abstractmethod
    def obtener_procesos_por_recurso(self, recurso_id: str) -> List[Proceso]:
        """
        Obtiene procesos que requieren un recurso específico.
        
        Args:
            recurso_id: ID del recurso requerido
            
        Returns:
            List[Proceso]: Lista de procesos que requieren el recurso
            
        Raises:
            RepositoryError: Si ocurre un error al buscar los procesos
        """
        pass
    
    @abstractmethod
    def obtener_procesos_ejecutables(self) -> List[Proceso]:
        """
        Obtiene procesos que pueden ejecutarse (sin dependencias pendientes).
        
        Returns:
            List[Proceso]: Lista de procesos ejecutables
            
        Raises:
            RepositoryError: Si ocurre un error al buscar los procesos
        """
        pass
    
    @abstractmethod
    def actualizar_proceso(self, proceso: Proceso) -> Proceso:
        """
        Actualiza un proceso existente.
        
        Args:
            proceso: Proceso con los datos actualizados
            
        Returns:
            Proceso: Proceso actualizado
            
        Raises:
            RepositoryError: Si ocurre un error al actualizar el proceso
            ProcessNotFoundError: Si el proceso no existe
        """
        pass
    
    @abstractmethod
    def eliminar_proceso(self, proceso_id: str) -> bool:
        """
        Elimina un proceso del repositorio.
        
        Args:
            proceso_id: ID del proceso a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
            
        Raises:
            RepositoryError: Si ocurre un error al eliminar el proceso
            ProcessNotFoundError: Si el proceso no existe
        """
        pass
    
    @abstractmethod
    def buscar_procesos(self, criterios: Dict[str, Any]) -> List[Proceso]:
        """
        Busca procesos basándose en criterios específicos.
        
        Args:
            criterios: Diccionario con los criterios de búsqueda
                      Ejemplo: {"nombre": "proceso", "estado": "pendiente"}
            
        Returns:
            List[Proceso]: Lista de procesos que cumplen los criterios
            
        Raises:
            RepositoryError: Si ocurre un error al buscar los procesos
        """
        pass
    
    @abstractmethod
    def contar_procesos(self, filtros: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número de procesos que cumplen los filtros.
        
        Args:
            filtros: Filtros opcionales para la cuenta
            
        Returns:
            int: Número de procesos que cumplen los filtros
            
        Raises:
            RepositoryError: Si ocurre un error al contar los procesos
        """
        pass
    
    @abstractmethod
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de los procesos.
        
        Returns:
            Dict[str, Any]: Estadísticas de procesos
                          Ejemplo: {
                              "total": 100,
                              "por_estado": {"pendiente": 50, "completado": 30},
                              "por_tipo": {"rutinario": 70, "especial": 30}
                          }
            
        Raises:
            RepositoryError: Si ocurre un error al obtener estadísticas
        """
        pass
    
    @abstractmethod
    def obtener_procesos_paginados(self, pagina: int, tamaño: int) -> Dict[str, Any]:
        """
        Obtiene procesos con paginación.
        
        Args:
            pagina: Número de página (empezando en 1)
            tamaño: Tamaño de página
            
        Returns:
            Dict[str, Any]: Diccionario con procesos paginados
                          Ejemplo: {
                              "procesos": [Proceso...],
                              "pagina": 1,
                              "tamaño": 10,
                              "total": 100,
                              "paginas": 10
                          }
            
        Raises:
            RepositoryError: Si ocurre un error al obtener los procesos
        """
        pass
    
    @abstractmethod
    def crear_procesos_lote(self, procesos: List[Proceso]) -> List[Proceso]:
        """
        Crea múltiples procesos en una sola operación.
        
        Args:
            procesos: Lista de procesos a crear
            
        Returns:
            List[Proceso]: Lista de procesos creados
            
        Raises:
            RepositoryError: Si ocurre un error al crear los procesos
        """
        pass
    
    @abstractmethod
    def actualizar_procesos_lote(self, procesos: List[Proceso]) -> List[Proceso]:
        """
        Actualiza múltiples procesos en una sola operación.
        
        Args:
            procesos: Lista de procesos a actualizar
            
        Returns:
            List[Proceso]: Lista de procesos actualizados
            
        Raises:
            RepositoryError: Si ocurre un error al actualizar los procesos
        """
        pass
    
    @abstractmethod
    def eliminar_procesos_lote(self, proceso_ids: List[str]) -> bool:
        """
        Elimina múltiples procesos en una sola operación.
        
        Args:
            proceso_ids: Lista de IDs de procesos a eliminar
            
        Returns:
            bool: True si se eliminaron todos exitosamente
            
        Raises:
            RepositoryError: Si ocurre un error al eliminar los procesos
        """
        pass
    
    @abstractmethod
    def existe_proceso(self, proceso_id: str) -> bool:
        """
        Verifica si existe un proceso con el ID especificado.
        
        Args:
            proceso_id: ID del proceso a verificar
            
        Returns:
            bool: True si el proceso existe
            
        Raises:
            RepositoryError: Si ocurre un error al verificar la existencia
        """
        pass
    
    @abstractmethod
    def obtener_procesos_relacionados(self, proceso_id: str) -> List[Proceso]:
        """
        Obtiene procesos relacionados (dependencias y dependientes).
        
        Args:
            proceso_id: ID del proceso base
            
        Returns:
            List[Proceso]: Lista de procesos relacionados
            
        Raises:
            RepositoryError: Si ocurre un error al obtener los procesos relacionados
        """
        pass
    
    @abstractmethod
    def obtener_dependencias(self, proceso_id: str) -> List[Proceso]:
        """
        Obtiene las dependencias de un proceso.
        
        Args:
            proceso_id: ID del proceso
            
        Returns:
            List[Proceso]: Lista de procesos de los que depende
            
        Raises:
            RepositoryError: Si ocurre un error al obtener las dependencias
        """
        pass
    
    @abstractmethod
    def obtener_dependientes(self, proceso_id: str) -> List[Proceso]:
        """
        Obtiene los procesos que dependen de un proceso específico.
        
        Args:
            proceso_id: ID del proceso
            
        Returns:
            List[Proceso]: Lista de procesos que dependen de este
            
        Raises:
            RepositoryError: Si ocurre un error al obtener los dependientes
        """
        pass


class RepositoryError(Exception):
    """
    Excepción base para errores del repositorio.
    
    Se lanza cuando ocurre un error general en las operaciones
    del repositorio que no está relacionado con la lógica de negocio.
    """
    pass


class ProcessNotFoundError(RepositoryError):
    """
    Excepción que se lanza cuando no se encuentra un proceso.
    
    Se lanza cuando se intenta acceder a un proceso que no existe
    en el repositorio.
    """
    pass
