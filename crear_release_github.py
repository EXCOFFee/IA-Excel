"""
Script para crear Release en GitHub

Este script crea automáticamente un release en GitHub con los ejecutables
y toda la documentación necesaria.

Requiere:
- Tener configurado GitHub CLI (gh)
- O usar la interfaz web de GitHub

Autor: Equipo de Desarrollo
Fecha: 2025-07-08
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def crear_release_github():
    """Crea un release en GitHub con los archivos listos"""
    
    print("🚀 Creando Release v1.0.0 en GitHub...")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists("github_release"):
        print("❌ Error: No se encuentra la carpeta github_release")
        return False
    
    # Archivos a incluir en el release
    archivos = [
        "github_release/Planificador_Inteligente_v1.0.0_Installer.zip",
        "github_release/Planificador_Inteligente_v1.0.0_Standalone.exe", 
        "github_release/RELEASE_NOTES.md",
        "github_release/README_RELEASE.md",
        "github_release/CHECKSUMS.txt"
    ]
    
    # Verificar que todos los archivos existen
    for archivo in archivos:
        if not os.path.exists(archivo):
            print(f"❌ Error: No se encuentra {archivo}")
            return False
    
    print("✅ Todos los archivos encontrados")
    
    # Leer las notas de release
    with open("github_release/RELEASE_NOTES.md", "r", encoding="utf-8") as f:
        release_notes = f.read()
    
    # Comando para crear release usando GitHub CLI
    comando_gh = [
        "gh", "release", "create", "v1.0.0",
        "--title", "🚀 Planificador Inteligente v1.0.0",
        "--notes-file", "github_release/RELEASE_NOTES.md"
    ]
    
    # Agregar archivos al comando
    for archivo in archivos:
        comando_gh.append(archivo)
    
    print("\n📋 Comando a ejecutar:")
    print(" ".join(comando_gh))
    
    print("\n" + "="*60)
    print("🔧 OPCIONES PARA CREAR EL RELEASE:")
    print("="*60)
    
    print("\n🤖 OPCIÓN 1: GitHub CLI (Automático)")
    print("1. Instalar GitHub CLI: https://cli.github.com/")
    print("2. Autenticarse: gh auth login")
    print("3. Ejecutar este script nuevamente")
    
    print("\n🌐 OPCIÓN 2: Interfaz Web GitHub (Manual)")
    print("1. Ir a: https://github.com/TU_USUARIO/IA-Excel/releases")
    print("2. Clic en 'Create a new release'")
    print("3. Tag: v1.0.0")
    print("4. Title: 🚀 Planificador Inteligente v1.0.0")
    print("5. Copiar contenido de github_release/RELEASE_NOTES.md")
    print("6. Arrastrar y soltar estos archivos:")
    for archivo in archivos:
        print(f"   📁 {archivo}")
    
    print("\n📋 OPCIÓN 3: Comando Manual")
    print("Copiar y ejecutar este comando en la terminal:")
    print("\n" + " ".join(comando_gh))
    
    # Intentar ejecutar GitHub CLI
    try:
        print("\n🔄 Intentando crear release automáticamente...")
        result = subprocess.run(comando_gh, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ ¡Release creado exitosamente!")
            print("🌐 URL del release:", result.stdout.strip())
            return True
        else:
            print("⚠️ No se pudo crear automáticamente.")
            print("📝 Error:", result.stderr)
            print("👆 Usar una de las opciones manuales arriba")
            return False
            
    except FileNotFoundError:
        print("⚠️ GitHub CLI no está instalado.")
        print("👆 Usar una de las opciones manuales arriba")
        return False

def mostrar_instrucciones_web():
    """Muestra las instrucciones para crear el release manualmente"""
    
    print("\n" + "="*60)
    print("🌐 INSTRUCCIONES PARA RELEASE MANUAL EN GITHUB")
    print("="*60)
    
    print("""
1. 🌐 Ir a tu repositorio en GitHub
2. 📋 Clic en la pestaña "Releases" 
3. ➕ Clic en "Create a new release"
4. 🏷️ En "Tag version" escribir: v1.0.0
5. 📝 En "Release title" escribir: 🚀 Planificador Inteligente v1.0.0
6. 📄 En la descripción, copiar el contenido de github_release/RELEASE_NOTES.md
7. 📁 En "Attach binaries" arrastrar estos archivos:
   
   📦 Planificador_Inteligente_v1.0.0_Installer.zip (67 MB)
   ⚡ Planificador_Inteligente_v1.0.0_Standalone.exe (68 MB)
   📋 RELEASE_NOTES.md
   📖 README_RELEASE.md  
   🔐 CHECKSUMS.txt
   
8. ✅ Marcar "Set as the latest release"
9. 🚀 Clic en "Publish release"

¡Tu aplicación estará disponible para descarga! 🎉
""")

if __name__ == "__main__":
    print("🚀 Creador de Release - Planificador Inteligente")
    print("="*50)
    
    if crear_release_github():
        print("\n🎉 ¡Release creado exitosamente!")
    else:
        mostrar_instrucciones_web()
    
    print("\n✨ ¡Tu aplicación ya está lista para distribución!")
