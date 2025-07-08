"""
Instalador del Planificador Inteligente
======================================

Este script instala automáticamente todas las dependencias
y configura el sistema para que funcione como aplicación
de escritorio para usuarios finales.

Características:
- Instalación automática de dependencias
- Configuración del entorno virtual
- Creación de acceso directo
- Verificación del sistema

Autor: Equipo de Desarrollo
Fecha: 2025-01-08
"""

import os
import sys
import subprocess
import platform
import json
from pathlib import Path

def log(mensaje):
    """Imprime un mensaje con formato"""
    print(f"[INSTALADOR] {mensaje}")

def verificar_python():
    """Verifica que Python esté instalado"""
    try:
        resultado = subprocess.run([sys.executable, "--version"], 
                                 capture_output=True, text=True)
        if resultado.returncode == 0:
            version = resultado.stdout.strip()
            log(f"✅ Python encontrado: {version}")
            return True
        else:
            log("❌ Python no encontrado o no funciona correctamente")
            return False
    except Exception as e:
        log(f"❌ Error verificando Python: {str(e)}")
        return False

def crear_entorno_virtual():
    """Crea un entorno virtual para la aplicación"""
    log("🔧 Creando entorno virtual...")
    
    try:
        # Crear directorio venv
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        log("✅ Entorno virtual creado")
        return True
    except Exception as e:
        log(f"❌ Error creando entorno virtual: {str(e)}")
        return False

def obtener_python_venv():
    """Obtiene la ruta del Python del entorno virtual"""
    if platform.system() == "Windows":
        return os.path.join("venv", "Scripts", "python.exe")
    else:
        return os.path.join("venv", "bin", "python")

def instalar_dependencias():
    """Instala las dependencias necesarias"""
    log("📦 Instalando dependencias...")
    
    try:
        python_venv = obtener_python_venv()
        
        # Actualizar pip
        subprocess.run([python_venv, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        
        # Instalar dependencias básicas
        dependencias = [
            "fastapi==0.105.0",
            "uvicorn==0.25.0",
            "python-multipart==0.0.6",
            "sqlalchemy==2.0.25",
            "pandas==2.1.3",
            "openpyxl==3.1.2",
            "numpy==1.25.2",
            "requests==2.31.0",
            "pydantic==2.5.0"
        ]
        
        for dep in dependencias:
            log(f"📦 Instalando {dep}...")
            subprocess.run([python_venv, "-m", "pip", "install", dep], 
                          check=True)
        
        log("✅ Todas las dependencias instaladas")
        return True
        
    except Exception as e:
        log(f"❌ Error instalando dependencias: {str(e)}")
        return False

def crear_script_ejecutable():
    """Crea un script ejecutable para iniciar la aplicación"""
    log("🚀 Creando script ejecutable...")
    
    try:
        python_venv = obtener_python_venv()
        
        if platform.system() == "Windows":
            # Script para Windows
            contenido = f"""@echo off
cd /d "{os.getcwd()}"
"{python_venv}" planificador_gui.py
pause
"""
            with open("Planificador_Inteligente.bat", "w") as f:
                f.write(contenido)
            log("✅ Script ejecutable creado: Planificador_Inteligente.bat")
            
        else:
            # Script para Linux/Mac
            contenido = f"""#!/bin/bash
cd "{os.getcwd()}"
{python_venv} planificador_gui.py
"""
            with open("Planificador_Inteligente.sh", "w") as f:
                f.write(contenido)
            os.chmod("Planificador_Inteligente.sh", 0o755)
            log("✅ Script ejecutable creado: Planificador_Inteligente.sh")
            
        return True
        
    except Exception as e:
        log(f"❌ Error creando script ejecutable: {str(e)}")
        return False

def crear_acceso_directo():
    """Crea un acceso directo en el escritorio (Windows)"""
    if platform.system() != "Windows":
        return True
        
    try:
        log("🔗 Creando acceso directo en el escritorio...")
        
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "Planificador Inteligente.lnk")
        target = os.path.join(os.getcwd(), "Planificador_Inteligente.bat")
        wDir = os.getcwd()
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = target
        shortcut.WorkingDirectory = wDir
        shortcut.Description = "Planificador Inteligente - Procesador de Excel"
        shortcut.save()
        
        log("✅ Acceso directo creado en el escritorio")
        return True
        
    except ImportError:
        log("⚠️ No se pudo crear acceso directo (faltan módulos de Windows)")
        return True
    except Exception as e:
        log(f"⚠️ Error creando acceso directo: {str(e)}")
        return True

def verificar_instalacion():
    """Verifica que la instalación funcione correctamente"""
    log("🔍 Verificando instalación...")
    
    try:
        python_venv = obtener_python_venv()
        
        # Verificar que se pueden importar los módulos principales
        test_script = """
import sys
try:
    import fastapi
    import uvicorn
    import pandas
    import openpyxl
    import tkinter
    print("✅ Todos los módulos importados correctamente")
    sys.exit(0)
except ImportError as e:
    print(f"❌ Error importando módulos: {e}")
    sys.exit(1)
"""
        
        with open("test_install.py", "w") as f:
            f.write(test_script)
        
        resultado = subprocess.run([python_venv, "test_install.py"], 
                                 capture_output=True, text=True)
        
        os.remove("test_install.py")
        
        if resultado.returncode == 0:
            log("✅ Instalación verificada correctamente")
            return True
        else:
            log(f"❌ Error en verificación: {resultado.stderr}")
            return False
            
    except Exception as e:
        log(f"❌ Error verificando instalación: {str(e)}")
        return False

def crear_configuracion():
    """Crea archivos de configuración necesarios"""
    log("⚙️ Creando configuración...")
    
    try:
        # Crear archivo de configuración
        config = {
            "version": "1.0.0",
            "servidor": {
                "host": "127.0.0.1",
                "port": 8000
            },
            "aplicacion": {
                "titulo": "Planificador Inteligente",
                "debug": False
            }
        }
        
        with open("config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        log("✅ Configuración creada")
        return True
        
    except Exception as e:
        log(f"❌ Error creando configuración: {str(e)}")
        return False

def limpiar_archivos_desarrollo():
    """Limpia archivos innecesarios para producción"""
    log("🧹 Limpiando archivos de desarrollo...")
    
    archivos_innecesarios = [
        "test_*.py",
        "prueba_*.py",
        "tutorial_*.py",
        "demo_*.py",
        "ejemplo_*.py",
        "*.pyc",
        "__pycache__",
        "*.log"
    ]
    
    try:
        import glob
        
        for patron in archivos_innecesarios:
            for archivo in glob.glob(patron):
                if os.path.isfile(archivo):
                    os.remove(archivo)
                    log(f"🗑️ Eliminado: {archivo}")
                elif os.path.isdir(archivo):
                    import shutil
                    shutil.rmtree(archivo)
                    log(f"🗑️ Eliminado directorio: {archivo}")
        
        log("✅ Archivos de desarrollo limpiados")
        return True
        
    except Exception as e:
        log(f"⚠️ Error limpiando archivos: {str(e)}")
        return True

def main():
    """Función principal del instalador"""
    print("🚀 INSTALADOR DEL PLANIFICADOR INTELIGENTE")
    print("=" * 50)
    
    # Verificar Python
    if not verificar_python():
        print("\n❌ INSTALACIÓN FALLIDA: Python no está disponible")
        input("Presiona Enter para salir...")
        return False
    
    # Crear entorno virtual
    if not crear_entorno_virtual():
        print("\n❌ INSTALACIÓN FALLIDA: No se pudo crear el entorno virtual")
        input("Presiona Enter para salir...")
        return False
    
    # Instalar dependencias
    if not instalar_dependencias():
        print("\n❌ INSTALACIÓN FALLIDA: No se pudieron instalar las dependencias")
        input("Presiona Enter para salir...")
        return False
    
    # Crear configuración
    if not crear_configuracion():
        print("\n❌ INSTALACIÓN FALLIDA: No se pudo crear la configuración")
        input("Presiona Enter para salir...")
        return False
    
    # Crear script ejecutable
    if not crear_script_ejecutable():
        print("\n❌ INSTALACIÓN FALLIDA: No se pudo crear el script ejecutable")
        input("Presiona Enter para salir...")
        return False
    
    # Crear acceso directo
    crear_acceso_directo()
    
    # Verificar instalación
    if not verificar_instalacion():
        print("\n❌ INSTALACIÓN FALLIDA: La verificación falló")
        input("Presiona Enter para salir...")
        return False
    
    # Limpiar archivos de desarrollo
    limpiar_archivos_desarrollo()
    
    print("\n🎉 ¡INSTALACIÓN COMPLETADA EXITOSAMENTE!")
    print("=" * 50)
    print("📋 CÓMO USAR LA APLICACIÓN:")
    print("   1. Ejecuta 'Planificador_Inteligente.bat' (Windows)")
    print("   2. O usa el acceso directo del escritorio")
    print("   3. La aplicación se abrirá con interfaz gráfica")
    print("   4. Sigue las instrucciones en pantalla")
    
    print("\n💡 FUNCIONALIDADES:")
    print("   ✅ Descargar plantilla Excel")
    print("   ✅ Procesar archivos Excel")
    print("   ✅ Generar reportes optimizados")
    print("   ✅ Interfaz amigable para usuarios")
    
    input("\nPresiona Enter para salir...")
    return True

if __name__ == "__main__":
    main()
