"""
Rutas para Planeador

Este módulo contiene los endpoints relacionados con la planificación
y optimización de recursos. Incluye funcionalidades como cálculo de
capacidad, distribución de recursos y generación de planes optimizados.

Endpoints disponibles:
- POST /capacidad: Calcular capacidad semanal
- POST /distribuir: Distribuir recursos entre procesos
- POST /optimizar: Optimizar asignaciones usando algoritmos avanzados
- GET /planes: Listar planes guardados
- POST /planes: Guardar plan de trabajo
- GET /reportes: Generar reportes de planificación

Autor: Equipo de Desarrollo
Fecha: 2025-07-07
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, time
import logging

# Importar casos de uso y modelos
from app.use_cases.calcular_capacidad import (
    CapacidadSemanalRequest, CapacidadSemanalResponse
)
from app.use_cases.distribuir_recursos import (
    DistribucionRecursosRequest, DistribucionRecursosResponse,
    EstrategiaDistribucion, RestriccionDistribucion, AsignacionRecurso
)
from app.services.optimizador import (
    OptimizadorRecursos, ParametrosOptimizacion, AlgoritmoOptimizacion, SolucionOptimizada
)
from domain.models.proceso import Proceso, TipoProceso, NivelPrioridad
from domain.models.recurso import Recurso, TipoRecurso, HorarioTrabajo


# Configuración de logging
logger = logging.getLogger(__name__)


def tipo_recurso_from_string(tipo_str: str) -> TipoRecurso:
    """Convierte string a enum de tipo recurso"""
    tipo_map = {
        "humano": TipoRecurso.HUMANO,
        "material": TipoRecurso.MATERIAL,
        "tecnologico": TipoRecurso.TECNOLOGICO,
        "espacial": TipoRecurso.ESPACIAL,
        "financiero": TipoRecurso.FINANCIERO
    }
    return tipo_map.get(tipo_str.lower(), TipoRecurso.HUMANO)


def tipo_proceso_from_string(tipo_str: str) -> TipoProceso:
    """Convierte string a enum de tipo proceso"""
    tipo_map = {
        "rutinario": TipoProceso.RUTINARIO,
        "especial": TipoProceso.ESPECIAL,
        "urgente": TipoProceso.URGENTE,
        "mantenimiento": TipoProceso.MANTENIMIENTO
    }
    return tipo_map.get(tipo_str.lower(), TipoProceso.RUTINARIO)


def prioridad_from_string(prioridad_str: str) -> NivelPrioridad:
    """Convierte string a enum de prioridad"""
    prioridad_map = {
        "baja": NivelPrioridad.BAJA,
        "media": NivelPrioridad.MEDIA,
        "alta": NivelPrioridad.ALTA,
        "critica": NivelPrioridad.CRITICA
    }
    return prioridad_map.get(prioridad_str.lower(), NivelPrioridad.MEDIA)


def estrategia_distribucion_from_string(estrategia_str: str) -> EstrategiaDistribucion:
    """Convierte string a enum de estrategia de distribución"""
    estrategia_map = {
        "prioridad": EstrategiaDistribucion.PRIORIDAD,
        "eficiencia": EstrategiaDistribucion.EFICIENCIA,
        "costo_minimo": EstrategiaDistribucion.COSTO_MINIMO,
        "tiempo_minimo": EstrategiaDistribucion.TIEMPO_MINIMO,
        "balanceada": EstrategiaDistribucion.BALANCEADA
    }
    return estrategia_map.get(estrategia_str.lower(), EstrategiaDistribucion.BALANCEADA)


def algoritmo_optimizacion_from_string(algoritmo_str: str) -> AlgoritmoOptimizacion:
    """Convierte string a enum de algoritmo de optimización"""
    algoritmo_map = {
        "lineal": AlgoritmoOptimizacion.LINEAL,
        "genetico": AlgoritmoOptimizacion.GENETICO,
        "simulated_annealing": AlgoritmoOptimizacion.SIMULATED_ANNEALING,
        "greedy": AlgoritmoOptimizacion.GREEDY,
        "branch_and_bound": AlgoritmoOptimizacion.BRANCH_AND_BOUND
    }
    return algoritmo_map.get(algoritmo_str.lower(), AlgoritmoOptimizacion.GREEDY)

# Crear router
router = APIRouter()


# Modelos Pydantic para la API

class RecursoSimple(BaseModel):
    """Modelo simplificado de recurso para requests."""
    nombre: str
    tipo: str = "humano"
    capacidad_maxima: float
    costo_por_hora: float = 0.0
    habilidades: List[str] = Field(default_factory=list)
    horas_dia: float = 8.0


class ProcesoSimple(BaseModel):
    """Modelo simplificado de proceso para requests."""
    nombre: str
    tiempo_estimado_horas: float
    prioridad: str = "media"
    tipo: str = "rutinario"
    recursos_requeridos: List[str] = Field(default_factory=list)


class CapacidadRequest(BaseModel):
    """Request para cálculo de capacidad."""
    fecha_inicio: datetime
    fecha_fin: datetime
    recursos: List[RecursoSimple]
    restricciones: Optional[Dict[str, Any]] = None


class CapacidadResponse(BaseModel):
    """Response del cálculo de capacidad."""
    total_procesos_posibles: int
    capacidad_por_recurso: Dict[str, int]
    tiempo_total_disponible: float
    tiempo_total_requerido: float
    eficiencia_proyectada: float
    recomendaciones: List[str]


class DistribucionRequest(BaseModel):
    """Request para distribución de recursos."""
    procesos: List[ProcesoSimple]
    recursos: List[RecursoSimple]
    estrategia: str = "balanceada"
    fecha_inicio: Optional[datetime] = None
    restricciones: Optional[Dict[str, Any]] = None


class AsignacionResponse(BaseModel):
    """Response de una asignación."""
    proceso_id: str
    recurso_id: str
    horas_asignadas: float
    fecha_inicio: datetime
    fecha_fin: datetime
    costo_estimado: float


class DistribucionResponse(BaseModel):
    """Response de la distribución."""
    asignaciones: List[AsignacionResponse]
    procesos_asignados: int
    procesos_sin_asignar: int
    recursos_utilizados: int
    eficiencia_estimada: float
    costo_total: float
    tiempo_total: float
    recomendaciones: List[str]


class OptimizacionRequest(BaseModel):
    """Request para optimización."""
    procesos: List[ProcesoSimple]
    recursos: List[RecursoSimple]
    algoritmo: str = "greedy"
    parametros: Optional[Dict[str, Any]] = None


class OptimizacionResponse(BaseModel):
    """Response de la optimización."""
    asignaciones: List[AsignacionResponse]
    valor_objetivo: float
    tiempo_ejecucion: float
    iteraciones: int
    convergencia: bool
    metricas: Dict[str, Any]


class PlanTrabajo(BaseModel):
    """Modelo para planes de trabajo."""
    nombre: str
    descripcion: str = ""
    fecha_inicio: datetime
    fecha_fin: datetime
    asignaciones: List[AsignacionResponse]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReporteRequest(BaseModel):
    """Request para generación de reportes."""
    tipo_reporte: str = "resumen"
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    incluir_graficos: bool = True
    formato: str = "json"


# Endpoints

@router.post("/capacidad", response_model=CapacidadResponse)
async def calcular_capacidad(request: CapacidadRequest):
    """
    Calcula la capacidad semanal de procesamiento.
    
    Args:
        request: Datos para el cálculo de capacidad
        
    Returns:
        CapacidadResponse: Resultado del cálculo
    """
    try:
        logger.info("Calculando capacidad semanal")
        
        # Convertir recursos del request a entidades del dominio
        recursos: List[Recurso] = []
        for r in request.recursos:
            recurso = Recurso(
                nombre=r.nombre,
                tipo=tipo_recurso_from_string(r.tipo),
                capacidad_maxima=r.capacidad_maxima
            )
            recurso.costo_por_hora = r.costo_por_hora
            recurso.habilidades = r.habilidades
            
            # Configurar horario
            if r.horas_dia > 0:
                recurso.horario = HorarioTrabajo(
                    hora_inicio=time(8, 0),
                    hora_fin=time(8 + int(r.horas_dia), 0)
                )
            
            recursos.append(recurso)
        
        # Crear request del caso de uso
        capacidad_request = CapacidadSemanalRequest(
            fecha_inicio=request.fecha_inicio,
            fecha_fin=request.fecha_fin,
            recursos_disponibles=recursos,
            restricciones=request.restricciones
        )
        
        # Ejecutar caso de uso
        # caso_uso = CalcularCapacidadSemanal(proceso_repository)
        # resultado = caso_uso.execute(capacidad_request)
        
        # Simular resultado
        resultado = CapacidadSemanalResponse(
            total_procesos_posibles=20,
            capacidad_por_recurso={r.nombre: 5 for r in recursos},
            tiempo_total_disponible=160.0,
            tiempo_total_requerido=120.0,
            eficiencia_proyectada=75.0,
            recomendaciones=[
                "La eficiencia es buena. Considere planificar procesos adicionales.",
                "Distribución balanceada entre recursos."
            ]
        )
        
        response = CapacidadResponse(
            total_procesos_posibles=resultado.total_procesos_posibles,
            capacidad_por_recurso=resultado.capacidad_por_recurso,
            tiempo_total_disponible=resultado.tiempo_total_disponible,
            tiempo_total_requerido=resultado.tiempo_total_requerido,
            eficiencia_proyectada=resultado.eficiencia_proyectada,
            recomendaciones=resultado.recomendaciones
        )
        
        logger.info(f"Capacidad calculada: {resultado.total_procesos_posibles} procesos posibles")
        return response
        
    except Exception as e:
        logger.error(f"Error calculando capacidad: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al calcular capacidad: {str(e)}"
        )


@router.post("/distribuir", response_model=DistribucionResponse)
async def distribuir_recursos(request: DistribucionRequest):
    """
    Distribuye recursos entre procesos usando la estrategia especificada.
    
    Args:
        request: Datos para la distribución
        
    Returns:
        DistribucionResponse: Resultado de la distribución
    """
    try:
        logger.info(f"Distribuyendo recursos con estrategia: {request.estrategia}")
        
        # Convertir procesos del request a entidades del dominio
        procesos: List[Proceso] = []
        for p in request.procesos:
            proceso = Proceso(
                nombre=p.nombre,
                descripcion="Proceso desde API",
                tipo=tipo_proceso_from_string(p.tipo),
                tiempo_estimado_horas=p.tiempo_estimado_horas,
                prioridad=prioridad_from_string(p.prioridad)
            )
            proceso.recursos_requeridos = p.recursos_requeridos
            procesos.append(proceso)
        
        # Convertir recursos del request a entidades del dominio
        recursos: List[Recurso] = []
        for r in request.recursos:
            recurso = Recurso(
                nombre=r.nombre,
                tipo=tipo_recurso_from_string(r.tipo),
                capacidad_maxima=r.capacidad_maxima
            )
            recurso.costo_por_hora = r.costo_por_hora
            recurso.habilidades = r.habilidades
            recursos.append(recurso)
        
        # Crear request del caso de uso
        distribucion_request = DistribucionRecursosRequest(
            procesos=procesos,
            recursos=recursos,
            estrategia=estrategia_distribucion_from_string(request.estrategia),
            fecha_inicio=request.fecha_inicio or datetime.now(),
            restricciones=RestriccionDistribucion() if not request.restricciones else None
        )
        
        # Ejecutar caso de uso
        # caso_uso = DistribuirRecursos(proceso_repository)
        # resultado = caso_uso.execute(distribucion_request)
        
        # Simular resultado
        asignaciones_simuladas: List[AsignacionRecurso] = []
        for i, proceso in enumerate(procesos[:min(len(procesos), len(recursos))]):
            recurso = recursos[i % len(recursos)]
            asignacion = AsignacionRecurso(
                proceso_id=proceso.id,
                recurso_id=recurso.id,
                horas_asignadas=proceso.tiempo_estimado_horas,
                fecha_inicio=datetime.now(),
                fecha_fin=datetime.now(),
                prioridad=proceso.prioridad.value,
                costo_estimado=proceso.tiempo_estimado_horas * recurso.costo_por_hora
            )
            asignaciones_simuladas.append(asignacion)
        
        resultado = DistribucionRecursosResponse(
            asignaciones=asignaciones_simuladas,
            procesos_asignados=len(asignaciones_simuladas),
            procesos_sin_asignar=[],
            recursos_utilizados=min(len(recursos), len(procesos)),
            eficiencia_estimada=85.0,
            costo_total=sum(a.costo_estimado for a in asignaciones_simuladas),
            tiempo_total=40.0,
            recomendaciones=["Distribución óptima encontrada"],
            metricas={"eficiencia": 85.0}
        )
        
        # Convertir a response
        asignaciones_response = [
            AsignacionResponse(
                proceso_id=a.proceso_id,
                recurso_id=a.recurso_id,
                horas_asignadas=a.horas_asignadas,
                fecha_inicio=a.fecha_inicio,
                fecha_fin=a.fecha_fin,
                costo_estimado=a.costo_estimado
            )
            for a in resultado.asignaciones
        ]
        
        response = DistribucionResponse(
            asignaciones=asignaciones_response,
            procesos_asignados=resultado.procesos_asignados,
            procesos_sin_asignar=len(resultado.procesos_sin_asignar),
            recursos_utilizados=resultado.recursos_utilizados,
            eficiencia_estimada=resultado.eficiencia_estimada,
            costo_total=resultado.costo_total,
            tiempo_total=resultado.tiempo_total,
            recomendaciones=resultado.recomendaciones
        )
        
        logger.info(f"Distribución completada: {len(asignaciones_response)} asignaciones")
        return response
        
    except Exception as e:
        logger.error(f"Error distribuyendo recursos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al distribuir recursos: {str(e)}"
        )


@router.post("/optimizar", response_model=OptimizacionResponse)
async def optimizar_asignaciones(request: OptimizacionRequest):
    """
    Optimiza las asignaciones usando algoritmos avanzados.
    
    Args:
        request: Datos para la optimización
        
    Returns:
        OptimizacionResponse: Resultado de la optimización
    """
    try:
        logger.info(f"Optimizando asignaciones con algoritmo: {request.algoritmo}")
        
        # Convertir procesos y recursos
        procesos: List[Proceso] = []
        for p in request.procesos:
            proceso = Proceso(
                nombre=p.nombre,
                descripcion="Proceso desde API",
                tipo=tipo_proceso_from_string(p.tipo),
                tiempo_estimado_horas=p.tiempo_estimado_horas,
                prioridad=prioridad_from_string(p.prioridad)
            )
            procesos.append(proceso)
        
        recursos: List[Recurso] = []
        for r in request.recursos:
            recurso = Recurso(
                nombre=r.nombre,
                tipo=tipo_recurso_from_string(r.tipo),
                capacidad_maxima=r.capacidad_maxima
            )
            recurso.costo_por_hora = r.costo_por_hora
            recursos.append(recurso)
        
        # Configurar parámetros de optimización
        parametros = ParametrosOptimizacion(
            algoritmo=algoritmo_optimizacion_from_string(request.algoritmo),
            max_iteraciones=request.parametros.get("max_iteraciones", 1000) if request.parametros else 1000,
            peso_costo=request.parametros.get("peso_costo", 0.4) if request.parametros else 0.4,
            peso_tiempo=request.parametros.get("peso_tiempo", 0.3) if request.parametros else 0.3,
            peso_eficiencia=request.parametros.get("peso_eficiencia", 0.3) if request.parametros else 0.3
        )
        
        # Ejecutar optimización
        optimizador = OptimizadorRecursos()
        # resultado = optimizador.optimizar_asignaciones(procesos, recursos, parametros)
        
        # Simular resultado
        asignaciones_optimizadas: List[AsignacionRecurso] = []
        for i, proceso in enumerate(procesos[:min(len(procesos), len(recursos))]):
            recurso = recursos[i % len(recursos)]
            asignacion = AsignacionRecurso(
                proceso_id=proceso.id,
                recurso_id=recurso.id,
                horas_asignadas=proceso.tiempo_estimado_horas,
                fecha_inicio=datetime.now(),
                fecha_fin=datetime.now(),
                prioridad=proceso.prioridad.value,
                costo_estimado=proceso.tiempo_estimado_horas * recurso.costo_por_hora
            )
            asignaciones_optimizadas.append(asignacion)
        
        resultado = SolucionOptimizada(
            asignaciones=asignaciones_optimizadas,
            valor_objetivo=100.5,
            tiempo_ejecucion=0.5,
            iteraciones=50,
            convergencia=True,
            metricas={"eficiencia": 90.0, "costo_total": 1000.0}
        )
        
        # Convertir a response
        asignaciones_response = [
            AsignacionResponse(
                proceso_id=a.proceso_id,
                recurso_id=a.recurso_id,
                horas_asignadas=a.horas_asignadas,
                fecha_inicio=a.fecha_inicio,
                fecha_fin=a.fecha_fin,
                costo_estimado=a.costo_estimado
            )
            for a in resultado.asignaciones
        ]
        
        response = OptimizacionResponse(
            asignaciones=asignaciones_response,
            valor_objetivo=resultado.valor_objetivo,
            tiempo_ejecucion=resultado.tiempo_ejecucion,
            iteraciones=resultado.iteraciones,
            convergencia=resultado.convergencia,
            metricas=resultado.metricas
        )
        
        logger.info(f"Optimización completada en {resultado.tiempo_ejecucion:.2f}s")
        return response
        
    except Exception as e:
        logger.error(f"Error optimizando asignaciones: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al optimizar asignaciones: {str(e)}"
        )


@router.get("/planes")
async def listar_planes() -> List[Dict[str, Any]]:
    """
    Lista los planes de trabajo guardados.
    
    Returns:
        List[PlanTrabajo]: Lista de planes guardados
    """
    try:
        logger.info("Listando planes de trabajo")
        
        # Simular planes guardados
        planes = [
            {
                "id": "1",
                "nombre": "Plan Semanal - Semana 1",
                "descripcion": "Plan de trabajo para la primera semana",
                "fecha_inicio": datetime.now(),
                "fecha_fin": datetime.now(),
                "asignaciones": [],
                "metadata": {"creado_por": "usuario@ejemplo.com"}
            }
        ]
        
        return planes
        
    except Exception as e:
        logger.error(f"Error listando planes: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al listar planes: {str(e)}"
        )


@router.post("/planes")
async def guardar_plan(plan: PlanTrabajo) -> Dict[str, str]:
    """
    Guarda un nuevo plan de trabajo.
    
    Args:
        plan: Plan de trabajo a guardar
        
    Returns:
        Dict: Confirmación del guardado
    """
    try:
        logger.info(f"Guardando plan: {plan.nombre}")
        
        # Aquí iría la lógica para guardar en base de datos
        plan_id = "nuevo_plan_id"
        
        return {
            "id": plan_id,
            "message": f"Plan '{plan.nombre}' guardado exitosamente"
        }
        
    except Exception as e:
        logger.error(f"Error guardando plan: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al guardar plan: {str(e)}"
        )


@router.post("/reportes")
async def generar_reporte(request: ReporteRequest) -> Dict[str, Any]:
    """
    Genera reportes de planificación.
    
    Args:
        request: Configuración del reporte
        
    Returns:
        Dict: Reporte generado
    """
    try:
        logger.info(f"Generando reporte tipo: {request.tipo_reporte}")
        
        # Simular generación de reporte
        reporte = {
            "tipo": request.tipo_reporte,
            "fecha_generacion": datetime.now(),
            "resumen": {
                "total_procesos": 50,
                "total_recursos": 10,
                "eficiencia_promedio": 85.5,
                "costo_total": 15000.0
            },
            "detalles": {
                "procesos_por_estado": {
                    "completados": 30,
                    "en_progreso": 15,
                    "pendientes": 5
                },
                "utilizacion_recursos": {
                    "promedio": 75.0,
                    "maximo": 95.0,
                    "minimo": 45.0
                }
            }
        }
        
        if request.incluir_graficos:
            reporte["graficos"] = {
                "eficiencia_temporal": "data:image/base64,ejemplo",
                "distribucion_recursos": "data:image/base64,ejemplo"
            }
        
        return reporte
        
    except Exception as e:
        logger.error(f"Error generando reporte: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al generar reporte: {str(e)}"
        )
