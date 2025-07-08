"""
Caso de Uso: Distribuir Recursos

Este módulo implementa la lógica para distribuir recursos de manera óptima
entre los procesos disponibles, maximizando la eficiencia y minimizando
los costos mientras se respetan las restricciones del sistema.

Principios SOLID aplicados:
- Single Responsibility: Solo se encarga de la distribución de recursos
- Open/Closed: Extensible para nuevos algoritmos de distribución
- Dependency Inversion: Depende de abstracciones, no de implementaciones

Autor: Equipo de Desarrollo
Fecha: 2025-07-07
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
from enum import Enum

from domain.models.proceso import Proceso, EstadoProceso, NivelPrioridad
from domain.models.recurso import Recurso, EstadoRecurso, TipoRecurso
from domain.repositories.proceso_repository import ProcesoRepository


# Configuración de logging
logger = logging.getLogger(__name__)


class EstrategiaDistribucion(Enum):
    """
    Enumeración de estrategias de distribución de recursos.
    
    Estrategias:
        PRIORIDAD: Distribución basada en prioridad de procesos
        EFICIENCIA: Distribución para maximizar eficiencia
        COSTO_MINIMO: Distribución para minimizar costos
        TIEMPO_MINIMO: Distribución para minimizar tiempo total
        BALANCEADA: Distribución balanceada entre múltiples criterios
    """
    PRIORIDAD = "prioridad"
    EFICIENCIA = "eficiencia"
    COSTO_MINIMO = "costo_minimo"
    TIEMPO_MINIMO = "tiempo_minimo"
    BALANCEADA = "balanceada"


@dataclass
class RestriccionDistribucion:
    """
    Restricciones para la distribución de recursos.
    
    Attributes:
        max_procesos_por_recurso: Máximo número de procesos por recurso
        max_horas_por_recurso: Máximo horas de trabajo por recurso
        recursos_obligatorios: Recursos que deben usarse obligatoriamente
        recursos_prohibidos: Recursos que no pueden usarse
        procesos_prioritarios: Procesos que tienen prioridad absoluta
        tiempo_limite: Tiempo límite para completar todos los procesos
    """
    max_procesos_por_recurso: Optional[int] = None
    max_horas_por_recurso: Optional[float] = None
    recursos_obligatorios: Optional[List[str]] = None
    recursos_prohibidos: Optional[List[str]] = None
    procesos_prioritarios: Optional[List[str]] = None
    tiempo_limite: Optional[datetime] = None
    
    def __post_init__(self):
        """Inicializa listas vacías si son None."""
        if self.recursos_obligatorios is None:
            self.recursos_obligatorios = []
        if self.recursos_prohibidos is None:
            self.recursos_prohibidos = []
        if self.procesos_prioritarios is None:
            self.procesos_prioritarios = []


@dataclass
class AsignacionRecurso:
    """
    Representa una asignación de recurso a proceso.
    
    Attributes:
        proceso_id: ID del proceso asignado
        recurso_id: ID del recurso asignado
        horas_asignadas: Horas de recurso asignadas
        fecha_inicio: Fecha de inicio de la asignación
        fecha_fin: Fecha de fin de la asignación
        prioridad: Prioridad de la asignación
        costo_estimado: Costo estimado de la asignación
    """
    proceso_id: str
    recurso_id: str
    horas_asignadas: float
    fecha_inicio: datetime
    fecha_fin: datetime
    prioridad: int
    costo_estimado: float


@dataclass
class DistribucionRecursosRequest:
    """
    Datos de entrada para la distribución de recursos.
    
    Attributes:
        procesos: Lista de procesos a asignar
        recursos: Lista de recursos disponibles
        estrategia: Estrategia de distribución a usar
        restricciones: Restricciones para la distribución
        fecha_inicio: Fecha de inicio de la planificación
        optimizar_costos: Si se debe optimizar por costos
        optimizar_tiempo: Si se debe optimizar por tiempo
    """
    procesos: List[Proceso]
    recursos: List[Recurso]
    estrategia: EstrategiaDistribucion
    restricciones: Optional[RestriccionDistribucion] = None
    fecha_inicio: Optional[datetime] = None
    optimizar_costos: bool = True
    optimizar_tiempo: bool = True
    
    def __post_init__(self):
        """Inicializa valores por defecto."""
        if self.fecha_inicio is None:
            self.fecha_inicio = datetime.now()
        if self.restricciones is None:
            self.restricciones = RestriccionDistribucion()


@dataclass
class DistribucionRecursosResponse:
    """
    Resultado de la distribución de recursos.
    
    Attributes:
        asignaciones: Lista de asignaciones realizadas
        procesos_asignados: Número de procesos asignados
        procesos_sin_asignar: Lista de procesos sin asignar
        recursos_utilizados: Número de recursos utilizados
        eficiencia_estimada: Eficiencia estimada del plan
        costo_total: Costo total estimado
        tiempo_total: Tiempo total estimado
        recomendaciones: Lista de recomendaciones
        metricas: Métricas adicionales del plan
    """
    asignaciones: List[AsignacionRecurso]
    procesos_asignados: int
    procesos_sin_asignar: List[Proceso]
    recursos_utilizados: int
    eficiencia_estimada: float
    costo_total: float
    tiempo_total: float
    recomendaciones: List[str]
    metricas: Dict[str, float]


class DistribuirRecursos:
    """
    Caso de uso para distribuir recursos entre procesos.
    
    Implementa diferentes estrategias de distribución para asignar
    recursos a procesos de manera óptima según los criterios establecidos.
    """
    
    def __init__(self, proceso_repository: ProcesoRepository):
        """
        Inicializa el caso de uso con las dependencias necesarias.
        
        Args:
            proceso_repository: Repositorio para acceder a los datos de procesos
        """
        self._proceso_repository = proceso_repository
        self._logger = logging.getLogger(self.__class__.__name__)
    
    def execute(self, request: DistribucionRecursosRequest) -> DistribucionRecursosResponse:
        """
        Ejecuta la distribución de recursos.
        
        Args:
            request: Datos de entrada para la distribución
            
        Returns:
            DistribucionRecursosResponse: Resultado de la distribución
            
        Raises:
            ValueError: Si los datos de entrada son inválidos
            RuntimeError: Si ocurre un error durante la distribución
        """
        try:
            self._logger.info(f"Iniciando distribución de recursos con estrategia {request.estrategia.value}")
            
            # Validar entrada
            self._validar_entrada(request)
            
            # Filtrar recursos disponibles
            recursos_disponibles = self._filtrar_recursos_disponibles(request)
            
            # Ordenar procesos según la estrategia
            procesos_ordenados = self._ordenar_procesos(request)
            
            # Ejecutar distribución según la estrategia
            asignaciones = self._ejecutar_distribucion(
                procesos_ordenados,
                recursos_disponibles,
                request
            )
            
            # Calcular métricas
            metricas = self._calcular_metricas(asignaciones, request)
            
            # Identificar procesos sin asignar
            procesos_sin_asignar = self._identificar_procesos_sin_asignar(
                request.procesos,
                asignaciones
            )
            
            # Generar recomendaciones
            recomendaciones = self._generar_recomendaciones(
                asignaciones,
                procesos_sin_asignar,
                recursos_disponibles,
                request
            )
            
            # Crear respuesta
            response = DistribucionRecursosResponse(
                asignaciones=asignaciones,
                procesos_asignados=len(asignaciones),
                procesos_sin_asignar=procesos_sin_asignar,
                recursos_utilizados=len(set(a.recurso_id for a in asignaciones)),
                eficiencia_estimada=metricas.get("eficiencia", 0.0),
                costo_total=metricas.get("costo_total", 0.0),
                tiempo_total=metricas.get("tiempo_total", 0.0),
                recomendaciones=recomendaciones,
                metricas=metricas
            )
            
            self._logger.info(f"Distribución completada: {len(asignaciones)} asignaciones realizadas")
            return response
            
        except Exception as e:
            self._logger.error(f"Error en distribución de recursos: {str(e)}")
            raise RuntimeError(f"Error distribuyendo recursos: {str(e)}")
    
    def _validar_entrada(self, request: DistribucionRecursosRequest) -> None:
        """
        Valida los datos de entrada del caso de uso.
        
        Args:
            request: Datos de entrada a validar
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        if not request.procesos:
            raise ValueError("Debe haber al menos un proceso para distribuir")
        
        if not request.recursos:
            raise ValueError("Debe haber al menos un recurso disponible")
        
        # Validar que los procesos estén en estado válido
        for proceso in request.procesos:
            if proceso.estado not in [EstadoProceso.PENDIENTE]:
                raise ValueError(f"El proceso {proceso.nombre} no está en estado válido para distribución")
        
        # Validar restricciones
        if request.restricciones:
            self._validar_restricciones(request.restricciones)
    
    def _validar_restricciones(self, restricciones: RestriccionDistribucion) -> None:
        """
        Valida las restricciones de distribución.
        
        Args:
            restricciones: Restricciones a validar
            
        Raises:
            ValueError: Si las restricciones son inválidas
        """
        if restricciones.max_procesos_por_recurso is not None:
            if restricciones.max_procesos_por_recurso <= 0:
                raise ValueError("El máximo de procesos por recurso debe ser mayor a 0")
        
        if restricciones.max_horas_por_recurso is not None:
            if restricciones.max_horas_por_recurso <= 0:
                raise ValueError("El máximo de horas por recurso debe ser mayor a 0")
    
    def _filtrar_recursos_disponibles(self, request: DistribucionRecursosRequest) -> List[Recurso]:
        """
        Filtra los recursos disponibles según las restricciones.
        
        Args:
            request: Datos de entrada con recursos y restricciones
            
        Returns:
            List[Recurso]: Lista de recursos disponibles
        """
        recursos_disponibles = []
        
        for recurso in request.recursos:
            # Verificar que el recurso esté disponible
            if not recurso.esta_disponible():
                continue
            
            # Verificar restricciones
            if request.restricciones:
                # Recursos prohibidos
                if (request.restricciones.recursos_prohibidos and 
                    recurso.id in request.restricciones.recursos_prohibidos):
                    continue
                
                # Recursos obligatorios (si se especifican, solo usar esos)
                if (request.restricciones.recursos_obligatorios and 
                    recurso.id not in request.restricciones.recursos_obligatorios):
                    continue
            
            recursos_disponibles.append(recurso)
        
        return recursos_disponibles
    
    def _ordenar_procesos(self, request: DistribucionRecursosRequest) -> List[Proceso]:
        """
        Ordena los procesos según la estrategia de distribución.
        
        Args:
            request: Datos de entrada con procesos y estrategia
            
        Returns:
            List[Proceso]: Lista de procesos ordenados
        """
        procesos = request.procesos.copy()
        
        # Procesos prioritarios primero
        if request.restricciones and request.restricciones.procesos_prioritarios:
            procesos_prioritarios = [p for p in procesos if p.id in request.restricciones.procesos_prioritarios]
            procesos_normales = [p for p in procesos if p.id not in request.restricciones.procesos_prioritarios]
            procesos = procesos_prioritarios + procesos_normales
        
        # Ordenar según estrategia
        if request.estrategia == EstrategiaDistribucion.PRIORIDAD:
            procesos.sort(key=lambda p: p.prioridad.value, reverse=True)
        elif request.estrategia == EstrategiaDistribucion.TIEMPO_MINIMO:
            procesos.sort(key=lambda p: p.tiempo_estimado_horas)
        elif request.estrategia == EstrategiaDistribucion.COSTO_MINIMO:
            # Ordenar por procesos que requieren recursos más baratos
            procesos.sort(key=lambda p: self._calcular_costo_estimado_proceso(p, request.recursos))
        elif request.estrategia == EstrategiaDistribucion.EFICIENCIA:
            # Ordenar por eficiencia estimada (tiempo/recursos)
            procesos.sort(key=lambda p: p.tiempo_estimado_horas / len(p.recursos_requeridos) if p.recursos_requeridos else p.tiempo_estimado_horas)
        
        return procesos
    
    def _calcular_costo_estimado_proceso(self, proceso: Proceso, recursos: List[Recurso]) -> float:
        """
        Calcula el costo estimado de un proceso.
        
        Args:
            proceso: Proceso a evaluar
            recursos: Lista de recursos disponibles
            
        Returns:
            float: Costo estimado del proceso
        """
        if not proceso.recursos_requeridos:
            # Si no especifica recursos, usar el más barato
            costos = [r.costo_por_hora for r in recursos if r.costo_por_hora > 0]
            costo_minimo = min(costos) if costos else 0
            return proceso.tiempo_estimado_horas * costo_minimo
        
        # Calcular con recursos específicos
        costo_total = 0
        for recurso_req in proceso.recursos_requeridos:
            recursos_compatibles = [r for r in recursos if r.nombre == recurso_req or recurso_req in r.habilidades]
            if recursos_compatibles:
                costo_minimo = min(r.costo_por_hora for r in recursos_compatibles)
                costo_total += proceso.tiempo_estimado_horas * costo_minimo
        
        return costo_total
    
    def _ejecutar_distribucion(self, 
                              procesos: List[Proceso], 
                              recursos: List[Recurso], 
                              request: DistribucionRecursosRequest) -> List[AsignacionRecurso]:
        """
        Ejecuta la distribución de recursos usando la estrategia seleccionada.
        
        Args:
            procesos: Lista de procesos ordenados
            recursos: Lista de recursos disponibles
            request: Datos de entrada
            
        Returns:
            List[AsignacionRecurso]: Lista de asignaciones realizadas
        """
        asignaciones = []
        recursos_ocupados = {r.id: 0.0 for r in recursos}  # Horas ocupadas por recurso
        
        for proceso in procesos:
            # Encontrar el mejor recurso para este proceso
            recurso_asignado = self._encontrar_mejor_recurso(
                proceso,
                recursos,
                recursos_ocupados,
                request
            )
            
            if recurso_asignado:
                # Crear asignación
                asignacion = self._crear_asignacion(
                    proceso,
                    recurso_asignado,
                    request.fecha_inicio or datetime.now(),
                    recursos_ocupados[recurso_asignado.id]
                )
                
                asignaciones.append(asignacion)
                
                # Actualizar recurso ocupado
                recursos_ocupados[recurso_asignado.id] += proceso.tiempo_estimado_horas
                
                self._logger.debug(f"Proceso {proceso.nombre} asignado a recurso {recurso_asignado.nombre}")
        
        return asignaciones
    
    def _encontrar_mejor_recurso(self, 
                                proceso: Proceso, 
                                recursos: List[Recurso], 
                                recursos_ocupados: Dict[str, float],
                                request: DistribucionRecursosRequest) -> Optional[Recurso]:
        """
        Encuentra el mejor recurso para un proceso dado.
        
        Args:
            proceso: Proceso a asignar
            recursos: Lista de recursos disponibles
            recursos_ocupados: Horas ocupadas por recurso
            request: Datos de entrada
            
        Returns:
            Optional[Recurso]: Mejor recurso encontrado o None
        """
        candidatos = []
        
        for recurso in recursos:
            # Verificar disponibilidad
            if not self._puede_asignar_recurso(recurso, proceso, recursos_ocupados, request):
                continue
            
            # Calcular puntuación del recurso
            puntuacion = self._calcular_puntuacion_recurso(recurso, proceso, request)
            candidatos.append((recurso, puntuacion))
        
        if not candidatos:
            return None
        
        # Ordenar por puntuación (mayor es mejor)
        candidatos.sort(key=lambda x: x[1], reverse=True)
        return candidatos[0][0]
    
    def _puede_asignar_recurso(self, 
                              recurso: Recurso, 
                              proceso: Proceso, 
                              recursos_ocupados: Dict[str, float],
                              request: DistribucionRecursosRequest) -> bool:
        """
        Verifica si un recurso puede ser asignado a un proceso.
        
        Args:
            recurso: Recurso a evaluar
            proceso: Proceso a asignar
            recursos_ocupados: Horas ocupadas por recurso
            request: Datos de entrada
            
        Returns:
            bool: True si el recurso puede ser asignado
        """
        # Verificar restricciones de horas
        if request.restricciones and request.restricciones.max_horas_por_recurso:
            horas_actuales = recursos_ocupados.get(recurso.id, 0)
            if horas_actuales + proceso.tiempo_estimado_horas > request.restricciones.max_horas_por_recurso:
                return False
        
        # Verificar capacidad del recurso
        if not recurso.puede_asignarse(proceso.tiempo_estimado_horas):
            return False
        
        # Verificar compatibilidad de habilidades
        if proceso.recursos_requeridos:
            if not any(req in recurso.habilidades or req == recurso.nombre for req in proceso.recursos_requeridos):
                return False
        
        return True
    
    def _calcular_puntuacion_recurso(self, 
                                    recurso: Recurso, 
                                    proceso: Proceso, 
                                    request: DistribucionRecursosRequest) -> float:
        """
        Calcula la puntuación de un recurso para un proceso.
        
        Args:
            recurso: Recurso a evaluar
            proceso: Proceso a asignar
            request: Datos de entrada
            
        Returns:
            float: Puntuación del recurso (mayor es mejor)
        """
        puntuacion = 0.0
        
        # Puntuación base por disponibilidad
        puntuacion += recurso.porcentaje_utilizacion * 0.1
        
        # Puntuación por compatibilidad de habilidades
        if proceso.recursos_requeridos:
            habilidades_compatibles = sum(1 for req in proceso.recursos_requeridos 
                                        if req in recurso.habilidades or req == recurso.nombre)
            puntuacion += habilidades_compatibles * 10
        
        # Ajustar según estrategia
        if request.estrategia == EstrategiaDistribucion.COSTO_MINIMO:
            # Preferir recursos más baratos
            puntuacion += max(0, 100 - recurso.costo_por_hora)
        elif request.estrategia == EstrategiaDistribucion.EFICIENCIA:
            # Preferir recursos con mayor capacidad disponible
            puntuacion += recurso.capacidad_disponible
        elif request.estrategia == EstrategiaDistribucion.PRIORIDAD:
            # Preferir recursos de mayor calidad para procesos prioritarios
            if proceso.prioridad.value >= 8:
                puntuacion += 50 if recurso.experiencia else 0
        
        return puntuacion
    
    def _crear_asignacion(self, 
                         proceso: Proceso, 
                         recurso: Recurso, 
                         fecha_inicio_base: datetime,
                         horas_ocupadas: float) -> AsignacionRecurso:
        """
        Crea una asignación de recurso a proceso.
        
        Args:
            proceso: Proceso a asignar
            recurso: Recurso asignado
            fecha_inicio_base: Fecha base de inicio
            horas_ocupadas: Horas ya ocupadas del recurso
            
        Returns:
            AsignacionRecurso: Asignación creada
        """
        # Calcular fechas considerando horas ocupadas
        from datetime import timedelta
        
        # Calcular inicio considerando trabajo previo
        dias_trabajo_previo = horas_ocupadas / recurso.horas_disponibles_dia
        fecha_inicio = fecha_inicio_base + timedelta(days=int(dias_trabajo_previo))
        
        # Calcular fin
        dias_necesarios = proceso.tiempo_estimado_horas / recurso.horas_disponibles_dia
        fecha_fin = fecha_inicio + timedelta(days=int(dias_necesarios) + 1)
        
        # Calcular costo
        costo_estimado = proceso.tiempo_estimado_horas * recurso.costo_por_hora
        
        return AsignacionRecurso(
            proceso_id=proceso.id,
            recurso_id=recurso.id,
            horas_asignadas=proceso.tiempo_estimado_horas,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            prioridad=proceso.prioridad.value,
            costo_estimado=costo_estimado
        )
    
    def _calcular_metricas(self, 
                          asignaciones: List[AsignacionRecurso], 
                          request: DistribucionRecursosRequest) -> Dict[str, float]:
        """
        Calcula métricas de la distribución.
        
        Args:
            asignaciones: Lista de asignaciones realizadas
            request: Datos de entrada
            
        Returns:
            Dict[str, float]: Métricas calculadas
        """
        if not asignaciones:
            return {
                "eficiencia": 0.0,
                "costo_total": 0.0,
                "tiempo_total": 0.0,
                "utilizacion_recursos": 0.0
            }
        
        # Calcular métricas básicas
        costo_total = sum(a.costo_estimado for a in asignaciones)
        tiempo_total = max(a.fecha_fin for a in asignaciones) - min(a.fecha_inicio for a in asignaciones)
        tiempo_total_horas = tiempo_total.total_seconds() / 3600
        
        # Calcular eficiencia
        horas_trabajo_total = sum(a.horas_asignadas for a in asignaciones)
        recursos_utilizados = len(set(a.recurso_id for a in asignaciones))
        recursos_totales = len(request.recursos)
        
        eficiencia = (horas_trabajo_total / tiempo_total_horas) * 100 if tiempo_total_horas > 0 else 0
        utilizacion_recursos = (recursos_utilizados / recursos_totales) * 100 if recursos_totales > 0 else 0
        
        return {
            "eficiencia": min(eficiencia, 100.0),
            "costo_total": costo_total,
            "tiempo_total": tiempo_total_horas,
            "utilizacion_recursos": utilizacion_recursos,
            "horas_trabajo_total": horas_trabajo_total,
            "recursos_utilizados": recursos_utilizados,
            "costo_promedio_hora": costo_total / horas_trabajo_total if horas_trabajo_total > 0 else 0
        }
    
    def _identificar_procesos_sin_asignar(self, 
                                         procesos_originales: List[Proceso],
                                         asignaciones: List[AsignacionRecurso]) -> List[Proceso]:
        """
        Identifica procesos que no pudieron ser asignados.
        
        Args:
            procesos_originales: Lista original de procesos
            asignaciones: Lista de asignaciones realizadas
            
        Returns:
            List[Proceso]: Lista de procesos sin asignar
        """
        procesos_asignados = {a.proceso_id for a in asignaciones}
        return [p for p in procesos_originales if p.id not in procesos_asignados]
    
    def _generar_recomendaciones(self, 
                                asignaciones: List[AsignacionRecurso],
                                procesos_sin_asignar: List[Proceso],
                                recursos_disponibles: List[Recurso],
                                request: DistribucionRecursosRequest) -> List[str]:
        """
        Genera recomendaciones basadas en el resultado de la distribución.
        
        Args:
            asignaciones: Lista de asignaciones realizadas
            procesos_sin_asignar: Lista de procesos sin asignar
            recursos_disponibles: Lista de recursos disponibles
            request: Datos de entrada
            
        Returns:
            List[str]: Lista de recomendaciones
        """
        recomendaciones = []
        
        # Recomendaciones por procesos sin asignar
        if procesos_sin_asignar:
            recomendaciones.append(f"Hay {len(procesos_sin_asignar)} procesos sin asignar. Considere añadir más recursos o flexibilizar restricciones.")
        
        # Recomendaciones por utilización de recursos
        if recursos_disponibles:
            recursos_no_utilizados = len(recursos_disponibles) - len(set(a.recurso_id for a in asignaciones))
            if recursos_no_utilizados > 0:
                recomendaciones.append(f"Hay {recursos_no_utilizados} recursos no utilizados. Considere reasignar o redistribuir la carga.")
        
        # Recomendaciones por eficiencia
        if asignaciones:
            metricas = self._calcular_metricas(asignaciones, request)
            if metricas["eficiencia"] < 60:
                recomendaciones.append("La eficiencia es baja. Considere ajustar la estrategia de distribución o las restricciones.")
            elif metricas["eficiencia"] > 90:
                recomendaciones.append("Excelente eficiencia. Considere planificar procesos adicionales.")
        
        # Recomendaciones por costos
        if request.optimizar_costos and asignaciones:
            costo_promedio = sum(a.costo_estimado for a in asignaciones) / len(asignaciones)
            if costo_promedio > 1000:  # Umbral configurable
                recomendaciones.append("Los costos son altos. Considere usar recursos más económicos o revisar la duración de los procesos.")
        
        return recomendaciones
