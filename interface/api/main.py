"""
Aplicación Principal FastAPI

Este módulo contiene la configuración y inicialización de la aplicación
FastAPI que expone la API REST del sistema de planificación inteligente.

Funcionalidades:
- Configuración de la aplicación FastAPI
- Middleware de CORS y seguridad
- Registro de rutas y endpoints
- Manejo global de excepciones
- Documentación automática con Swagger/OpenAPI
- Configuración de logging

Principios SOLID aplicados:
- Single Responsibility: Solo configura la aplicación principal
- Dependency Inversion: Inyecta dependencias en los endpoints
- Open/Closed: Extensible para nuevas rutas

Autor: Equipo de Desarrollo
Fecha: 2025-07-07
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import logging
from contextlib import asynccontextmanager
from typing import Dict, Any
import uvicorn
import os
from pathlib import Path

# Importar rutas
from interface.api.routes.procesos import router as procesos_router
from interface.api.routes.planeador import router as planeador_router


# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Maneja el ciclo de vida de la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    # Startup
    logger.info("Iniciando aplicación Planificador Inteligente")
    
    # Inicializar base de datos
    try:
        from infrastructure.database.config import create_tables
        create_tables()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación Planificador Inteligente")
    
    # Limpiar recursos si es necesario
    # cerrar_conexiones_bd()
    # limpiar_servicios()


def crear_aplicacion() -> FastAPI:
    """
    Crea y configura la aplicación FastAPI.
    
    Returns:
        FastAPI: Instancia de la aplicación configurada
    """
    # Crear aplicación FastAPI
    app = FastAPI(
        title="Planificador Inteligente Multiplataforma",
        description="""
        Sistema inteligente de planificación y asignación de procesos que determina 
        cuántos procesos pueden ejecutarse por semana, con qué personal y cómo 
        distribuir la carga para optimizar tiempos y recursos.
        
        ## Características Principales
        
        * **Importación de Excel**: Procesa archivos Excel con datos de procesos y recursos
        * **Cálculo de Capacidad**: Determina capacidad semanal de ejecución
        * **Optimización de Recursos**: Distribución óptima de recursos
        * **Reportes y Análisis**: Genera reportes detallados y visualizaciones
        * **APIs REST**: Acceso programático completo
        
        ## Casos de Uso
        
        * Planificación de recursos empresariales
        * Gestión de proyectos y tareas
        * Optimización de procesos operativos
        * Análisis de capacidad y rendimiento
        
        ## Tecnologías
        
        * FastAPI para la API REST
        * Python con arquitectura Clean Architecture
        * Procesamiento de Excel con pandas/openpyxl
        * Algoritmos de optimización avanzados
        """,
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    
    # Configurar CORS
    configurar_cors(app)
    
    # Registrar middleware
    registrar_middleware(app)
    
    # Registrar rutas
    registrar_rutas(app)
    
    # Registrar manejadores de errores
    registrar_manejadores_errores(app)
    
    # Configurar OpenAPI personalizado
    configurar_openapi(app)
    
    return app


def configurar_cors(app: FastAPI) -> None:
    """
    Configura CORS para la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    # Obtener orígenes permitidos desde variables de entorno
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )
    
    logger.info(f"CORS configurado con orígenes: {origins}")


def registrar_middleware(app: FastAPI) -> None:
    """
    Registra middleware personalizado.
    
    Args:
        app: Instancia de FastAPI
    """
    
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """
        Middleware para logging de requests.
        
        Args:
            request: Request HTTP
            call_next: Siguiente middleware
            
        Returns:
            Response: Respuesta HTTP
        """
        # Log del request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Procesar request
        response = await call_next(request)
        
        # Log del response
        logger.info(f"Response: {response.status_code}")
        
        return response


def registrar_rutas(app: FastAPI) -> None:
    """
    Registra todas las rutas de la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    # Ruta de salud
    @app.get("/health", tags=["Health"])
    async def health_check():
        """
        Endpoint de verificación de salud del sistema.
        
        Returns:
            Dict: Estado del sistema
        """
        return {
            "status": "healthy",
            "service": "Planificador Inteligente",
            "version": "1.0.0",
            "timestamp": "2025-07-07T00:00:00Z"
        }
    
    # Ruta raíz
    @app.get("/", tags=["Root"])
    async def root():
        """
        Endpoint raíz con información del sistema.
        
        Returns:
            Dict: Información del sistema
        """
        return {
            "message": "Planificador Inteligente Multiplataforma API",
            "version": "1.0.0",
            "documentation": "/docs",
            "redoc": "/redoc",
            "health": "/health"
        }
    
    # Registrar rutas de módulos
    app.include_router(procesos_router, prefix="/api/procesos", tags=["Procesos"])
    app.include_router(planeador_router, prefix="/api/planeador", tags=["Planeador"])
    
    # Importar y registrar rutas de Excel
    from interface.api.routes.excel import router as excel_router
    app.include_router(excel_router, prefix="/api/excel", tags=["Excel"])
    
    logger.info("Rutas registradas exitosamente")


def registrar_manejadores_errores(app: FastAPI) -> None:
    """
    Registra manejadores de errores personalizados.
    
    Args:
        app: Instancia de FastAPI
    """
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """
        Manejador de excepciones HTTP.
        
        Args:
            request: Request HTTP
            exc: Excepción HTTP
            
        Returns:
            JSONResponse: Respuesta JSON con el error
        """
        logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "code": exc.status_code,
                    "message": exc.detail,
                    "type": "HTTP_EXCEPTION"
                }
            }
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """
        Manejador de excepciones generales.
        
        Args:
            request: Request HTTP
            exc: Excepción general
            
        Returns:
            JSONResponse: Respuesta JSON con el error
        """
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": 500,
                    "message": "Error interno del servidor",
                    "type": "INTERNAL_SERVER_ERROR"
                }
            }
        )


def configurar_openapi(app: FastAPI) -> None:
    """
    Configura el esquema OpenAPI personalizado.
    
    Args:
        app: Instancia de FastAPI
    """
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        
        openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            description=app.description,
            routes=app.routes,
        )
        
        # Personalizar esquema OpenAPI
        openapi_schema["info"]["x-logo"] = {
            "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        }
        
        # Agregar información adicional
        openapi_schema["info"]["contact"] = {
            "name": "Equipo de Desarrollo",
            "email": "desarrollo@planificador.com",
            "url": "https://planificador.com"
        }
        
        openapi_schema["info"]["license"] = {
            "name": "MIT",
            "url": "https://opensource.org/licenses/MIT"
        }
        
        # Agregar tags
        openapi_schema["tags"] = [
            {
                "name": "Procesos",
                "description": "Operaciones relacionadas con procesos"
            },
            {
                "name": "Planeador",
                "description": "Operaciones de planificación y optimización"
            },
            {
                "name": "Health",
                "description": "Verificación de salud del sistema"
            }
        ]
        
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    
    app.openapi = custom_openapi


# Crear instancia de la aplicación
app = crear_aplicacion()


def main():
    """
    Función principal para ejecutar el servidor.
    """
    # Configuración del servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    logger.info(f"Iniciando servidor en {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Documentación disponible en: http://{host}:{port}/docs")
    
    # Ejecutar servidor
    uvicorn.run(
        "interface.api.main:app",
        host=host,
        port=port,
        reload=debug,
        access_log=True,
        log_level="info" if not debug else "debug"
    )


if __name__ == "__main__":
    main()
