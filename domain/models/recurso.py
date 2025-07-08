"""
Entidad Recurso - Modelo de Dominio

Esta entidad representa un recurso (humano o material) que puede ser
asignado a la ejecución de procesos. Encapsula toda la información
y comportamientos relacionados con la gestión de recursos.

Principios SOLID aplicados:
- Single Responsibility: Solo maneja la lógica de recursos
- Open/Closed: Extensible para nuevos tipos de recursos
- Liskov Substitution: Las subclases pueden sustituir a la clase base

Autor: Equipo de Desarrollo
Fecha: 2025-07-07
"""

from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Optional, Dict, Any, Set
from enum import Enum
import uuid


class TipoRecurso(Enum):
    """
    Enumeración de los tipos de recursos disponibles.
    
    Tipos:
        HUMANO: Recursos de personal
        MATERIAL: Recursos materiales o equipos
        TECNOLOGICO: Recursos tecnológicos (software, hardware)
        ESPACIAL: Recursos de espacio físico
        FINANCIERO: Recursos financieros
    """
    HUMANO = "humano"
    MATERIAL = "material"
    TECNOLOGICO = "tecnologico"
    ESPACIAL = "espacial"
    FINANCIERO = "financiero"


class EstadoRecurso(Enum):
    """
    Enumeración de los estados de un recurso.
    
    Estados:
        DISPONIBLE: Recurso disponible para asignación
        ASIGNADO: Recurso asignado a un proceso
        OCUPADO: Recurso ocupado pero no asignado
        MANTENIMIENTO: Recurso en mantenimiento
        INACTIVO: Recurso temporalmente inactivo
        RETIRADO: Recurso retirado del servicio
    """
    DISPONIBLE = "disponible"
    ASIGNADO = "asignado"
    OCUPADO = "ocupado"
    MANTENIMIENTO = "mantenimiento"
    INACTIVO = "inactivo"
    RETIRADO = "retirado"


class NivelExperiencia(Enum):
    """
    Enumeración de niveles de experiencia para recursos humanos.
    
    Niveles:
        JUNIOR: Experiencia básica (0-2 años)
        INTERMEDIO: Experiencia media (2-5 años)
        SENIOR: Experiencia avanzada (5-10 años)
        EXPERTO: Experiencia especializada (10+ años)
    """
    JUNIOR = "junior"
    INTERMEDIO = "intermedio"
    SENIOR = "senior"
    EXPERTO = "experto"


@dataclass
class HorarioTrabajo:
    """
    Clase para representar el horario de trabajo de un recurso.
    
    Attributes:
        hora_inicio: Hora de inicio de trabajo
        hora_fin: Hora de finalización de trabajo
        dias_semana: Días de la semana que trabaja (0=Lunes, 6=Domingo)
        horas_descanso: Horas de descanso dentro del horario
    """
    hora_inicio: time
    hora_fin: time
    dias_semana: Set[int] = field(default_factory=lambda: {0, 1, 2, 3, 4})  # Lunes a Viernes
    horas_descanso: float = 1.0  # Hora de almuerzo por defecto
    
    def calcular_horas_diarias(self) -> float:
        """
        Calcula las horas de trabajo diarias.
        
        Returns:
            float: Horas de trabajo por día
        """
        inicio_minutos = self.hora_inicio.hour * 60 + self.hora_inicio.minute
        fin_minutos = self.hora_fin.hour * 60 + self.hora_fin.minute
        
        horas_totales = (fin_minutos - inicio_minutos) / 60
        return max(0, horas_totales - self.horas_descanso)
    
    def calcular_horas_semanales(self) -> float:
        """
        Calcula las horas de trabajo semanales.
        
        Returns:
            float: Horas de trabajo por semana
        """
        horas_diarias = self.calcular_horas_diarias()
        return horas_diarias * len(self.dias_semana)


@dataclass
class Recurso:
    """
    Entidad que representa un recurso del sistema.
    
    Esta clase encapsula toda la información y comportamientos
    relacionados con un recurso que puede ser asignado a procesos.
    
    Attributes:
        id: Identificador único del recurso
        nombre: Nombre del recurso
        descripcion: Descripción detallada del recurso
        tipo: Tipo de recurso según TipoRecurso
        estado: Estado actual del recurso
        capacidad_maxima: Capacidad máxima del recurso
        capacidad_actual: Capacidad actualmente utilizada
        costo_por_hora: Costo por hora de uso del recurso
        ubicacion: Ubicación física del recurso
        responsable: Persona responsable del recurso
        habilidades: Lista de habilidades del recurso
        experiencia: Nivel de experiencia (para recursos humanos)
        horario: Horario de trabajo del recurso
        fecha_creacion: Fecha de registro del recurso
        fecha_modificacion: Fecha de última modificación
        procesos_asignados: Lista de IDs de procesos asignados
        historial_asignaciones: Historial de asignaciones previas
        metadatos: Datos adicionales del recurso
    """
    
    # Campos obligatorios
    nombre: str
    tipo: TipoRecurso
    capacidad_maxima: float
    
    # Campos con valores por defecto
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    descripcion: str = ""
    estado: EstadoRecurso = EstadoRecurso.DISPONIBLE
    capacidad_actual: float = 0.0
    costo_por_hora: float = 0.0
    ubicacion: str = ""
    responsable: str = ""
    
    # Campos específicos para recursos humanos
    habilidades: List[str] = field(default_factory=list)
    experiencia: Optional[NivelExperiencia] = None
    horario: Optional[HorarioTrabajo] = None
    
    # Campos de fechas
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_modificacion: datetime = field(default_factory=datetime.now)
    
    # Campos de asignaciones
    procesos_asignados: List[str] = field(default_factory=list)
    historial_asignaciones: List[Dict[str, Any]] = field(default_factory=list)
    
    # Campos adicionales
    metadatos: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """
        Validaciones que se ejecutan después de la inicialización.
        
        Raises:
            ValueError: Si los datos son inválidos
        """
        self._validar_datos()
        self._configurar_horario_default()
    
    def _validar_datos(self) -> None:
        """
        Valida la consistencia de los datos del recurso.
        
        Raises:
            ValueError: Si los datos son inválidos
        """
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del recurso no puede estar vacío")
        
        if self.capacidad_maxima <= 0:
            raise ValueError("La capacidad máxima debe ser mayor a 0")
        
        if self.capacidad_actual < 0:
            raise ValueError("La capacidad actual no puede ser negativa")
        
        if self.capacidad_actual > self.capacidad_maxima:
            raise ValueError("La capacidad actual no puede exceder la capacidad máxima")
        
        if self.costo_por_hora < 0:
            raise ValueError("El costo por hora no puede ser negativo")
    
    def _configurar_horario_default(self) -> None:
        """
        Configura un horario por defecto si no se especifica uno.
        """
        if not self.horario and self.tipo == TipoRecurso.HUMANO:
            self.horario = HorarioTrabajo(
                hora_inicio=time(8, 0),  # 8:00 AM
                hora_fin=time(17, 0),    # 5:00 PM
                dias_semana={0, 1, 2, 3, 4}  # Lunes a Viernes
            )
    
    @property
    def horas_disponibles_dia(self) -> float:
        """
        Calcula las horas disponibles por día.
        
        Returns:
            float: Horas disponibles por día
        """
        if self.horario:
            return self.horario.calcular_horas_diarias()
        return 8.0  # Valor por defecto
    
    @property
    def horas_disponibles_semana(self) -> float:
        """
        Calcula las horas disponibles por semana.
        
        Returns:
            float: Horas disponibles por semana
        """
        if self.horario:
            return self.horario.calcular_horas_semanales()
        return 40.0  # Valor por defecto
    
    @property
    def capacidad_disponible(self) -> float:
        """
        Calcula la capacidad disponible del recurso.
        
        Returns:
            float: Capacidad disponible
        """
        return self.capacidad_maxima - self.capacidad_actual
    
    @property
    def porcentaje_utilizacion(self) -> float:
        """
        Calcula el porcentaje de utilización del recurso.
        
        Returns:
            float: Porcentaje de utilización (0-100)
        """
        if self.capacidad_maxima == 0:
            return 0.0
        return (self.capacidad_actual / self.capacidad_maxima) * 100
    
    def esta_disponible(self) -> bool:
        """
        Verifica si el recurso está disponible para asignación.
        
        Returns:
            bool: True si el recurso está disponible
        """
        return (self.estado == EstadoRecurso.DISPONIBLE and 
                self.capacidad_disponible > 0)
    
    def puede_asignarse(self, capacidad_requerida: float) -> bool:
        """
        Verifica si el recurso puede ser asignado con la capacidad requerida.
        
        Args:
            capacidad_requerida: Capacidad requerida para la asignación
            
        Returns:
            bool: True si puede asignarse
        """
        return (self.esta_disponible() and 
                self.capacidad_disponible >= capacidad_requerida)
    
    def asignar_proceso(self, proceso_id: str, capacidad_requerida: float) -> None:
        """
        Asigna el recurso a un proceso.
        
        Args:
            proceso_id: ID del proceso a asignar
            capacidad_requerida: Capacidad requerida para el proceso
            
        Raises:
            ValueError: Si no se puede realizar la asignación
        """
        if not self.puede_asignarse(capacidad_requerida):
            raise ValueError(f"No se puede asignar el recurso {self.nombre} al proceso {proceso_id}")
        
        if proceso_id in self.procesos_asignados:
            raise ValueError(f"El proceso {proceso_id} ya está asignado a este recurso")
        
        # Realizar la asignación
        self.procesos_asignados.append(proceso_id)
        self.capacidad_actual += capacidad_requerida
        
        # Cambiar estado si es necesario
        if self.capacidad_actual >= self.capacidad_maxima:
            self.estado = EstadoRecurso.ASIGNADO
        
        # Registrar en historial
        self._registrar_asignacion(proceso_id, capacidad_requerida, "asignado")
        
        # Actualizar fecha de modificación
        self.fecha_modificacion = datetime.now()
    
    def liberar_proceso(self, proceso_id: str) -> None:
        """
        Libera el recurso del proceso asignado.
        
        Args:
            proceso_id: ID del proceso a liberar
            
        Raises:
            ValueError: Si el proceso no está asignado
        """
        if proceso_id not in self.procesos_asignados:
            raise ValueError(f"El proceso {proceso_id} no está asignado a este recurso")
        
        # Encontrar la asignación en el historial para obtener la capacidad
        capacidad_liberada = 0.0
        for asignacion in self.historial_asignaciones:
            if (asignacion["proceso_id"] == proceso_id and 
                asignacion["accion"] == "asignado"):
                capacidad_liberada = asignacion["capacidad"]
                break
        
        # Liberar el recurso
        self.procesos_asignados.remove(proceso_id)
        self.capacidad_actual = max(0, self.capacidad_actual - capacidad_liberada)
        
        # Cambiar estado si es necesario
        if self.capacidad_actual < self.capacidad_maxima:
            self.estado = EstadoRecurso.DISPONIBLE
        
        # Registrar en historial
        self._registrar_asignacion(proceso_id, capacidad_liberada, "liberado")
        
        # Actualizar fecha de modificación
        self.fecha_modificacion = datetime.now()
    
    def _registrar_asignacion(self, proceso_id: str, capacidad: float, accion: str) -> None:
        """
        Registra una asignación en el historial.
        
        Args:
            proceso_id: ID del proceso
            capacidad: Capacidad involucrada
            accion: Acción realizada (asignado/liberado)
        """
        registro = {
            "proceso_id": proceso_id,
            "capacidad": capacidad,
            "accion": accion,
            "fecha": datetime.now(),
            "capacidad_antes": self.capacidad_actual if accion == "liberado" else self.capacidad_actual - capacidad,
            "capacidad_despues": self.capacidad_actual
        }
        self.historial_asignaciones.append(registro)
    
    def cambiar_estado(self, nuevo_estado: EstadoRecurso, motivo: str = "") -> None:
        """
        Cambia el estado del recurso.
        
        Args:
            nuevo_estado: Nuevo estado del recurso
            motivo: Motivo del cambio de estado
        """
        estado_anterior = self.estado
        self.estado = nuevo_estado
        
        # Registrar cambio en metadatos
        if "cambios_estado" not in self.metadatos:
            self.metadatos["cambios_estado"] = []
        
        self.metadatos["cambios_estado"].append({
            "fecha": datetime.now(),
            "estado_anterior": estado_anterior.value,
            "estado_nuevo": nuevo_estado.value,
            "motivo": motivo
        })
        
        self.fecha_modificacion = datetime.now()
    
    def agregar_habilidad(self, habilidad: str) -> None:
        """
        Agrega una habilidad al recurso.
        
        Args:
            habilidad: Nombre de la habilidad
        """
        if habilidad not in self.habilidades:
            self.habilidades.append(habilidad)
            self.fecha_modificacion = datetime.now()
    
    def remover_habilidad(self, habilidad: str) -> None:
        """
        Remueve una habilidad del recurso.
        
        Args:
            habilidad: Nombre de la habilidad
        """
        if habilidad in self.habilidades:
            self.habilidades.remove(habilidad)
            self.fecha_modificacion = datetime.now()
    
    def tiene_habilidad(self, habilidad: str) -> bool:
        """
        Verifica si el recurso tiene una habilidad específica.
        
        Args:
            habilidad: Nombre de la habilidad
            
        Returns:
            bool: True si tiene la habilidad
        """
        return habilidad in self.habilidades
    
    def calcular_costo_periodo(self, horas: float) -> float:
        """
        Calcula el costo del recurso para un período específico.
        
        Args:
            horas: Número de horas del período
            
        Returns:
            float: Costo total del período
        """
        return self.costo_por_hora * horas
    
    def obtener_estadisticas(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas del recurso.
        
        Returns:
            Dict[str, Any]: Estadísticas del recurso
        """
        return {
            "total_asignaciones": len(self.historial_asignaciones),
            "procesos_activos": len(self.procesos_asignados),
            "utilizacion_actual": self.porcentaje_utilizacion,
            "capacidad_disponible": self.capacidad_disponible,
            "horas_disponibles_dia": self.horas_disponibles_dia,
            "horas_disponibles_semana": self.horas_disponibles_semana,
            "costo_estimado_semana": self.calcular_costo_periodo(self.horas_disponibles_semana),
            "habilidades_totales": len(self.habilidades),
            "dias_desde_creacion": (datetime.now() - self.fecha_creacion).days
        }
    
    def obtener_resumen(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del recurso para reportes.
        
        Returns:
            Dict[str, Any]: Resumen del recurso
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo.value,
            "estado": self.estado.value,
            "capacidad_maxima": self.capacidad_maxima,
            "capacidad_actual": self.capacidad_actual,
            "capacidad_disponible": self.capacidad_disponible,
            "utilizacion": self.porcentaje_utilizacion,
            "costo_por_hora": self.costo_por_hora,
            "ubicacion": self.ubicacion,
            "habilidades": self.habilidades,
            "experiencia": self.experiencia.value if self.experiencia else None,
            "procesos_asignados": len(self.procesos_asignados),
            "disponible": self.esta_disponible(),
            "responsable": self.responsable
        }
    
    def __str__(self) -> str:
        """
        Representación en cadena del recurso.
        
        Returns:
            str: Representación legible del recurso
        """
        return f"Recurso(id={self.id[:8]}..., nombre='{self.nombre}', tipo={self.tipo.value}, estado={self.estado.value})"
    
    def __repr__(self) -> str:
        """
        Representación técnica del recurso.
        
        Returns:
            str: Representación técnica del recurso
        """
        return (f"Recurso(id='{self.id}', nombre='{self.nombre}', "
                f"tipo={self.tipo}, estado={self.estado}, "
                f"capacidad={self.capacidad_actual}/{self.capacidad_maxima})")
