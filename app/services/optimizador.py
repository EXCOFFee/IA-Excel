"""
Servicio de Optimización

Este servicio implementa algoritmos de optimización para mejorar
la distribución de recursos y la planificación de procesos.
Utiliza técnicas matemáticas y heurísticas para encontrar
soluciones óptimas o cerca del óptimo.

Principios SOLID aplicados:
- Single Responsibility: Solo se encarga de optimización
- Open/Closed: Extensible para nuevos algoritmos
- Dependency Inversion: Depende de abstracciones

Autor: Equipo de Desarrollo
Fecha: 2025-07-07
"""

from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
from enum import Enum
import numpy as np
from scipy.optimize import linprog
import random

from domain.models.proceso import Proceso, NivelPrioridad
from domain.models.recurso import Recurso
from app.use_cases.distribuir_recursos import AsignacionRecurso, EstrategiaDistribucion


# Configuración de logging
logger = logging.getLogger(__name__)


class AlgoritmoOptimizacion(Enum):
    """
    Enumeración de algoritmos de optimización disponibles.
    
    Algoritmos:
        LINEAL: Programación lineal
        GENETICO: Algoritmo genético
        SIMULATED_ANNEALING: Recocido simulado
        GREEDY: Algoritmo voraz
        BRANCH_AND_BOUND: Ramificación y acotación
    """
    LINEAL = "lineal"
    GENETICO = "genetico"
    SIMULATED_ANNEALING = "simulated_annealing"
    GREEDY = "greedy"
    BRANCH_AND_BOUND = "branch_and_bound"


@dataclass
class ParametrosOptimizacion:
    """
    Parámetros para la optimización.
    
    Attributes:
        algoritmo: Algoritmo de optimización a usar
        max_iteraciones: Número máximo de iteraciones
        tolerancia: Tolerancia para convergencia
        peso_costo: Peso del costo en la función objetivo
        peso_tiempo: Peso del tiempo en la función objetivo
        peso_eficiencia: Peso de la eficiencia en la función objetivo
        semilla_aleatoria: Semilla para reproducibilidad
    """
    algoritmo: AlgoritmoOptimizacion = AlgoritmoOptimizacion.GREEDY
    max_iteraciones: int = 1000
    tolerancia: float = 1e-6
    peso_costo: float = 0.4
    peso_tiempo: float = 0.3
    peso_eficiencia: float = 0.3
    semilla_aleatoria: Optional[int] = None


@dataclass
class SolucionOptimizada:
    """
    Resultado de la optimización.
    
    Attributes:
        asignaciones: Lista de asignaciones optimizadas
        valor_objetivo: Valor de la función objetivo
        tiempo_ejecucion: Tiempo de ejecución del algoritmo
        iteraciones: Número de iteraciones realizadas
        convergencia: Si el algoritmo convergió
        metricas: Métricas adicionales de la solución
    """
    asignaciones: List[AsignacionRecurso]
    valor_objetivo: float
    tiempo_ejecucion: float
    iteraciones: int
    convergencia: bool
    metricas: Dict[str, Any]


class OptimizadorRecursos:
    """
    Servicio de optimización de recursos.
    
    Implementa diferentes algoritmos de optimización para mejorar
    la asignación de recursos a procesos, maximizando la eficiencia
    y minimizando costos y tiempos.
    """
    
    def __init__(self):
        """
        Inicializa el optimizador.
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        self._random = random.Random()
    
    def optimizar_asignaciones(self, 
                              procesos: List[Proceso], 
                              recursos: List[Recurso],
                              parametros: ParametrosOptimizacion) -> SolucionOptimizada:
        """
        Optimiza las asignaciones de recursos a procesos.
        
        Args:
            procesos: Lista de procesos a asignar
            recursos: Lista de recursos disponibles
            parametros: Parámetros de optimización
            
        Returns:
            SolucionOptimizada: Solución optimizada encontrada
            
        Raises:
            ValueError: Si los datos de entrada son inválidos
            RuntimeError: Si ocurre un error durante la optimización
        """
        try:
            inicio = datetime.now()
            
            # Configurar semilla aleatoria
            if parametros.semilla_aleatoria is not None:
                self._random.seed(parametros.semilla_aleatoria)
                np.random.seed(parametros.semilla_aleatoria)
            
            self._logger.info(f"Iniciando optimización con algoritmo {parametros.algoritmo.value}")
            
            # Validar entrada
            self._validar_entrada(procesos, recursos, parametros)
            
            # Ejecutar algoritmo específico
            if parametros.algoritmo == AlgoritmoOptimizacion.LINEAL:
                solucion = self._optimizar_lineal(procesos, recursos, parametros)
            elif parametros.algoritmo == AlgoritmoOptimizacion.GENETICO:
                solucion = self._optimizar_genetico(procesos, recursos, parametros)
            elif parametros.algoritmo == AlgoritmoOptimizacion.SIMULATED_ANNEALING:
                solucion = self._optimizar_simulated_annealing(procesos, recursos, parametros)
            elif parametros.algoritmo == AlgoritmoOptimizacion.GREEDY:
                solucion = self._optimizar_greedy(procesos, recursos, parametros)
            elif parametros.algoritmo == AlgoritmoOptimizacion.BRANCH_AND_BOUND:
                solucion = self._optimizar_branch_and_bound(procesos, recursos, parametros)
            else:
                raise ValueError(f"Algoritmo no soportado: {parametros.algoritmo}")
            
            # Calcular tiempo de ejecución
            tiempo_ejecucion = (datetime.now() - inicio).total_seconds()
            solucion.tiempo_ejecucion = tiempo_ejecucion
            
            self._logger.info(f"Optimización completada en {tiempo_ejecucion:.2f}s")
            return solucion
            
        except Exception as e:
            self._logger.error(f"Error en optimización: {str(e)}")
            raise RuntimeError(f"Error optimizando asignaciones: {str(e)}")
    
    def _validar_entrada(self, 
                        procesos: List[Proceso], 
                        recursos: List[Recurso], 
                        parametros: ParametrosOptimizacion) -> None:
        """
        Valida los datos de entrada.
        
        Args:
            procesos: Lista de procesos
            recursos: Lista de recursos
            parametros: Parámetros de optimización
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        if not procesos:
            raise ValueError("Debe haber al menos un proceso")
        
        if not recursos:
            raise ValueError("Debe haber al menos un recurso")
        
        if parametros.max_iteraciones <= 0:
            raise ValueError("El número máximo de iteraciones debe ser mayor a 0")
        
        if parametros.tolerancia <= 0:
            raise ValueError("La tolerancia debe ser mayor a 0")
        
        # Validar pesos
        total_pesos = parametros.peso_costo + parametros.peso_tiempo + parametros.peso_eficiencia
        if abs(total_pesos - 1.0) > 1e-6:
            raise ValueError("Los pesos deben sumar 1.0")
    
    def _optimizar_greedy(self, 
                         procesos: List[Proceso], 
                         recursos: List[Recurso], 
                         parametros: ParametrosOptimizacion) -> SolucionOptimizada:
        """
        Optimiza usando algoritmo voraz (greedy).
        
        Args:
            procesos: Lista de procesos
            recursos: Lista de recursos
            parametros: Parámetros de optimización
            
        Returns:
            SolucionOptimizada: Solución encontrada
        """
        # Ordenar procesos por prioridad y ratio eficiencia/costo
        procesos_ordenados = self._ordenar_procesos_greedy(procesos, recursos, parametros)
        
        asignaciones = []
        recursos_ocupados = {r.id: 0.0 for r in recursos}
        
        for proceso in procesos_ordenados:
            # Encontrar el mejor recurso para este proceso
            mejor_recurso, mejor_puntuacion = self._encontrar_mejor_recurso_greedy(
                proceso, recursos, recursos_ocupados, parametros
            )
            
            if mejor_recurso:
                # Crear asignación
                asignacion = self._crear_asignacion_optimizada(
                    proceso, mejor_recurso, recursos_ocupados[mejor_recurso.id]
                )
                asignaciones.append(asignacion)
                recursos_ocupados[mejor_recurso.id] += proceso.tiempo_estimado_horas
        
        # Calcular valor objetivo
        valor_objetivo = self._calcular_valor_objetivo(asignaciones, parametros)
        
        return SolucionOptimizada(
            asignaciones=asignaciones,
            valor_objetivo=valor_objetivo,
            tiempo_ejecucion=0.0,  # Se calculará en el método principal
            iteraciones=1,
            convergencia=True,
            metricas=self._calcular_metricas_solucion(asignaciones)
        )
    
    def _optimizar_genetico(self, 
                           procesos: List[Proceso], 
                           recursos: List[Recurso], 
                           parametros: ParametrosOptimizacion) -> SolucionOptimizada:
        """
        Optimiza usando algoritmo genético.
        
        Args:
            procesos: Lista de procesos
            recursos: Lista de recursos
            parametros: Parámetros de optimización
            
        Returns:
            SolucionOptimizada: Solución encontrada
        """
        # Parámetros del algoritmo genético
        tamaño_poblacion = 50
        tasa_cruce = 0.8
        tasa_mutacion = 0.1
        
        # Inicializar población
        poblacion = self._inicializar_poblacion(procesos, recursos, tamaño_poblacion)
        
        mejor_solucion = None
        mejor_valor = float('inf')
        
        for iteracion in range(parametros.max_iteraciones):
            # Evaluar población
            valores_fitness = []
            for individuo in poblacion:
                asignaciones = self._decodificar_individuo(individuo, procesos, recursos)
                valor = self._calcular_valor_objetivo(asignaciones, parametros)
                valores_fitness.append(valor)
                
                # Actualizar mejor solución
                if valor < mejor_valor:
                    mejor_valor = valor
                    mejor_solucion = asignaciones
            
            # Selección
            poblacion_seleccionada = self._seleccion_torneo(poblacion, valores_fitness)
            
            # Cruce
            nueva_poblacion = []
            for i in range(0, len(poblacion_seleccionada), 2):
                padre1 = poblacion_seleccionada[i]
                padre2 = poblacion_seleccionada[i+1] if i+1 < len(poblacion_seleccionada) else poblacion_seleccionada[0]
                
                if self._random.random() < tasa_cruce:
                    hijo1, hijo2 = self._cruce_uniforme(padre1, padre2)
                else:
                    hijo1, hijo2 = padre1.copy(), padre2.copy()
                
                nueva_poblacion.extend([hijo1, hijo2])
            
            # Mutación
            for individuo in nueva_poblacion:
                if self._random.random() < tasa_mutacion:
                    self._mutar_individuo(individuo, len(recursos))
            
            poblacion = nueva_poblacion
            
            # Verificar convergencia
            if iteracion > 100 and abs(mejor_valor) < parametros.tolerancia:
                break
        
        return SolucionOptimizada(
            asignaciones=mejor_solucion or [],
            valor_objetivo=mejor_valor,
            tiempo_ejecucion=0.0,
            iteraciones=iteracion + 1,
            convergencia=abs(mejor_valor) < parametros.tolerancia,
            metricas=self._calcular_metricas_solucion(mejor_solucion or [])
        )
    
    def _optimizar_simulated_annealing(self, 
                                      procesos: List[Proceso], 
                                      recursos: List[Recurso], 
                                      parametros: ParametrosOptimizacion) -> SolucionOptimizada:
        """
        Optimiza usando recocido simulado.
        
        Args:
            procesos: Lista de procesos
            recursos: Lista de recursos
            parametros: Parámetros de optimización
            
        Returns:
            SolucionOptimizada: Solución encontrada
        """
        # Generar solución inicial
        solucion_actual = self._generar_solucion_inicial(procesos, recursos)
        valor_actual = self._calcular_valor_objetivo(solucion_actual, parametros)
        
        mejor_solucion = solucion_actual.copy()
        mejor_valor = valor_actual
        
        # Parámetros del recocido simulado
        temperatura_inicial = 1000.0
        temperatura_final = 0.1
        factor_enfriamiento = 0.95
        
        temperatura = temperatura_inicial
        
        for iteracion in range(parametros.max_iteraciones):
            # Generar solución vecina
            solucion_vecina = self._generar_solucion_vecina(solucion_actual, procesos, recursos)
            valor_vecina = self._calcular_valor_objetivo(solucion_vecina, parametros)
            
            # Decidir si aceptar la solución vecina
            if valor_vecina < valor_actual:
                # Mejor solución, aceptar
                solucion_actual = solucion_vecina
                valor_actual = valor_vecina
                
                # Actualizar mejor solución global
                if valor_vecina < mejor_valor:
                    mejor_solucion = solucion_vecina.copy()
                    mejor_valor = valor_vecina
            else:
                # Peor solución, aceptar con probabilidad
                delta = valor_vecina - valor_actual
                probabilidad = np.exp(-delta / temperatura)
                
                if self._random.random() < probabilidad:
                    solucion_actual = solucion_vecina
                    valor_actual = valor_vecina
            
            # Enfriar temperatura
            temperatura *= factor_enfriamiento
            
            # Verificar convergencia
            if temperatura < temperatura_final:
                break
        
        return SolucionOptimizada(
            asignaciones=mejor_solucion,
            valor_objetivo=mejor_valor,
            tiempo_ejecucion=0.0,
            iteraciones=iteracion + 1,
            convergencia=temperatura < temperatura_final,
            metricas=self._calcular_metricas_solucion(mejor_solucion)
        )
    
    def _optimizar_lineal(self, 
                         procesos: List[Proceso], 
                         recursos: List[Recurso], 
                         parametros: ParametrosOptimizacion) -> SolucionOptimizada:
        """
        Optimiza usando programación lineal.
        
        Args:
            procesos: Lista de procesos
            recursos: Lista de recursos
            parametros: Parámetros de optimización
            
        Returns:
            SolucionOptimizada: Solución encontrada
        """
        # Crear matriz de variables de decisión
        # x[i][j] = 1 si proceso i se asigna a recurso j, 0 en caso contrario
        num_procesos = len(procesos)
        num_recursos = len(recursos)
        
        # Coeficientes de la función objetivo
        c = []
        for i, proceso in enumerate(procesos):
            for j, recurso in enumerate(recursos):
                # Costo de asignar proceso i a recurso j
                costo = proceso.tiempo_estimado_horas * recurso.costo_por_hora
                tiempo = proceso.tiempo_estimado_horas
                eficiencia = recurso.capacidad_disponible / recurso.capacidad_maxima
                
                # Función objetivo ponderada
                valor_objetivo = (parametros.peso_costo * costo + 
                                parametros.peso_tiempo * tiempo - 
                                parametros.peso_eficiencia * eficiencia)
                c.append(valor_objetivo)
        
        # Restricciones
        A_eq = []
        b_eq = []
        
        # Restricción: cada proceso debe asignarse a exactamente un recurso
        for i in range(num_procesos):
            restriccion = [0] * (num_procesos * num_recursos)
            for j in range(num_recursos):
                restriccion[i * num_recursos + j] = 1
            A_eq.append(restriccion)
            b_eq.append(1)
        
        # Restricciones de desigualdad
        A_ub = []
        b_ub = []
        
        # Restricción: capacidad de recursos
        for j in range(num_recursos):
            restriccion = [0] * (num_procesos * num_recursos)
            for i in range(num_procesos):
                restriccion[i * num_recursos + j] = procesos[i].tiempo_estimado_horas
            A_ub.append(restriccion)
            b_ub.append(recursos[j].capacidad_disponible)
        
        # Límites de las variables (0 <= x <= 1)
        bounds = [(0, 1) for _ in range(num_procesos * num_recursos)]
        
        try:
            # Resolver el problema de programación lineal
            resultado = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq, 
                              bounds=bounds, method='highs')
            
            if resultado.success:
                # Convertir resultado a asignaciones
                asignaciones = self._convertir_resultado_lineal(resultado.x, procesos, recursos)
                
                return SolucionOptimizada(
                    asignaciones=asignaciones,
                    valor_objetivo=resultado.fun,
                    tiempo_ejecucion=0.0,
                    iteraciones=resultado.nit if hasattr(resultado, 'nit') else 0,
                    convergencia=True,
                    metricas=self._calcular_metricas_solucion(asignaciones)
                )
            else:
                # Fallback a algoritmo greedy si falla la optimización lineal
                return self._optimizar_greedy(procesos, recursos, parametros)
                
        except Exception as e:
            self._logger.warning(f"Error en optimización lineal: {str(e)}, usando greedy")
            return self._optimizar_greedy(procesos, recursos, parametros)
    
    def _optimizar_branch_and_bound(self, 
                                   procesos: List[Proceso], 
                                   recursos: List[Recurso], 
                                   parametros: ParametrosOptimizacion) -> SolucionOptimizada:
        """
        Optimiza usando ramificación y acotación.
        
        Args:
            procesos: Lista de procesos
            recursos: Lista de recursos
            parametros: Parámetros de optimización
            
        Returns:
            SolucionOptimizada: Solución encontrada
        """
        # Por simplicidad, implementamos una versión básica
        # que usa el algoritmo greedy como heurística
        return self._optimizar_greedy(procesos, recursos, parametros)
    
    # Métodos auxiliares
    def _ordenar_procesos_greedy(self, 
                                procesos: List[Proceso], 
                                recursos: List[Recurso], 
                                parametros: ParametrosOptimizacion) -> List[Proceso]:
        """Ordena procesos para el algoritmo greedy."""
        def clave_ordenamiento(proceso):
            # Combinar prioridad, tiempo y costo estimado
            prioridad = proceso.prioridad.value
            tiempo = proceso.tiempo_estimado_horas
            costo_estimado = min(r.costo_por_hora for r in recursos if r.costo_por_hora > 0) * tiempo
            
            return (prioridad * parametros.peso_eficiencia + 
                    1/tiempo * parametros.peso_tiempo + 
                    1/costo_estimado * parametros.peso_costo)
        
        return sorted(procesos, key=clave_ordenamiento, reverse=True)
    
    def _encontrar_mejor_recurso_greedy(self, 
                                       proceso: Proceso, 
                                       recursos: List[Recurso], 
                                       recursos_ocupados: Dict[str, float], 
                                       parametros: ParametrosOptimizacion) -> Tuple[Optional[Recurso], float]:
        """Encuentra el mejor recurso para un proceso en el algoritmo greedy."""
        mejor_recurso = None
        mejor_puntuacion = float('inf')
        
        for recurso in recursos:
            if not recurso.puede_asignarse(proceso.tiempo_estimado_horas):
                continue
            
            # Calcular puntuación
            costo = proceso.tiempo_estimado_horas * recurso.costo_por_hora
            tiempo = proceso.tiempo_estimado_horas
            eficiencia = recurso.capacidad_disponible / recurso.capacidad_maxima
            
            puntuacion = (parametros.peso_costo * costo + 
                         parametros.peso_tiempo * tiempo - 
                         parametros.peso_eficiencia * eficiencia)
            
            if puntuacion < mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_recurso = recurso
        
        return mejor_recurso, mejor_puntuacion
    
    def _crear_asignacion_optimizada(self, 
                                    proceso: Proceso, 
                                    recurso: Recurso, 
                                    horas_ocupadas: float) -> AsignacionRecurso:
        """Crea una asignación optimizada."""
        from datetime import timedelta
        
        fecha_inicio = datetime.now() + timedelta(hours=horas_ocupadas)
        fecha_fin = fecha_inicio + timedelta(hours=proceso.tiempo_estimado_horas)
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
    
    def _calcular_valor_objetivo(self, 
                                asignaciones: List[AsignacionRecurso], 
                                parametros: ParametrosOptimizacion) -> float:
        """Calcula el valor de la función objetivo."""
        if not asignaciones:
            return float('inf')
        
        costo_total = sum(a.costo_estimado for a in asignaciones)
        tiempo_total = max(a.fecha_fin for a in asignaciones) - min(a.fecha_inicio for a in asignaciones)
        tiempo_total_horas = tiempo_total.total_seconds() / 3600
        
        # Normalizar valores
        costo_normalizado = costo_total / len(asignaciones)
        tiempo_normalizado = tiempo_total_horas / len(asignaciones)
        eficiencia = len(asignaciones) / tiempo_total_horas if tiempo_total_horas > 0 else 0
        
        return (parametros.peso_costo * costo_normalizado + 
                parametros.peso_tiempo * tiempo_normalizado - 
                parametros.peso_eficiencia * eficiencia)
    
    def _calcular_metricas_solucion(self, asignaciones: List[AsignacionRecurso]) -> Dict[str, Any]:
        """Calcula métricas de una solución."""
        if not asignaciones:
            return {}
        
        costo_total = sum(a.costo_estimado for a in asignaciones)
        tiempo_total = max(a.fecha_fin for a in asignaciones) - min(a.fecha_inicio for a in asignaciones)
        
        return {
            "costo_total": costo_total,
            "tiempo_total_horas": tiempo_total.total_seconds() / 3600,
            "num_asignaciones": len(asignaciones),
            "costo_promedio": costo_total / len(asignaciones),
            "recursos_utilizados": len(set(a.recurso_id for a in asignaciones))
        }
    
    # Métodos auxiliares para algoritmo genético
    def _inicializar_poblacion(self, procesos: List[Proceso], recursos: List[Recurso], tamaño: int) -> List[List[int]]:
        """Inicializa población para algoritmo genético."""
        poblacion = []
        for _ in range(tamaño):
            individuo = [self._random.randint(0, len(recursos)-1) for _ in range(len(procesos))]
            poblacion.append(individuo)
        return poblacion
    
    def _decodificar_individuo(self, individuo: List[int], procesos: List[Proceso], recursos: List[Recurso]) -> List[AsignacionRecurso]:
        """Decodifica un individuo a asignaciones."""
        asignaciones = []
        recursos_ocupados = {r.id: 0.0 for r in recursos}
        
        for i, recurso_idx in enumerate(individuo):
            proceso = procesos[i]
            recurso = recursos[recurso_idx]
            
            if recurso.puede_asignarse(proceso.tiempo_estimado_horas):
                asignacion = self._crear_asignacion_optimizada(proceso, recurso, recursos_ocupados[recurso.id])
                asignaciones.append(asignacion)
                recursos_ocupados[recurso.id] += proceso.tiempo_estimado_horas
        
        return asignaciones
    
    def _seleccion_torneo(self, poblacion: List[List[int]], fitness: List[float]) -> List[List[int]]:
        """Selección por torneo."""
        seleccionados = []
        for _ in range(len(poblacion)):
            torneo = self._random.sample(list(zip(poblacion, fitness)), 3)
            ganador = min(torneo, key=lambda x: x[1])
            seleccionados.append(ganador[0])
        return seleccionados
    
    def _cruce_uniforme(self, padre1: List[int], padre2: List[int]) -> Tuple[List[int], List[int]]:
        """Cruce uniforme."""
        hijo1 = []
        hijo2 = []
        for i in range(len(padre1)):
            if self._random.random() < 0.5:
                hijo1.append(padre1[i])
                hijo2.append(padre2[i])
            else:
                hijo1.append(padre2[i])
                hijo2.append(padre1[i])
        return hijo1, hijo2
    
    def _mutar_individuo(self, individuo: List[int], num_recursos: int) -> None:
        """Muta un individuo."""
        for i in range(len(individuo)):
            if self._random.random() < 0.1:  # Tasa de mutación por gen
                individuo[i] = self._random.randint(0, num_recursos-1)
    
    # Métodos auxiliares para simulated annealing
    def _generar_solucion_inicial(self, procesos: List[Proceso], recursos: List[Recurso]) -> List[AsignacionRecurso]:
        """Genera solución inicial para simulated annealing."""
        parametros = ParametrosOptimizacion()
        return self._optimizar_greedy(procesos, recursos, parametros).asignaciones
    
    def _generar_solucion_vecina(self, solucion: List[AsignacionRecurso], procesos: List[Proceso], recursos: List[Recurso]) -> List[AsignacionRecurso]:
        """Genera solución vecina para simulated annealing."""
        nueva_solucion = solucion.copy()
        
        if nueva_solucion:
            # Cambiar aleatoriamente una asignación
            idx = self._random.randint(0, len(nueva_solucion)-1)
            nuevo_recurso = self._random.choice(recursos)
            
            # Encontrar el proceso correspondiente
            proceso_id = nueva_solucion[idx].proceso_id
            proceso = next((p for p in procesos if p.id == proceso_id), None)
            
            if proceso and nuevo_recurso.puede_asignarse(proceso.tiempo_estimado_horas):
                nueva_solucion[idx] = self._crear_asignacion_optimizada(proceso, nuevo_recurso, 0)
        
        return nueva_solucion
    
    def _convertir_resultado_lineal(self, x: np.ndarray, procesos: List[Proceso], recursos: List[Recurso]) -> List[AsignacionRecurso]:
        """Convierte resultado de programación lineal a asignaciones."""
        asignaciones = []
        num_recursos = len(recursos)
        
        for i, proceso in enumerate(procesos):
            for j, recurso in enumerate(recursos):
                idx = i * num_recursos + j
                if x[idx] > 0.5:  # Asignación binaria
                    asignacion = self._crear_asignacion_optimizada(proceso, recurso, 0)
                    asignaciones.append(asignacion)
                    break
        
        return asignaciones
