"""
Caso de Uso: Calcular Capacidad Semanal

Este módulo implementa la lógica para calcular cuántos procesos
pueden ejecutarse por semana basándose en los recursos disponibles,
las horas de trabajo y las restricciones del sistema.

Principios SOLID aplicados:
- Single Responsibility: Solo se encarga del cálculo de capacidad
- Open/Closed: Extensible para nuevos tipos de cálculo
- Dependency Inversion: Depende de abstracciones, no de implementaciones

Autor: Equipo de Desarrollo
Fecha: 2025-07-07
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from domain.models.proceso import Proceso
from domain.models.recurso import Recurso
from domain.repositories.proceso_repository import ProcesoRepository


# Configuración de logging
logger = logging.getLogger(__name__)


@dataclass
class CapacidadSemanalRequest:
    """
    Datos de entrada para el cálculo de capacidad semanal.
    
    Attributes:
        fecha_inicio: Fecha de inicio de la semana a planificar
        fecha_fin: Fecha de fin de la semana a planificar
        recursos_disponibles: Lista de recursos disponibles
        restricciones: Restricciones adicionales del sistema
    """
    fecha_inicio: datetime
    fecha_fin: datetime
    recursos_disponibles: List[Recurso]
    restricciones: Optional[Dict] = None


@dataclass
class CapacidadSemanalResponse:
    """
    Resultado del cálculo de capacidad semanal.
    
    Attributes:
        total_procesos_posibles: Número total de procesos que pueden ejecutarse
        capacidad_por_recurso: Capacidad individual de cada recurso
        tiempo_total_disponible: Tiempo total disponible en horas
        tiempo_total_requerido: Tiempo total requerido para todos los procesos
        eficiencia_proyectada: Porcentaje de eficiencia esperado
        recomendaciones: Lista de recomendaciones para optimizar
    """
    total_procesos_posibles: int
    capacidad_por_recurso: Dict[str, int]
    tiempo_total_disponible: float
    tiempo_total_requerido: float
    eficiencia_proyectada: float
    recomendaciones: List[str]


class CalcularCapacidadSemanal:
    """
    Caso de uso para calcular la capacidad semanal de procesamiento.
    
    Este caso de uso implementa el algoritmo principal para determinar
    cuántos procesos pueden ejecutarse en una semana específica,
    considerando los recursos disponibles y las restricciones del sistema.
    """
    
    def __init__(self, proceso_repository: ProcesoRepository):
        """
        Inicializa el caso de uso con las dependencias necesarias.
        
        Args:
            proceso_repository: Repositorio para acceder a los datos de procesos
        """
        self._proceso_repository = proceso_repository
        self._logger = logging.getLogger(self.__class__.__name__)
        
    def execute(self, request: CapacidadSemanalRequest) -> CapacidadSemanalResponse:
        """
        Ejecuta el cálculo de capacidad semanal.
        
        Args:
            request: Datos de entrada para el cálculo
            
        Returns:
            CapacidadSemanalResponse: Resultado del cálculo
            
        Raises:
            ValueError: Si los datos de entrada son inválidos
            RuntimeError: Si ocurre un error durante el cálculo
        """
        try:
            self._logger.info(f"Iniciando cálculo de capacidad semanal para {request.fecha_inicio} - {request.fecha_fin}")
            
            # Validar entrada
            self._validar_entrada(request)
            
            # Obtener procesos disponibles
            procesos = self._obtener_procesos_disponibles(request)
            
            # Calcular tiempo total disponible
            tiempo_disponible = self._calcular_tiempo_disponible(request)
            
            # Calcular capacidad por recurso
            capacidad_por_recurso = self._calcular_capacidad_por_recurso(
                request.recursos_disponibles, 
                procesos, 
                tiempo_disponible
            )
            
            # Calcular total de procesos posibles
            total_procesos = self._calcular_total_procesos_posibles(
                capacidad_por_recurso, 
                procesos
            )
            
            # Calcular tiempo requerido
            tiempo_requerido = self._calcular_tiempo_requerido(procesos, total_procesos)
            
            # Calcular eficiencia proyectada
            eficiencia = self._calcular_eficiencia_proyectada(
                tiempo_disponible, 
                tiempo_requerido
            )
            
            # Generar recomendaciones
            recomendaciones = self._generar_recomendaciones(
                request, 
                capacidad_por_recurso, 
                eficiencia
            )
            
            # Crear respuesta
            response = CapacidadSemanalResponse(
                total_procesos_posibles=total_procesos,
                capacidad_por_recurso=capacidad_por_recurso,
                tiempo_total_disponible=tiempo_disponible,
                tiempo_total_requerido=tiempo_requerido,
                eficiencia_proyectada=eficiencia,
                recomendaciones=recomendaciones
            )
            
            self._logger.info(f"Cálculo completado: {total_procesos} procesos posibles")
            return response
            
        except Exception as e:
            self._logger.error(f"Error en cálculo de capacidad: {str(e)}")
            raise RuntimeError(f"Error calculando capacidad semanal: {str(e)}")
    
    def _validar_entrada(self, request: CapacidadSemanalRequest) -> None:
        """
        Valida los datos de entrada del caso de uso.
        
        Args:
            request: Datos de entrada a validar
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        if request.fecha_inicio >= request.fecha_fin:
            raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        if not request.recursos_disponibles:
            raise ValueError("Debe haber al menos un recurso disponible")
        
        # Validar que las fechas no sean en el pasado
        if request.fecha_inicio < datetime.now().date():
            raise ValueError("Las fechas de planificación no pueden ser en el pasado")
    
    def _obtener_procesos_disponibles(self, request: CapacidadSemanalRequest) -> List[Proceso]:
        """
        Obtiene los procesos disponibles para el período especificado.
        
        Args:
            request: Datos de entrada con el período
            
        Returns:
            List[Proceso]: Lista de procesos disponibles
        """
        try:
            procesos = self._proceso_repository.obtener_procesos_activos()
            self._logger.debug(f"Obtenidos {len(procesos)} procesos activos")
            return procesos
        except Exception as e:
            self._logger.error(f"Error obteniendo procesos: {str(e)}")
            raise
    
    def _calcular_tiempo_disponible(self, request: CapacidadSemanalRequest) -> float:
        """
        Calcula el tiempo total disponible en horas para el período.
        
        Args:
            request: Datos de entrada con recursos y fechas
            
        Returns:
            float: Tiempo total disponible en horas
        """
        dias_laborables = self._calcular_dias_laborables(
            request.fecha_inicio, 
            request.fecha_fin
        )
        
        tiempo_total = 0.0
        for recurso in request.recursos_disponibles:
            # Asumimos 8 horas laborables por día por recurso
            tiempo_recurso = dias_laborables * recurso.horas_disponibles_dia
            tiempo_total += tiempo_recurso
        
        self._logger.debug(f"Tiempo total disponible: {tiempo_total} horas")
        return tiempo_total
    
    def _calcular_dias_laborables(self, fecha_inicio: datetime, fecha_fin: datetime) -> int:
        """
        Calcula el número de días laborables entre dos fechas.
        
        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            
        Returns:
            int: Número de días laborables
        """
        dias_laborables = 0
        fecha_actual = fecha_inicio
        
        while fecha_actual < fecha_fin:
            # Lunes=0, Domingo=6
            if fecha_actual.weekday() < 5:  # Lunes a Viernes
                dias_laborables += 1
            fecha_actual += timedelta(days=1)
        
        return dias_laborables
    
    def _calcular_capacidad_por_recurso(self, 
                                       recursos: List[Recurso], 
                                       procesos: List[Proceso], 
                                       tiempo_disponible: float) -> Dict[str, int]:
        """
        Calcula la capacidad individual de cada recurso.
        
        Args:
            recursos: Lista de recursos disponibles
            procesos: Lista de procesos a ejecutar
            tiempo_disponible: Tiempo total disponible
            
        Returns:
            Dict[str, int]: Capacidad de cada recurso
        """
        capacidad_por_recurso = {}
        
        for recurso in recursos:
            # Calcular tiempo disponible del recurso
            tiempo_recurso = recurso.horas_disponibles_dia * self._calcular_dias_laborables(
                datetime.now(), 
                datetime.now() + timedelta(days=7)
            )
            
            # Calcular cuántos procesos puede manejar
            if procesos:
                tiempo_promedio_proceso = sum(p.tiempo_estimado_horas for p in procesos) / len(procesos)
                capacidad = int(tiempo_recurso / tiempo_promedio_proceso)
            else:
                capacidad = 0
            
            capacidad_por_recurso[recurso.nombre] = capacidad
        
        return capacidad_por_recurso
    
    def _calcular_total_procesos_posibles(self, 
                                         capacidad_por_recurso: Dict[str, int], 
                                         procesos: List[Proceso]) -> int:
        """
        Calcula el total de procesos posibles basándose en la capacidad de recursos.
        
        Args:
            capacidad_por_recurso: Capacidad de cada recurso
            procesos: Lista de procesos disponibles
            
        Returns:
            int: Total de procesos posibles
        """
        if not capacidad_por_recurso:
            return 0
        
        # El total está limitado por el recurso con menor capacidad
        total_procesos = sum(capacidad_por_recurso.values())
        
        # Aplicar restricciones adicionales si existen
        if procesos:
            # Limitar por la disponibilidad de procesos
            total_procesos = min(total_procesos, len(procesos))
        
        return total_procesos
    
    def _calcular_tiempo_requerido(self, procesos: List[Proceso], total_procesos: int) -> float:
        """
        Calcula el tiempo total requerido para ejecutar los procesos.
        
        Args:
            procesos: Lista de procesos
            total_procesos: Número total de procesos a ejecutar
            
        Returns:
            float: Tiempo total requerido en horas
        """
        if not procesos or total_procesos == 0:
            return 0.0
        
        tiempo_promedio = sum(p.tiempo_estimado_horas for p in procesos) / len(procesos)
        return tiempo_promedio * total_procesos
    
    def _calcular_eficiencia_proyectada(self, 
                                       tiempo_disponible: float, 
                                       tiempo_requerido: float) -> float:
        """
        Calcula la eficiencia proyectada del sistema.
        
        Args:
            tiempo_disponible: Tiempo total disponible
            tiempo_requerido: Tiempo total requerido
            
        Returns:
            float: Eficiencia proyectada (0-100%)
        """
        if tiempo_disponible == 0:
            return 0.0
        
        eficiencia = (tiempo_requerido / tiempo_disponible) * 100
        return min(eficiencia, 100.0)  # Máximo 100%
    
    def _generar_recomendaciones(self, 
                                request: CapacidadSemanalRequest,
                                capacidad_por_recurso: Dict[str, int],
                                eficiencia: float) -> List[str]:
        """
        Genera recomendaciones para optimizar la capacidad.
        
        Args:
            request: Datos de entrada originales
            capacidad_por_recurso: Capacidad por recurso
            eficiencia: Eficiencia proyectada
            
        Returns:
            List[str]: Lista de recomendaciones
        """
        recomendaciones = []
        
        # Recomendaciones basadas en eficiencia
        if eficiencia < 50:
            recomendaciones.append("Considere agregar más recursos o extender el período de planificación")
        elif eficiencia > 90:
            recomendaciones.append("Excelente utilización de recursos. Considere planificar procesos adicionales")
        
        # Recomendaciones basadas en distribución de recursos
        if capacidad_por_recurso:
            capacidades = list(capacidad_por_recurso.values())
            if max(capacidades) - min(capacidades) > 5:
                recomendaciones.append("Considere rebalancear la carga entre recursos para mejor eficiencia")
        
        # Recomendaciones generales
        if len(request.recursos_disponibles) < 3:
            recomendaciones.append("Considere diversificar los recursos para reducir riesgos")
        
        return recomendaciones
