"""
Concrete Repository Implementation for Proceso
Implementación concreta del repositorio de procesos usando SQLAlchemy
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from datetime import datetime
import json

from domain.models.proceso import Proceso, NivelPrioridad, EstadoProceso, TipoProceso
from domain.repositories.proceso_repository import ProcesoRepository, RepositoryError, ProcessNotFoundError
from infrastructure.database.models import ProcesoORM


class SQLAlchemyProcesoRepository(ProcesoRepository):
    """
    Implementación concreta del repositorio de procesos usando SQLAlchemy
    """
    
    def __init__(self, db: Session):
        """
        Inicializar el repositorio con la sesión de base de datos
        
        Args:
            db: Sesión de base de datos SQLAlchemy
        """
        self.db = db
    
    def crear_proceso(self, proceso: Proceso) -> Proceso:
        """
        Crea un nuevo proceso en el repositorio.
        
        Args:
            proceso: Proceso a crear
            
        Returns:
            Proceso: Proceso creado con ID asignado
        """
        try:
            # Convertir recursos necesarios a JSON string
            recursos_json = json.dumps(proceso.recursos_requeridos) if proceso.recursos_requeridos else None
            
            # Crear nuevo proceso
            db_proceso = ProcesoORM(
                codigo=proceso.id,  # Usar el ID del proceso como código
                nombre=proceso.nombre,
                descripcion=proceso.descripcion,
                tiempo_estimado=proceso.tiempo_estimado_horas,
                recursos_necesarios=recursos_json,
                prioridad=proceso.prioridad.value,
                estado=proceso.estado.value
            )
            
            self.db.add(db_proceso)
            self.db.commit()
            self.db.refresh(db_proceso)
            
            return self._to_domain(db_proceso)
            
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Error al crear proceso: {str(e)}")
    
    def obtener_por_id(self, proceso_id: str) -> Optional[Proceso]:
        """
        Obtiene un proceso por su ID.
        
        Args:
            proceso_id: ID del proceso a buscar
            
        Returns:
            Optional[Proceso]: Proceso encontrado o None si no existe
        """
        try:
            db_proceso = self.db.query(ProcesoORM).filter(ProcesoORM.codigo == proceso_id).first()
            return self._to_domain(db_proceso) if db_proceso else None
        except Exception as e:
            raise RepositoryError(f"Error al obtener proceso por ID: {str(e)}")
    
    def obtener_todos(self) -> List[Proceso]:
        """
        Obtiene todos los procesos del repositorio.
        
        Returns:
            List[Proceso]: Lista de todos los procesos
        """
        try:
            db_procesos = self.db.query(ProcesoORM).all()
            return [self._to_domain(p) for p in db_procesos]
        except Exception as e:
            raise RepositoryError(f"Error al obtener todos los procesos: {str(e)}")
    
    def obtener_por_estado(self, estado: EstadoProceso) -> List[Proceso]:
        """
        Obtiene procesos filtrados por estado.
        
        Args:
            estado: Estado de los procesos a buscar
            
        Returns:
            List[Proceso]: Lista de procesos con el estado especificado
        """
        try:
            db_procesos = self.db.query(ProcesoORM).filter(
                ProcesoORM.estado == estado.value
            ).all()
            return [self._to_domain(p) for p in db_procesos]
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos por estado: {str(e)}")
    
    def obtener_por_tipo(self, tipo: TipoProceso) -> List[Proceso]:
        """
        Obtiene procesos filtrados por tipo.
        
        Args:
            tipo: Tipo de los procesos a buscar
            
        Returns:
            List[Proceso]: Lista de procesos del tipo especificado
        """
        try:
            # Nota: Necesitaríamos agregar una columna tipo en ProcesoORM
            # Por ahora, devolvemos todos los procesos
            return self.obtener_todos()
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos por tipo: {str(e)}")
    
    def obtener_por_prioridad(self, prioridad: NivelPrioridad) -> List[Proceso]:
        """
        Obtiene procesos filtrados por prioridad.
        
        Args:
            prioridad: Prioridad de los procesos a buscar
            
        Returns:
            List[Proceso]: Lista de procesos con la prioridad especificada
        """
        try:
            db_procesos = self.db.query(ProcesoORM).filter(
                ProcesoORM.prioridad == prioridad.value
            ).all()
            return [self._to_domain(p) for p in db_procesos]
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos por prioridad: {str(e)}")
    
    def obtener_por_usuario(self, usuario: str) -> List[Proceso]:
        """
        Obtiene procesos asignados a un usuario.
        
        Args:
            usuario: Usuario asignado a los procesos
            
        Returns:
            List[Proceso]: Lista de procesos asignados al usuario
        """
        try:
            # Nota: Necesitaríamos agregar una columna usuario en ProcesoORM
            # Por ahora, devolvemos todos los procesos
            return self.obtener_todos()
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos por usuario: {str(e)}")
    
    def obtener_por_fecha_limite(self, fecha_desde: datetime, fecha_hasta: datetime) -> List[Proceso]:
        """
        Obtiene procesos con fecha límite en un rango específico.
        
        Args:
            fecha_desde: Fecha de inicio del rango
            fecha_hasta: Fecha de fin del rango
            
        Returns:
            List[Proceso]: Lista de procesos con fecha límite en el rango
        """
        try:
            # Nota: Necesitaríamos agregar una columna fecha_limite en ProcesoORM
            # Por ahora, devolvemos todos los procesos
            return self.obtener_todos()
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos por fecha límite: {str(e)}")
    
    def obtener_procesos_activos(self) -> List[Proceso]:
        """
        Obtiene procesos que están activos (pendientes o en progreso).
        
        Returns:
            List[Proceso]: Lista de procesos activos
        """
        try:
            db_procesos = self.db.query(ProcesoORM).filter(
                or_(
                    ProcesoORM.estado == EstadoProceso.PENDIENTE.value,
                    ProcesoORM.estado == EstadoProceso.EN_PROGRESO.value
                )
            ).all()
            return [self._to_domain(p) for p in db_procesos]
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos activos: {str(e)}")
    
    def obtener_procesos_vencidos(self) -> List[Proceso]:
        """
        Obtiene procesos que están vencidos.
        
        Returns:
            List[Proceso]: Lista de procesos vencidos
        """
        try:
            # Nota: Necesitaríamos agregar una columna fecha_limite en ProcesoORM
            # Por ahora, devolvemos una lista vacía
            return []
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos vencidos: {str(e)}")
    
    def obtener_procesos_por_recurso(self, recurso_id: str) -> List[Proceso]:
        """
        Obtiene procesos que requieren un recurso específico.
        
        Args:
            recurso_id: ID del recurso requerido
            
        Returns:
            List[Proceso]: Lista de procesos que requieren el recurso
        """
        try:
            # Buscar en los recursos necesarios (JSON)
            db_procesos = self.db.query(ProcesoORM).filter(
                ProcesoORM.recursos_necesarios.contains(recurso_id)
            ).all()
            return [self._to_domain(p) for p in db_procesos]
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos por recurso: {str(e)}")
    
    def obtener_procesos_ejecutables(self) -> List[Proceso]:
        """
        Obtiene procesos que pueden ejecutarse (sin dependencias pendientes).
        
        Returns:
            List[Proceso]: Lista de procesos ejecutables
        """
        try:
            # Por simplicidad, devolvemos los procesos pendientes
            return self.obtener_por_estado(EstadoProceso.PENDIENTE)
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos ejecutables: {str(e)}")
    
    def actualizar_proceso(self, proceso: Proceso) -> Proceso:
        """
        Actualiza un proceso existente.
        
        Args:
            proceso: Proceso con los datos actualizados
            
        Returns:
            Proceso: Proceso actualizado
        """
        try:
            db_proceso = self.db.query(ProcesoORM).filter(ProcesoORM.codigo == proceso.id).first()
            
            if not db_proceso:
                raise ProcessNotFoundError(f"Proceso con ID {proceso.id} no encontrado")
            
            # Actualizar campos
            db_proceso.nombre = proceso.nombre
            db_proceso.descripcion = proceso.descripcion
            db_proceso.tiempo_estimado = proceso.tiempo_estimado_horas
            db_proceso.recursos_necesarios = json.dumps(proceso.recursos_requeridos) if proceso.recursos_requeridos else None
            db_proceso.prioridad = proceso.prioridad.value
            db_proceso.estado = proceso.estado.value
            db_proceso.fecha_actualizacion = func.now()
            
            self.db.commit()
            self.db.refresh(db_proceso)
            
            return self._to_domain(db_proceso)
            
        except ProcessNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Error al actualizar proceso: {str(e)}")
    
    def eliminar_proceso(self, proceso_id: str) -> bool:
        """
        Elimina un proceso del repositorio.
        
        Args:
            proceso_id: ID del proceso a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente
        """
        try:
            db_proceso = self.db.query(ProcesoORM).filter(ProcesoORM.codigo == proceso_id).first()
            
            if not db_proceso:
                raise ProcessNotFoundError(f"Proceso con ID {proceso_id} no encontrado")
            
            self.db.delete(db_proceso)
            self.db.commit()
            return True
            
        except ProcessNotFoundError:
            raise
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Error al eliminar proceso: {str(e)}")
    
    def buscar_procesos(self, criterios: Dict[str, Any]) -> List[Proceso]:
        """
        Busca procesos basándose en criterios específicos.
        
        Args:
            criterios: Diccionario con los criterios de búsqueda
            
        Returns:
            List[Proceso]: Lista de procesos que cumplen los criterios
        """
        try:
            query = self.db.query(ProcesoORM)
            
            # Aplicar filtros basados en criterios
            if 'nombre' in criterios:
                query = query.filter(ProcesoORM.nombre.contains(criterios['nombre']))
            
            if 'estado' in criterios:
                query = query.filter(ProcesoORM.estado == criterios['estado'])
            
            if 'prioridad' in criterios:
                query = query.filter(ProcesoORM.prioridad == criterios['prioridad'])
            
            db_procesos = query.all()
            return [self._to_domain(p) for p in db_procesos]
            
        except Exception as e:
            raise RepositoryError(f"Error al buscar procesos: {str(e)}")
    
    def contar_procesos(self, filtros: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número de procesos que cumplen los filtros.
        
        Args:
            filtros: Filtros opcionales para la cuenta
            
        Returns:
            int: Número de procesos que cumplen los filtros
        """
        try:
            query = self.db.query(ProcesoORM)
            
            if filtros:
                # Aplicar filtros
                if 'estado' in filtros:
                    query = query.filter(ProcesoORM.estado == filtros['estado'])
                
                if 'prioridad' in filtros:
                    query = query.filter(ProcesoORM.prioridad == filtros['prioridad'])
            
            return query.count()
            
        except Exception as e:
            raise RepositoryError(f"Error al contar procesos: {str(e)}")
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas generales de los procesos.
        
        Returns:
            Dict[str, Any]: Estadísticas de procesos
        """
        try:
            total = self.db.query(ProcesoORM).count()
            
            # Estadísticas por estado
            estados = self.db.query(ProcesoORM.estado, func.count(ProcesoORM.id)).group_by(ProcesoORM.estado).all()
            por_estado = {estado: count for estado, count in estados}
            
            # Estadísticas por prioridad
            prioridades = self.db.query(ProcesoORM.prioridad, func.count(ProcesoORM.id)).group_by(ProcesoORM.prioridad).all()
            por_prioridad = {prioridad: count for prioridad, count in prioridades}
            
            return {
                "total": total,
                "por_estado": por_estado,
                "por_prioridad": por_prioridad
            }
            
        except Exception as e:
            raise RepositoryError(f"Error al obtener estadísticas: {str(e)}")
    
    def obtener_procesos_paginados(self, pagina: int, tamaño: int) -> Dict[str, Any]:
        """
        Obtiene procesos con paginación.
        
        Args:
            pagina: Número de página (empezando en 1)
            tamaño: Tamaño de página
            
        Returns:
            Dict[str, Any]: Diccionario con procesos paginados
        """
        try:
            offset = (pagina - 1) * tamaño
            
            # Obtener procesos paginados
            db_procesos = self.db.query(ProcesoORM).offset(offset).limit(tamaño).all()
            procesos = [self._to_domain(p) for p in db_procesos]
            
            # Contar total
            total = self.db.query(ProcesoORM).count()
            paginas = (total + tamaño - 1) // tamaño  # Ceiling division
            
            return {
                "procesos": procesos,
                "pagina": pagina,
                "tamaño": tamaño,
                "total": total,
                "paginas": paginas
            }
            
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos paginados: {str(e)}")
    
    def crear_procesos_lote(self, procesos: List[Proceso]) -> List[Proceso]:
        """
        Crea múltiples procesos en una sola operación.
        
        Args:
            procesos: Lista de procesos a crear
            
        Returns:
            List[Proceso]: Lista de procesos creados
        """
        try:
            db_procesos = []
            
            for proceso in procesos:
                recursos_json = json.dumps(proceso.recursos_requeridos) if proceso.recursos_requeridos else None
                
                db_proceso = ProcesoORM(
                    codigo=proceso.id,
                    nombre=proceso.nombre,
                    descripcion=proceso.descripcion,
                    tiempo_estimado=proceso.tiempo_estimado_horas,
                    recursos_necesarios=recursos_json,
                    prioridad=proceso.prioridad.value,
                    estado=proceso.estado.value
                )
                
                db_procesos.append(db_proceso)
            
            self.db.add_all(db_procesos)
            self.db.commit()
            
            # Refresh all objects
            for db_proceso in db_procesos:
                self.db.refresh(db_proceso)
            
            return [self._to_domain(p) for p in db_procesos]
            
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Error al crear procesos en lote: {str(e)}")
    
    def actualizar_procesos_lote(self, procesos: List[Proceso]) -> List[Proceso]:
        """
        Actualiza múltiples procesos en una sola operación.
        
        Args:
            procesos: Lista de procesos a actualizar
            
        Returns:
            List[Proceso]: Lista de procesos actualizados
        """
        try:
            procesos_actualizados = []
            
            for proceso in procesos:
                db_proceso = self.db.query(ProcesoORM).filter(ProcesoORM.codigo == proceso.id).first()
                
                if db_proceso:
                    db_proceso.nombre = proceso.nombre
                    db_proceso.descripcion = proceso.descripcion
                    db_proceso.tiempo_estimado = proceso.tiempo_estimado_horas
                    db_proceso.recursos_necesarios = json.dumps(proceso.recursos_requeridos) if proceso.recursos_requeridos else None
                    db_proceso.prioridad = proceso.prioridad.value
                    db_proceso.estado = proceso.estado.value
                    db_proceso.fecha_actualizacion = func.now()
                    
                    procesos_actualizados.append(db_proceso)
            
            self.db.commit()
            
            # Refresh all objects
            for db_proceso in procesos_actualizados:
                self.db.refresh(db_proceso)
            
            return [self._to_domain(p) for p in procesos_actualizados]
            
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Error al actualizar procesos en lote: {str(e)}")
    
    def eliminar_procesos_lote(self, proceso_ids: List[str]) -> bool:
        """
        Elimina múltiples procesos en una sola operación.
        
        Args:
            proceso_ids: Lista de IDs de procesos a eliminar
            
        Returns:
            bool: True si se eliminaron todos exitosamente
        """
        try:
            deleted_count = self.db.query(ProcesoORM).filter(
                ProcesoORM.codigo.in_(proceso_ids)
            ).delete(synchronize_session=False)
            
            self.db.commit()
            
            # Verificar que se eliminaron todos
            return deleted_count == len(proceso_ids)
            
        except Exception as e:
            self.db.rollback()
            raise RepositoryError(f"Error al eliminar procesos en lote: {str(e)}")
    
    def existe_proceso(self, proceso_id: str) -> bool:
        """
        Verifica si existe un proceso con el ID especificado.
        
        Args:
            proceso_id: ID del proceso a verificar
            
        Returns:
            bool: True si el proceso existe
        """
        try:
            return self.db.query(ProcesoORM).filter(ProcesoORM.codigo == proceso_id).first() is not None
        except Exception as e:
            raise RepositoryError(f"Error al verificar existencia del proceso: {str(e)}")
    
    def obtener_procesos_relacionados(self, proceso_id: str) -> List[Proceso]:
        """
        Obtiene procesos relacionados (dependencias y dependientes).
        
        Args:
            proceso_id: ID del proceso base
            
        Returns:
            List[Proceso]: Lista de procesos relacionados
        """
        try:
            # Nota: Necesitaríamos una tabla de relaciones para implementar esto completamente
            # Por ahora, devolvemos una lista vacía
            return []
        except Exception as e:
            raise RepositoryError(f"Error al obtener procesos relacionados: {str(e)}")
    
    def obtener_dependencias(self, proceso_id: str) -> List[Proceso]:
        """
        Obtiene las dependencias de un proceso.
        
        Args:
            proceso_id: ID del proceso
            
        Returns:
            List[Proceso]: Lista de procesos de los que depende
        """
        try:
            # Nota: Necesitaríamos una tabla de dependencias para implementar esto completamente
            # Por ahora, devolvemos una lista vacía
            return []
        except Exception as e:
            raise RepositoryError(f"Error al obtener dependencias: {str(e)}")
    
    def obtener_dependientes(self, proceso_id: str) -> List[Proceso]:
        """
        Obtiene los procesos que dependen de un proceso específico.
        
        Args:
            proceso_id: ID del proceso
            
        Returns:
            List[Proceso]: Lista de procesos que dependen de este
        """
        try:
            # Nota: Necesitaríamos una tabla de dependencias para implementar esto completamente
            # Por ahora, devolvemos una lista vacía
            return []
        except Exception as e:
            raise RepositoryError(f"Error al obtener dependientes: {str(e)}")
    
    # Métodos heredados del repositorio anterior para compatibilidad
    def save(self, proceso: Proceso) -> Proceso:
        """Método de compatibilidad - alias para crear_proceso"""
        return self.crear_proceso(proceso)
    
    def find_by_id(self, proceso_id: int) -> Optional[Proceso]:
        """Método de compatibilidad - buscar por ID numérico"""
        return self.obtener_por_id(str(proceso_id))
    
    def find_by_codigo(self, codigo: str) -> Optional[Proceso]:
        """Método de compatibilidad - buscar por código"""
        return self.obtener_por_id(codigo)
    
    def find_all(self) -> List[Proceso]:
        """Método de compatibilidad - obtener todos"""
        return self.obtener_todos()
    
    def find_by_prioridad(self, prioridad: NivelPrioridad) -> List[Proceso]:
        """Método de compatibilidad - buscar por prioridad"""
        return self.obtener_por_prioridad(prioridad)
    
    def find_by_estado(self, estado: EstadoProceso) -> List[Proceso]:
        """Método de compatibilidad - buscar por estado"""
        return self.obtener_por_estado(estado)
    
    def delete(self, proceso_id: int) -> bool:
        """Método de compatibilidad - eliminar por ID numérico"""
        return self.eliminar_proceso(str(proceso_id))
    
    def count(self) -> int:
        """Método de compatibilidad - contar todos"""
        return self.contar_procesos()
    
    def _to_domain(self, db_proceso: ProcesoORM) -> Proceso:
        """
        Convertir modelo ORM a entidad de dominio
        
        Args:
            db_proceso: Proceso ORM
            
        Returns:
            Proceso de dominio
        """
        recursos_necesarios = []
        if db_proceso.recursos_necesarios:
            try:
                recursos_necesarios = json.loads(db_proceso.recursos_necesarios)
            except json.JSONDecodeError:
                recursos_necesarios = []
        
        # Convertir prioridad - si es string, convertir a int primero
        prioridad_value = db_proceso.prioridad
        if isinstance(prioridad_value, str):
            try:
                prioridad_value = int(prioridad_value)
            except ValueError:
                # Si no se puede convertir, usar valor por defecto
                prioridad_value = NivelPrioridad.MEDIA.value
        
        # Crear proceso con el ID correcto
        proceso = Proceso(
            nombre=db_proceso.nombre,
            descripcion=db_proceso.descripcion,
            tipo=TipoProceso.RUTINARIO,  # Valor por defecto ya que no está en la BD
            tiempo_estimado_horas=db_proceso.tiempo_estimado,
            prioridad=NivelPrioridad(prioridad_value),
            recursos_requeridos=recursos_necesarios,
            estado=EstadoProceso(db_proceso.estado)
        )
        
        # Establecer el ID del proceso al código almacenado
        proceso.id = db_proceso.codigo
        
        return proceso
