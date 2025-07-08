"""
Rutas para Procesos

Este módulo contiene los endpoints relacionados con la gestión
de procesos: crear, leer, actualizar, eliminar y operaciones
especializadas como carga desde Excel.

Endpoints disponibles:
- GET /: Listar procesos
- POST /: Crear proceso
- GET /{id}: Obtener proceso específico
- PUT /{id}: Actualizar proceso
- DELETE /{id}: Eliminar proceso
- POST /upload: Cargar procesos desde Excel
- GET /estadisticas: Obtener estadísticas de procesos

Autor: Equipo de Desarrollo
Fecha: 2025-07-07
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import tempfile
import os

# Importar casos de uso y modelos
from domain.models.proceso import Proceso, TipoProceso, EstadoProceso, NivelPrioridad
from infrastructure.excel.lector_excel import LectorExcel, ConfiguracionLectura
from infrastructure.database.config import get_db
from infrastructure.repositories.proceso_repository_impl import SQLAlchemyProcesoRepository
from app.use_cases.calcular_capacidad import CalcularCapacidadSemanal


# Configuración de logging
logger = logging.getLogger(__name__)


def prioridad_to_string(prioridad: NivelPrioridad) -> str:
    """Convierte enum de prioridad a string"""
    prioridad_map = {
        NivelPrioridad.BAJA: "baja",
        NivelPrioridad.MEDIA: "media",
        NivelPrioridad.ALTA: "alta",
        NivelPrioridad.CRITICA: "critica"
    }
    return prioridad_map.get(prioridad, "media")


def estado_to_string(estado: EstadoProceso) -> str:
    """Convierte enum de estado a string"""
    return estado.value


def tipo_to_string(tipo: TipoProceso) -> str:
    """Convierte enum de tipo a string"""
    return tipo.value

# Crear router
router = APIRouter()


# Modelos Pydantic para la API
class ProcesoRequest(BaseModel):
    """
    Modelo para crear/actualizar procesos.
    """
    nombre: str = Field(..., description="Nombre del proceso", min_length=1, max_length=200)
    descripcion: str = Field("", description="Descripción del proceso", max_length=1000)
    tipo: str = Field("rutinario", description="Tipo de proceso (rutinario, especial, urgente, mantenimiento)")
    tiempo_estimado_horas: float = Field(..., description="Tiempo estimado en horas", gt=0)
    prioridad: str = Field("media", description="Prioridad del proceso (baja, media, alta, critica)")
    recursos_requeridos: List[str] = Field(default_factory=list, description="Lista de recursos requeridos")
    fecha_limite: Optional[datetime] = Field(None, description="Fecha límite del proceso")
    asignado_a: Optional[str] = Field(None, description="Usuario asignado al proceso")
    notas: str = Field("", description="Notas adicionales")


class ProcesoResponse(BaseModel):
    """
    Modelo para respuestas de procesos.
    """
    id: str
    nombre: str
    descripcion: str
    tipo: str
    estado: str
    tiempo_estimado_horas: float
    tiempo_real_horas: Optional[float]
    prioridad: str
    recursos_requeridos: List[str]
    fecha_creacion: datetime
    fecha_inicio: Optional[datetime]
    fecha_fin: Optional[datetime]
    fecha_limite: Optional[datetime]
    asignado_a: Optional[str]
    notas: str
    progreso: float
    puede_ejecutarse: bool
    vencido: bool


class EstadisticasProcesos(BaseModel):
    """
    Modelo para estadísticas de procesos.
    """
    total_procesos: int
    por_estado: Dict[str, int]
    por_tipo: Dict[str, int]
    por_prioridad: Dict[str, int]
    tiempo_total_estimado: float
    tiempo_total_real: Optional[float]
    procesos_vencidos: int
    procesos_completados: int
    eficiencia_promedio: float


class ResultadoCargaExcel(BaseModel):
    """
    Modelo para resultado de carga desde Excel.
    """
    procesos_cargados: int
    recursos_cargados: int
    errores: List[str]
    advertencias: List[str]
    estadisticas: Dict[str, Any]


# Endpoints

@router.get("/", response_model=List[ProcesoResponse])
async def listar_procesos(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    tipo: Optional[str] = Query(None, description="Filtrar por tipo"),
    prioridad: Optional[str] = Query(None, description="Filtrar por prioridad"),
    asignado_a: Optional[str] = Query(None, description="Filtrar por usuario asignado"),
    limite: int = Query(100, ge=1, le=1000, description="Límite de resultados"),
    offset: int = Query(0, ge=0, description="Offset para paginación")
):
    """
    Lista todos los procesos con filtros opcionales.
    
    Args:
        estado: Filtro por estado del proceso
        tipo: Filtro por tipo de proceso
        prioridad: Filtro por prioridad
        asignado_a: Filtro por usuario asignado
        limite: Número máximo de resultados
        offset: Número de resultados a omitir
        
    Returns:
        List[ProcesoResponse]: Lista de procesos
    """
    try:
        logger.info(f"Listando procesos con filtros: estado={estado}, tipo={tipo}, prioridad={prioridad}")
        
        # Aquí iría la lógica para obtener procesos desde el repositorio
        # Por ahora retornamos una lista vacía
        procesos = []
        
        # Simular algunos procesos de ejemplo
        if not any([estado, tipo, prioridad, asignado_a]):
            procesos = [
                ProcesoResponse(
                    id="1",
                    nombre="Proceso de Ejemplo 1",
                    descripcion="Este es un proceso de ejemplo",
                    tipo="rutinario",
                    estado="pendiente",
                    tiempo_estimado_horas=8.0,
                    tiempo_real_horas=None,
                    prioridad="media",
                    recursos_requeridos=["Recurso A", "Recurso B"],
                    fecha_creacion=datetime.now(),
                    fecha_inicio=None,
                    fecha_fin=None,
                    fecha_limite=None,
                    asignado_a=None,
                    notas="",
                    progreso=0.0,
                    puede_ejecutarse=True,
                    vencido=False
                ),
                ProcesoResponse(
                    id="2",
                    nombre="Proceso de Ejemplo 2",
                    descripcion="Otro proceso de ejemplo",
                    tipo="especial",
                    estado="en_progreso",
                    tiempo_estimado_horas=12.0,
                    tiempo_real_horas=6.0,
                    prioridad="alta",
                    recursos_requeridos=["Recurso C"],
                    fecha_creacion=datetime.now(),
                    fecha_inicio=datetime.now(),
                    fecha_fin=None,
                    fecha_limite=None,
                    asignado_a="usuario@ejemplo.com",
                    notas="En progreso",
                    progreso=0.5,
                    puede_ejecutarse=False,
                    vencido=False
                )
            ]
        
        return procesos
        
    except Exception as e:
        logger.error(f"Error listando procesos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al listar procesos: {str(e)}"
        )


@router.post("/", response_model=ProcesoResponse)
async def crear_proceso(proceso_data: ProcesoRequest):
    """
    Crea un nuevo proceso.
    
    Args:
        proceso_data: Datos del proceso a crear
        
    Returns:
        ProcesoResponse: Proceso creado
    """
    try:
        logger.info(f"Creando proceso: {proceso_data.nombre}")
        
        # Validar tipos de enum
        try:
            tipo = TipoProceso(proceso_data.tipo)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de proceso inválido: {proceso_data.tipo}"
            )
        
        # Mapear prioridad string a enum
        prioridad_map = {
            "baja": NivelPrioridad.BAJA,
            "media": NivelPrioridad.MEDIA,
            "alta": NivelPrioridad.ALTA,
            "critica": NivelPrioridad.CRITICA
        }
        
        prioridad = prioridad_map.get(proceso_data.prioridad.lower())
        if not prioridad:
            raise HTTPException(
                status_code=400,
                detail=f"Prioridad inválida: {proceso_data.prioridad}"
            )
        
        # Crear proceso
        proceso = Proceso(
            nombre=proceso_data.nombre,
            descripcion=proceso_data.descripcion,
            tipo=tipo,
            tiempo_estimado_horas=proceso_data.tiempo_estimado_horas,
            prioridad=prioridad
        )
        
        # Configurar campos opcionales
        if proceso_data.recursos_requeridos:
            proceso.recursos_requeridos = proceso_data.recursos_requeridos
        
        if proceso_data.fecha_limite:
            proceso.fecha_limite = proceso_data.fecha_limite
        
        if proceso_data.asignado_a:
            proceso.asignado_a = proceso_data.asignado_a
        
        if proceso_data.notas:
            proceso.notas = proceso_data.notas
        
        # Aquí iría la lógica para guardar en el repositorio
        # proceso_guardado = proceso_repository.crear_proceso(proceso)
        
        # Convertir a response model
        response = ProcesoResponse(
            id=proceso.id,
            nombre=proceso.nombre,
            descripcion=proceso.descripcion,
            tipo=tipo_to_string(proceso.tipo),
            estado=estado_to_string(proceso.estado),
            tiempo_estimado_horas=proceso.tiempo_estimado_horas,
            tiempo_real_horas=proceso.tiempo_real_horas,
            prioridad=prioridad_to_string(proceso.prioridad),
            recursos_requeridos=proceso.recursos_requeridos,
            fecha_creacion=proceso.fecha_creacion,
            fecha_inicio=proceso.fecha_inicio,
            fecha_fin=proceso.fecha_fin,
            fecha_limite=proceso.fecha_limite,
            asignado_a=proceso.asignado_a,
            notas=proceso.notas,
            progreso=proceso.calcular_progreso(),
            puede_ejecutarse=proceso.puede_ejecutarse(),
            vencido=proceso.esta_vencido()
        )
        
        logger.info(f"Proceso creado exitosamente: {proceso.id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creando proceso: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al crear proceso: {str(e)}"
        )


@router.get("/{proceso_id}", response_model=ProcesoResponse)
async def obtener_proceso(proceso_id: str):
    """
    Obtiene un proceso específico por ID.
    
    Args:
        proceso_id: ID del proceso a obtener
        
    Returns:
        ProcesoResponse: Proceso encontrado
    """
    try:
        logger.info(f"Obteniendo proceso: {proceso_id}")
        
        # Aquí iría la lógica para obtener desde el repositorio
        # proceso = proceso_repository.obtener_por_id(proceso_id)
        
        # Simular proceso no encontrado
        if proceso_id == "999":
            raise HTTPException(
                status_code=404,
                detail=f"Proceso con ID {proceso_id} no encontrado"
            )
        
        # Simular proceso encontrado
        proceso = Proceso(
            nombre="Proceso de Ejemplo",
            descripcion="Este es un proceso de ejemplo",
            tipo=TipoProceso.RUTINARIO,
            tiempo_estimado_horas=8.0,
            prioridad=NivelPrioridad.MEDIA
        )
        proceso.id = proceso_id
        
        response = ProcesoResponse(
            id=proceso.id,
            nombre=proceso.nombre,
            descripcion=proceso.descripcion,
            tipo=tipo_to_string(proceso.tipo),
            estado=estado_to_string(proceso.estado),
            tiempo_estimado_horas=proceso.tiempo_estimado_horas,
            tiempo_real_horas=proceso.tiempo_real_horas,
            prioridad=prioridad_to_string(proceso.prioridad),
            recursos_requeridos=proceso.recursos_requeridos,
            fecha_creacion=proceso.fecha_creacion,
            fecha_inicio=proceso.fecha_inicio,
            fecha_fin=proceso.fecha_fin,
            fecha_limite=proceso.fecha_limite,
            asignado_a=proceso.asignado_a,
            notas=proceso.notas,
            progreso=proceso.calcular_progreso(),
            puede_ejecutarse=proceso.puede_ejecutarse(),
            vencido=proceso.esta_vencido()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error obteniendo proceso: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener proceso: {str(e)}"
        )


@router.put("/{proceso_id}", response_model=ProcesoResponse)
async def actualizar_proceso(proceso_id: str, proceso_data: ProcesoRequest):
    """
    Actualiza un proceso existente.
    
    Args:
        proceso_id: ID del proceso a actualizar
        proceso_data: Nuevos datos del proceso
        
    Returns:
        ProcesoResponse: Proceso actualizado
    """
    try:
        logger.info(f"Actualizando proceso: {proceso_id}")
        
        # Aquí iría la lógica para obtener y actualizar desde el repositorio
        # proceso = proceso_repository.obtener_por_id(proceso_id)
        # if not proceso:
        #     raise HTTPException(status_code=404, detail="Proceso no encontrado")
        
        # Simular actualización exitosa
        proceso = Proceso(
            nombre=proceso_data.nombre,
            descripcion=proceso_data.descripcion,
            tipo=TipoProceso(proceso_data.tipo),
            tiempo_estimado_horas=proceso_data.tiempo_estimado_horas,
            prioridad=NivelPrioridad(proceso_data.prioridad)
        )
        proceso.id = proceso_id
        
        response = ProcesoResponse(
            id=proceso.id,
            nombre=proceso.nombre,
            descripcion=proceso.descripcion,
            tipo=tipo_to_string(proceso.tipo),
            estado=estado_to_string(proceso.estado),
            tiempo_estimado_horas=proceso.tiempo_estimado_horas,
            tiempo_real_horas=proceso.tiempo_real_horas,
            prioridad=prioridad_to_string(proceso.prioridad),
            recursos_requeridos=proceso.recursos_requeridos,
            fecha_creacion=proceso.fecha_creacion,
            fecha_inicio=proceso.fecha_inicio,
            fecha_fin=proceso.fecha_fin,
            fecha_limite=proceso.fecha_limite,
            asignado_a=proceso.asignado_a,
            notas=proceso.notas,
            progreso=proceso.calcular_progreso(),
            puede_ejecutarse=proceso.puede_ejecutarse(),
            vencido=proceso.esta_vencido()
        )
        
        logger.info(f"Proceso actualizado exitosamente: {proceso_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error actualizando proceso: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al actualizar proceso: {str(e)}"
        )


@router.delete("/{proceso_id}")
async def eliminar_proceso(proceso_id: str):
    """
    Elimina un proceso específico.
    
    Args:
        proceso_id: ID del proceso a eliminar
        
    Returns:
        Dict: Mensaje de confirmación
    """
    try:
        logger.info(f"Eliminando proceso: {proceso_id}")
        
        # Aquí iría la lógica para eliminar desde el repositorio
        # exito = proceso_repository.eliminar_proceso(proceso_id)
        # if not exito:
        #     raise HTTPException(status_code=404, detail="Proceso no encontrado")
        
        logger.info(f"Proceso eliminado exitosamente: {proceso_id}")
        return {"message": f"Proceso {proceso_id} eliminado exitosamente"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error eliminando proceso: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al eliminar proceso: {str(e)}"
        )


@router.post("/upload", response_model=ResultadoCargaExcel)
async def cargar_procesos_excel(archivo: UploadFile = File(...)):
    """
    Carga procesos desde un archivo Excel.
    
    Args:
        archivo: Archivo Excel con datos de procesos
        
    Returns:
        ResultadoCargaExcel: Resultado de la carga
    """
    try:
        logger.info(f"Cargando procesos desde archivo: {archivo.filename}")
        
        # Validar tipo de archivo
        if not (archivo.filename or "").lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(
                status_code=400,
                detail="El archivo debe ser un archivo Excel (.xlsx o .xls)"
            )
        
        # Guardar archivo temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
            contenido = await archivo.read()
            temp_file.write(contenido)
            temp_file_path = temp_file.name
        
        try:
            # Leer archivo Excel
            lector = LectorExcel()
            resultado = lector.leer_archivo(temp_file_path)
            
            # Procesar resultados
            # Aquí iría la lógica para guardar en el repositorio
            # for proceso in resultado.procesos:
            #     proceso_repository.crear_proceso(proceso)
            
            response = ResultadoCargaExcel(
                procesos_cargados=len(resultado.procesos),
                recursos_cargados=len(resultado.recursos),
                errores=resultado.errores,
                advertencias=resultado.advertencias,
                estadisticas=resultado.estadisticas
            )
            
            logger.info(f"Archivo procesado exitosamente: {len(resultado.procesos)} procesos cargados")
            return response
            
        finally:
            # Limpiar archivo temporal
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cargando archivo Excel: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al cargar archivo Excel: {str(e)}"
        )


@router.get("/estadisticas", response_model=EstadisticasProcesos)
async def obtener_estadisticas():
    """
    Obtiene estadísticas generales de los procesos.
    
    Returns:
        EstadisticasProcesos: Estadísticas de procesos
    """
    try:
        logger.info("Obteniendo estadísticas de procesos")
        
        # Aquí iría la lógica para obtener estadísticas desde el repositorio
        # stats = proceso_repository.obtener_estadisticas()
        
        # Simular estadísticas
        estadisticas = EstadisticasProcesos(
            total_procesos=100,
            por_estado={
                "pendiente": 30,
                "en_progreso": 20,
                "completado": 45,
                "pausado": 3,
                "cancelado": 2
            },
            por_tipo={
                "rutinario": 70,
                "especial": 20,
                "urgente": 8,
                "mantenimiento": 2
            },
            por_prioridad={
                "baja": 25,
                "media": 50,
                "alta": 20,
                "critica": 5
            },
            tiempo_total_estimado=1200.0,
            tiempo_total_real=950.0,
            procesos_vencidos=5,
            procesos_completados=45,
            eficiencia_promedio=85.5
        )
        
        return estadisticas
        
    except Exception as e:
        logger.error(f"Error obteniendo estadísticas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno al obtener estadísticas: {str(e)}"
        )
