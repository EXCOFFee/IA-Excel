"""
Entidad Proceso - Modelo de Dominio

Esta entidad representa un proceso de negocio que puede ser ejecutado
por el sistema. Encapsula todas las propiedades y comportamientos
relacionados con un proceso específico.

Principios SOLID aplicados:
- Single Responsibility: Solo maneja la lógica de procesos
- Open/Closed: Extensible para nuevos tipos de procesos
- Liskov Substitution: Las subclases pueden sustituir a la clase base

Autor: Equipo de Desarrollo
Fecha: 2025-07-07
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid


class EstadoProceso(Enum):
    """
    Enumeración de los posibles estados de un proceso.
    
    Estados:
        PENDIENTE: Proceso creado pero no iniciado
        EN_PROGRESO: Proceso actualmente en ejecución
        COMPLETADO: Proceso terminado exitosamente
        PAUSADO: Proceso temporalmente detenido
        CANCELADO: Proceso terminado sin completar
        ERROR: Proceso terminado con errores
    """
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADO = "completado"
    PAUSADO = "pausado"
    CANCELADO = "cancelado"
    ERROR = "error"


class TipoProceso(Enum):
    """
    Enumeración de los tipos de procesos disponibles.
    
    Tipos:
        RUTINARIO: Procesos que se ejecutan regularmente
        ESPECIAL: Procesos únicos o especiales
        URGENTE: Procesos de alta prioridad
        MANTENIMIENTO: Procesos de mantenimiento del sistema
    """
    RUTINARIO = "rutinario"
    ESPECIAL = "especial"
    URGENTE = "urgente"
    MANTENIMIENTO = "mantenimiento"


class NivelPrioridad(Enum):
    """
    Enumeración de los niveles de prioridad.
    
    Niveles:
        BAJA: Prioridad baja (1-3)
        MEDIA: Prioridad media (4-6)
        ALTA: Prioridad alta (7-9)
        CRITICA: Prioridad crítica (10)
    """
    BAJA = 1
    MEDIA = 5
    ALTA = 8
    CRITICA = 10


@dataclass
class Proceso:
    """
    Entidad que representa un proceso de negocio.
    
    Esta clase encapsula toda la información y comportamientos
    relacionados con un proceso que puede ser ejecutado por el sistema.
    
    Attributes:
        id: Identificador único del proceso
        nombre: Nombre descriptivo del proceso
        descripcion: Descripción detallada del proceso
        tipo: Tipo de proceso según TipoProceso
        estado: Estado actual del proceso
        prioridad: Nivel de prioridad del proceso
        tiempo_estimado_horas: Tiempo estimado de ejecución en horas
        tiempo_real_horas: Tiempo real de ejecución (si está disponible)
        recursos_requeridos: Lista de recursos necesarios
        dependencias: Lista de IDs de procesos que deben completarse antes
        fecha_creacion: Fecha de creación del proceso
        fecha_inicio: Fecha de inicio de ejecución
        fecha_fin: Fecha de finalización
        fecha_limite: Fecha límite para completar el proceso
        creado_por: Usuario que creó el proceso
        asignado_a: Usuario asignado al proceso
        notas: Notas adicionales sobre el proceso
        metadatos: Datos adicionales del proceso
    """
    
    # Campos obligatorios
    nombre: str
    descripcion: str
    tipo: TipoProceso
    tiempo_estimado_horas: float
    prioridad: NivelPrioridad = NivelPrioridad.MEDIA
    
    # Campos con valores por defecto
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    estado: EstadoProceso = EstadoProceso.PENDIENTE
    tiempo_real_horas: Optional[float] = None
    recursos_requeridos: List[str] = field(default_factory=list)
    dependencias: List[str] = field(default_factory=list)
    
    # Campos de fechas
    fecha_creacion: datetime = field(default_factory=datetime.now)
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    fecha_limite: Optional[datetime] = None
    
    # Campos de usuarios
    creado_por: Optional[str] = None
    asignado_a: Optional[str] = None
    
    # Campos adicionales
    notas: str = ""
    metadatos: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """
        Validaciones que se ejecutan después de la inicialización.
        
        Raises:
            ValueError: Si los datos son inválidos
        """
        self._validar_datos()
    
    def _validar_datos(self) -> None:
        """
        Valida la consistencia de los datos del proceso.
        
        Raises:
            ValueError: Si los datos son inválidos
        """
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del proceso no puede estar vacío")
        
        if self.tiempo_estimado_horas <= 0:
            raise ValueError("El tiempo estimado debe ser mayor a 0")
        
        if self.tiempo_real_horas is not None and self.tiempo_real_horas < 0:
            raise ValueError("El tiempo real no puede ser negativo")
        
        if self.fecha_inicio and self.fecha_fin:
            if self.fecha_inicio >= self.fecha_fin:
                raise ValueError("La fecha de inicio debe ser anterior a la fecha de fin")
        
        if self.fecha_limite and self.fecha_creacion:
            if self.fecha_limite <= self.fecha_creacion:
                raise ValueError("La fecha límite debe ser posterior a la fecha de creación")
    
    def iniciar(self, usuario: Optional[str] = None) -> None:
        """
        Inicia la ejecución del proceso.
        
        Args:
            usuario: Usuario que inicia el proceso
            
        Raises:
            ValueError: Si el proceso no puede iniciarse
        """
        if self.estado != EstadoProceso.PENDIENTE:
            raise ValueError(f"No se puede iniciar un proceso en estado {self.estado.value}")
        
        self.estado = EstadoProceso.EN_PROGRESO
        self.fecha_inicio = datetime.now()
        
        if usuario:
            self.asignado_a = usuario
    
    def pausar(self, motivo: str = "") -> None:
        """
        Pausa la ejecución del proceso.
        
        Args:
            motivo: Motivo de la pausa
            
        Raises:
            ValueError: Si el proceso no puede pausarse
        """
        if self.estado != EstadoProceso.EN_PROGRESO:
            raise ValueError(f"No se puede pausar un proceso en estado {self.estado.value}")
        
        self.estado = EstadoProceso.PAUSADO
        
        if motivo:
            self.agregar_nota(f"Pausado: {motivo}")
    
    def reanudar(self) -> None:
        """
        Reanuda la ejecución del proceso.
        
        Raises:
            ValueError: Si el proceso no puede reanudarse
        """
        if self.estado != EstadoProceso.PAUSADO:
            raise ValueError(f"No se puede reanudar un proceso en estado {self.estado.value}")
        
        self.estado = EstadoProceso.EN_PROGRESO
        self.agregar_nota("Proceso reanudado")
    
    def completar(self, tiempo_real: Optional[float] = None) -> None:
        """
        Marca el proceso como completado.
        
        Args:
            tiempo_real: Tiempo real de ejecución en horas
            
        Raises:
            ValueError: Si el proceso no puede completarse
        """
        if self.estado not in [EstadoProceso.EN_PROGRESO, EstadoProceso.PAUSADO]:
            raise ValueError(f"No se puede completar un proceso en estado {self.estado.value}")
        
        self.estado = EstadoProceso.COMPLETADO
        self.fecha_fin = datetime.now()
        
        if tiempo_real is not None:
            self.tiempo_real_horas = tiempo_real
        elif self.fecha_inicio:
            # Calcular tiempo real basado en fechas
            duracion = self.fecha_fin - self.fecha_inicio
            self.tiempo_real_horas = duracion.total_seconds() / 3600
    
    def cancelar(self, motivo: str = "") -> None:
        """
        Cancela la ejecución del proceso.
        
        Args:
            motivo: Motivo de la cancelación
            
        Raises:
            ValueError: Si el proceso no puede cancelarse
        """
        if self.estado == EstadoProceso.COMPLETADO:
            raise ValueError("No se puede cancelar un proceso completado")
        
        self.estado = EstadoProceso.CANCELADO
        self.fecha_fin = datetime.now()
        
        if motivo:
            self.agregar_nota(f"Cancelado: {motivo}")
    
    def marcar_error(self, mensaje_error: str) -> None:
        """
        Marca el proceso como erróneo.
        
        Args:
            mensaje_error: Descripción del error
        """
        self.estado = EstadoProceso.ERROR
        self.fecha_fin = datetime.now()
        self.agregar_nota(f"Error: {mensaje_error}")
    
    def agregar_nota(self, nota: str) -> None:
        """
        Agrega una nota al proceso.
        
        Args:
            nota: Texto de la nota a agregar
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        nueva_nota = f"[{timestamp}] {nota}"
        
        if self.notas:
            self.notas += f"\n{nueva_nota}"
        else:
            self.notas = nueva_nota
    
    def agregar_dependencia(self, proceso_id: str) -> None:
        """
        Agrega una dependencia al proceso.
        
        Args:
            proceso_id: ID del proceso del cual depende
        """
        if proceso_id not in self.dependencias:
            self.dependencias.append(proceso_id)
    
    def remover_dependencia(self, proceso_id: str) -> None:
        """
        Remueve una dependencia del proceso.
        
        Args:
            proceso_id: ID del proceso a remover de las dependencias
        """
        if proceso_id in self.dependencias:
            self.dependencias.remove(proceso_id)
    
    def agregar_recurso_requerido(self, recurso: str) -> None:
        """
        Agrega un recurso requerido al proceso.
        
        Args:
            recurso: Nombre del recurso requerido
        """
        if recurso not in self.recursos_requeridos:
            self.recursos_requeridos.append(recurso)
    
    def remover_recurso_requerido(self, recurso: str) -> None:
        """
        Remueve un recurso requerido del proceso.
        
        Args:
            recurso: Nombre del recurso a remover
        """
        if recurso in self.recursos_requeridos:
            self.recursos_requeridos.remove(recurso)
    
    def calcular_progreso(self) -> float:
        """
        Calcula el progreso del proceso como porcentaje.
        
        Returns:
            float: Progreso del proceso (0.0 a 1.0)
        """
        if self.estado == EstadoProceso.COMPLETADO:
            return 1.0
        elif self.estado == EstadoProceso.PENDIENTE:
            return 0.0
        elif self.estado in [EstadoProceso.CANCELADO, EstadoProceso.ERROR]:
            return 0.0
        elif self.estado in [EstadoProceso.EN_PROGRESO, EstadoProceso.PAUSADO]:
            if self.fecha_inicio and self.tiempo_estimado_horas:
                tiempo_transcurrido = (datetime.now() - self.fecha_inicio).total_seconds() / 3600
                progreso = min(tiempo_transcurrido / self.tiempo_estimado_horas, 1.0)
                return progreso
            return 0.5  # Progreso estimado si no hay datos precisos
        
        return 0.0
    
    def esta_vencido(self) -> bool:
        """
        Verifica si el proceso está vencido.
        
        Returns:
            bool: True si el proceso está vencido
        """
        if not self.fecha_limite:
            return False
        
        if self.estado == EstadoProceso.COMPLETADO:
            return self.fecha_fin and self.fecha_fin > self.fecha_limite
        
        return datetime.now() > self.fecha_limite
    
    def puede_ejecutarse(self) -> bool:
        """
        Verifica si el proceso puede ejecutarse (no tiene dependencias pendientes).
        
        Returns:
            bool: True si el proceso puede ejecutarse
        """
        # Por simplicidad, asumimos que puede ejecutarse si está pendiente
        # En una implementación real, se verificarían las dependencias
        return self.estado == EstadoProceso.PENDIENTE
    
    def tiempo_restante_estimado(self) -> Optional[float]:
        """
        Calcula el tiempo restante estimado para completar el proceso.
        
        Returns:
            Optional[float]: Tiempo restante en horas, None si no se puede calcular
        """
        if self.estado == EstadoProceso.COMPLETADO:
            return 0.0
        
        if self.estado == EstadoProceso.PENDIENTE:
            return self.tiempo_estimado_horas
        
        if self.estado in [EstadoProceso.EN_PROGRESO, EstadoProceso.PAUSADO]:
            if self.fecha_inicio:
                tiempo_transcurrido = (datetime.now() - self.fecha_inicio).total_seconds() / 3600
                tiempo_restante = max(0, self.tiempo_estimado_horas - tiempo_transcurrido)
                return tiempo_restante
        
        return None
    
    def obtener_resumen(self) -> Dict[str, Any]:
        """
        Obtiene un resumen del proceso para reportes.
        
        Returns:
            Dict[str, Any]: Resumen del proceso
        """
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo.value,
            "estado": self.estado.value,
            "prioridad": self.prioridad.value,
            "tiempo_estimado": self.tiempo_estimado_horas,
            "tiempo_real": self.tiempo_real_horas,
            "progreso": self.calcular_progreso(),
            "vencido": self.esta_vencido(),
            "puede_ejecutarse": self.puede_ejecutarse(),
            "recursos_requeridos": self.recursos_requeridos,
            "fecha_creacion": self.fecha_creacion.isoformat() if self.fecha_creacion else None,
            "fecha_limite": self.fecha_limite.isoformat() if self.fecha_limite else None,
            "asignado_a": self.asignado_a
        }
    
    def __str__(self) -> str:
        """
        Representación en cadena del proceso.
        
        Returns:
            str: Representación legible del proceso
        """
        return f"Proceso(id={self.id[:8]}..., nombre='{self.nombre}', estado={self.estado.value})"
    
    def __repr__(self) -> str:
        """
        Representación técnica del proceso.
        
        Returns:
            str: Representación técnica del proceso
        """
        return (f"Proceso(id='{self.id}', nombre='{self.nombre}', "
                f"tipo={self.tipo}, estado={self.estado}, "
                f"tiempo_estimado={self.tiempo_estimado_horas})")
