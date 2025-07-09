# Guía Completa: Integración con Excel - Sistema Planificador Inteligente

## 📋 Resumen

El **Sistema Planificador Inteligente** incluye una integración completa con Microsoft Excel que permite:

- **Leer** archivos Excel con datos de procesos y recursos
- **Analizar** la información usando algoritmos de optimización
- **Generar** reportes detallados en formato Excel
- **Descargar** resultados con métricas y recomendaciones

## 🔧 Configuración Inicial

### Prerrequisitos
```bash
# Instalar dependencias
pip install pandas openpyxl python-multipart

# Iniciar servidor
python -m uvicorn interface.api.main:app --reload
```

### URLs Base
- **Servidor**: `http://localhost:8000`
- **API Excel**: `http://localhost:8000/api/excel`

## 📊 Formato de Archivos Excel

### Estructura Requerida
El archivo Excel debe contener **exactamente** 2 hojas:

#### 1. Hoja "Procesos"
| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `Nombre` | String | Nombre del proceso | "Desarrollo Frontend" |
| `Descripcion` | String | Descripción detallada | "Crear interfaz usuario" |
| `Tipo` | String | Tipo: `rutinario`, `critico`, `urgente` | "critico" |
| `Tiempo_Estimado_Horas` | Number | Horas estimadas | 120 |
| `Prioridad` | String | Prioridad: `baja`, `media`, `alta`, `critica` | "alta" |
| `Recursos_Requeridos` | String | Habilidades separadas por comas | "frontend,react,javascript" |

#### 2. Hoja "Recursos"
| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `Nombre` | String | Nombre del recurso | "María García" |
| `Tipo` | String | Tipo: `humano`, `servidor`, `software` | "humano" |
| `Capacidad_Maxima` | Number | Horas disponibles | 40 |
| `Costo_Por_Hora` | Number | Costo por hora | 45.50 |
| `Habilidades` | String | Habilidades separadas por comas | "frontend,react,css" |

## 🚀 Endpoints Disponibles

### 1. Descargar Plantilla
```http
GET /api/excel/plantilla
```
**Respuesta**: Archivo Excel con formato correcto y datos de ejemplo

### 2. Procesar Archivo
```http
POST /api/excel/procesar
Content-Type: multipart/form-data
```
**Parámetros**: `archivo` (archivo Excel)

**Respuesta**:
```json
{
    "mensaje": "Archivo procesado exitosamente",
    "procesos_leidos": 15,
    "recursos_leidos": 10,
    "archivo_resultados": "RESULTADOS_PLANIFICACION_20250707_223512.xlsx",
    "resumen": {
        "total_procesos": 15,
        "total_recursos": 10,
        "eficiencia_proyectada": 75.5,
        "costo_total": 45230.50,
        "tiempo_total_horas": 1200.0,
        "capacidad_total_horas": 800.0
    }
}
```

### 3. Descargar Resultados
```http
GET /api/excel/descargar/{nombre_archivo}
```
**Respuesta**: Archivo Excel con resultados del análisis

## 📈 Archivo de Resultados

El archivo Excel generado contiene **4 hojas**:

### 1. Resumen Ejecutivo
- Fecha de análisis
- Métricas principales
- Costos totales
- Eficiencia proyectada

### 2. Procesos Analizados
- Todos los procesos procesados
- Datos originales con validaciones
- Formateo profesional

### 3. Recursos Analizados
- Todos los recursos disponibles
- Capacidades y costos
- Habilidades procesadas

### 4. Recomendaciones
- Sugerencias de optimización
- Mejores prácticas
- Acciones recomendadas

## 💻 Ejemplos de Uso

### Ejemplo 1: Usando Python
```python
import requests

# Procesar archivo
with open('mi_archivo.xlsx', 'rb') as f:
    files = {'archivo': f}
    response = requests.post('http://localhost:8000/api/excel/procesar', files=files)

resultado = response.json()
print(f"Eficiencia: {resultado['resumen']['eficiencia_proyectada']}%")

# Descargar resultados
archivo_resultados = resultado['archivo_resultados']
response = requests.get(f'http://localhost:8000/api/excel/descargar/{archivo_resultados}')
with open('resultados.xlsx', 'wb') as f:
    f.write(response.content)
```

### Ejemplo 2: Usando cURL
```bash
# Procesar archivo
curl -X POST "http://localhost:8000/api/excel/procesar" \
     -F "archivo=@mi_archivo.xlsx"

# Descargar resultados
curl -X GET "http://localhost:8000/api/excel/descargar/RESULTADOS_PLANIFICACION_20250707_223512.xlsx" \
     -o resultados.xlsx
```

## 🎯 Flujo Completo de Trabajo

### Paso 1: Preparación
1. **Descargar plantilla**: `GET /api/excel/plantilla`
2. **Llenar datos**: Abrir en Excel y completar con datos reales
3. **Validar formato**: Verificar nombres de columnas y tipos de datos

### Paso 2: Procesamiento
1. **Subir archivo**: `POST /api/excel/procesar`
2. **Recibir análisis**: Obtener métricas y nombre del archivo de resultados
3. **Revisar métricas**: Analizar eficiencia, costos y capacidad

### Paso 3: Resultados
1. **Descargar archivo**: `GET /api/excel/descargar/{nombre}`
2. **Abrir en Excel**: Revisar todas las hojas generadas
3. **Implementar recomendaciones**: Seguir sugerencias de optimización

## 🔍 Métricas Calculadas

### Eficiencia Proyectada
```
Eficiencia = (Capacidad Total / Tiempo Total) * 100
```

### Costo Total
```
Costo Total = Tiempo Total * Costo Promedio por Hora
```

### Análisis de Capacidad
- **Capacidad suficiente**: Cuando recursos > tiempo requerido
- **Déficit de capacidad**: Cuando tiempo requerido > recursos disponibles

## ⚠️ Consideraciones Importantes

### Validaciones
- **Nombres de columnas**: Deben ser exactos (case-sensitive)
- **Tipos de datos**: Números para horas y costos
- **Valores enum**: Tipos y prioridades deben usar valores válidos
- **Formato de archivo**: Solo `.xlsx` y `.xls`

### Limitaciones
- **Tamaño máximo**: 10MB por archivo
- **Hojas requeridas**: Exactamente "Procesos" y "Recursos"
- **Encoding**: UTF-8 recomendado

### Errores Comunes
1. **Nombres incorrectos**: Verificar nombres de columnas
2. **Tipos inválidos**: Usar valores exactos para enums
3. **Datos faltantes**: Completar todas las columnas requeridas
4. **Formato incorrecto**: Usar plantilla como referencia

## 🚀 Scripts de Prueba

### Ejecutar Tutorial Completo
```bash
python tutorial_excel.py
```

### Ejecutar Ejemplo con Datos Reales
```bash
python ejemplo_excel_real.py
```

### Ejecutar Demo Completo
```bash
python demo_excel_completo.py
```

## 📞 Soporte y Troubleshooting

### Verificar Servidor
```bash
curl http://localhost:8000/health
```

### Logs del Servidor
Los logs incluyen información detallada sobre:
- Archivos procesados
- Errores de validación
- Métricas calculadas
- Archivos generados

### Errores Frecuentes
- **500 Error**: Verificar formato de archivo y datos
- **400 Error**: Revisar estructura y nombres de columnas
- **404 Error**: Verificar que el servidor esté ejecutándose

## 🎉 Casos de Uso Exitosos

### Desarrollo de Software
- **15 procesos**, **10 recursos humanos**
- **Eficiencia**: 75% con optimización
- **Ahorro**: 20% en costos totales

### Gestión de Proyectos
- **Planificación**: 6 meses adelante
- **Recursos**: Mix de humanos y servidores
- **Optimización**: Identificación de cuellos de botella

### Consultoría
- **Análisis**: Múltiples clientes simultáneos
- **Reportes**: Generación automática
- **Recomendaciones**: Basadas en datos reales

---

**¡El sistema está listo para usar! 🚀**

Para comenzar, ejecuta el servidor y sigue el flujo completo con los scripts de ejemplo proporcionados.
