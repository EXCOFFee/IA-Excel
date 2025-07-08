#!/usr/bin/env python3
"""
Script de Verificación Final
===========================

Verifica que todos los archivos estén en su lugar y el proyecto esté listo
"""

import os
import sys
from pathlib import Path
import json

def verificar_proyecto():
    """Verifica que el proyecto esté completo y listo"""
    
    print("🔍 Verificando estado del proyecto...")
    print("=" * 50)
    
    base_dir = Path(__file__).parent
    errores = []
    
    # Verificar estructura de directorios
    directorios_requeridos = [
        "domain",
        "app", 
        "infrastructure",
        "interface",
        "dist",
        "installer_build",
        "github_release"
    ]
    
    print("📁 Verificando estructura de directorios...")
    for dir_name in directorios_requeridos:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            print(f"✅ {dir_name}/")
        else:
            print(f"❌ {dir_name}/ - FALTA")
            errores.append(f"Directorio faltante: {dir_name}")
    
    # Verificar archivos principales
    archivos_principales = [
        "planificador_gui.py",
        "planificador.spec",
        "requirements_production.txt",
        "requirements_build.txt",
        "crear_instalador.py",
        "crear_release.py"
    ]
    
    print("\n📄 Verificando archivos principales...")
    for archivo in archivos_principales:
        archivo_path = base_dir / archivo
        if archivo_path.exists():
            print(f"✅ {archivo}")
        else:
            print(f"❌ {archivo} - FALTA")
            errores.append(f"Archivo faltante: {archivo}")
    
    # Verificar ejecutable
    print("\n⚙️ Verificando ejecutable...")
    exe_path = base_dir / "dist" / "PlanificadorInteligente.exe"
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ PlanificadorInteligente.exe ({size_mb:.1f} MB)")
    else:
        print("❌ PlanificadorInteligente.exe - FALTA")
        errores.append("Ejecutable no encontrado")
    
    # Verificar instalador
    print("\n📦 Verificando instalador...")
    installer_dir = base_dir / "installer_build"
    if installer_dir.exists():
        zip_files = list(installer_dir.glob("*.zip"))
        if zip_files:
            for zip_file in zip_files:
                size_mb = zip_file.stat().st_size / (1024 * 1024)
                print(f"✅ {zip_file.name} ({size_mb:.1f} MB)")
        else:
            print("❌ No se encontraron archivos ZIP del instalador")
            errores.append("Instalador ZIP no encontrado")
    else:
        print("❌ Directorio installer_build no encontrado")
        errores.append("Directorio installer_build faltante")
    
    # Verificar release
    print("\n🚀 Verificando release...")
    release_dir = base_dir / "github_release"
    if release_dir.exists():
        release_files = list(release_dir.glob("*"))
        if release_files:
            total_size = 0
            for file_path in release_files:
                if file_path.is_file():
                    size_mb = file_path.stat().st_size / (1024 * 1024)
                    total_size += size_mb
                    print(f"✅ {file_path.name} ({size_mb:.1f} MB)")
            print(f"📊 Tamaño total del release: {total_size:.1f} MB")
        else:
            print("❌ No se encontraron archivos de release")
            errores.append("Archivos de release no encontrados")
    else:
        print("❌ Directorio github_release no encontrado")
        errores.append("Directorio github_release faltante")
    
    # Verificar documentación
    print("\n📚 Verificando documentación...")
    docs_requeridos = [
        "README.md",
    ]
    
    for doc in docs_requeridos:
        doc_path = base_dir / doc
        if doc_path.exists():
            print(f"✅ {doc}")
        else:
            print(f"❌ {doc} - FALTA")
            errores.append(f"Documentación faltante: {doc}")
    
    # Verificar archivos de configuración
    print("\n⚙️ Verificando configuración...")
    config_files = [
        "config.json",
        "CHECKSUMS.txt",
        "RELEASE_NOTES.md",
        "README_RELEASE.md"
    ]
    
    for config_file in config_files:
        # Buscar en varios directorios
        found = False
        for search_dir in [base_dir, base_dir / "github_release", base_dir / "installer_build" / "Planificador_Inteligente"]:
            if search_dir.exists():
                config_path = search_dir / config_file
                if config_path.exists():
                    print(f"✅ {config_file} (en {search_dir.name})")
                    found = True
                    break
        
        if not found:
            print(f"❌ {config_file} - FALTA")
            errores.append(f"Archivo de configuración faltante: {config_file}")
    
    # Mostrar resumen
    print("\n" + "=" * 50)
    print("📊 RESUMEN DE VERIFICACIÓN")
    print("=" * 50)
    
    if errores:
        print(f"❌ {len(errores)} errores encontrados:")
        for error in errores:
            print(f"   • {error}")
        print("\n⚠️ EL PROYECTO NECESITA CORRECCIONES")
        return False
    else:
        print("✅ TODOS LOS ARCHIVOS ESTÁN EN SU LUGAR")
        print("✅ EL PROYECTO ESTÁ 100% COMPLETO")
        print("✅ LISTO PARA DISTRIBUCIÓN")
        
        # Mostrar estadísticas finales
        print("\n📈 ESTADÍSTICAS DEL PROYECTO:")
        print("-" * 30)
        
        # Contar archivos Python
        py_files = list(base_dir.glob("**/*.py"))
        print(f"📄 Archivos Python: {len(py_files)}")
        
        # Contar líneas de código
        total_lines = 0
        for py_file in py_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    total_lines += len(f.readlines())
            except:
                pass
        print(f"📝 Líneas de código: {total_lines:,}")
        
        # Tamaño del ejecutable
        if exe_path.exists():
            exe_size = exe_path.stat().st_size / (1024 * 1024)
            print(f"⚙️ Tamaño ejecutable: {exe_size:.1f} MB")
        
        # Tamaño total del release
        if release_dir.exists():
            total_release_size = 0
            for file_path in release_dir.glob("*"):
                if file_path.is_file():
                    total_release_size += file_path.stat().st_size
            print(f"📦 Tamaño release: {total_release_size / (1024 * 1024):.1f} MB")
        
        print("\n🎉 ¡PROYECTO COMPLETADO EXITOSAMENTE!")
        return True

def mostrar_instrucciones_github():
    """Muestra instrucciones para subir a GitHub"""
    
    print("\n🚀 INSTRUCCIONES PARA SUBIR A GITHUB:")
    print("=" * 40)
    print("1. Crear nuevo repositorio en GitHub")
    print("2. Subir código fuente:")
    print("   git init")
    print("   git add .")
    print("   git commit -m 'Planificador Inteligente v1.0.0 - Release inicial'")
    print("   git branch -M main")
    print("   git remote add origin https://github.com/tu-usuario/planificador-inteligente.git")
    print("   git push -u origin main")
    print()
    print("3. Crear release:")
    print("   - Ir a GitHub > Releases > Create new release")
    print("   - Tag: v1.0.0")
    print("   - Title: 🚀 Planificador Inteligente v1.0.0")
    print("   - Descripción: Copiar RELEASE_NOTES.md")
    print("   - Subir archivos binarios desde github_release/")
    print()
    print("4. Archivos a subir:")
    print("   - Planificador_Inteligente_v1.0.0_Installer.zip")
    print("   - Planificador_Inteligente_v1.0.0_Standalone.exe")
    print("   - CHECKSUMS.txt")
    print()
    print("5. Marcar como 'Latest release' y publicar")

if __name__ == "__main__":
    try:
        if verificar_proyecto():
            mostrar_instrucciones_github()
        else:
            print("\n⚠️ Corrija los errores antes de continuar")
    except Exception as e:
        print(f"\n❌ Error durante la verificación: {e}")
    
    input("\nPresione Enter para continuar...")
