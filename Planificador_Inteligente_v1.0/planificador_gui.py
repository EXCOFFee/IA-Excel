"""
Planificador Inteligente - Aplicación de Escritorio
==================================================

Interfaz gráfica de usuario para el Sistema Planificador Inteligente.
Permite a usuarios finales procesar archivos Excel sin conocimiento técnico.

Características:
- Interfaz gráfica amigable
- Procesamiento de archivos Excel
- Generación de reportes
- No requiere conocimiento técnico

Autor: Equipo de Desarrollo
Fecha: 2025-01-08
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import webbrowser
import os
import sys
import subprocess
import tempfile
import requests
import json
from datetime import datetime
import time

class PlanificadorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📊 Planificador Inteligente - Procesador de Excel")
        self.root.geometry("800x600")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.servidor_proceso = None
        self.servidor_activo = False
        self.archivo_excel = None
        self.archivo_resultados = None
        
        # Crear interfaz
        self.crear_interfaz()
        
        # Iniciar servidor automáticamente
        self.iniciar_servidor()
        
    def crear_interfaz(self):
        """Crea la interfaz gráfica"""
        # Título principal
        titulo = tk.Label(
            self.root, 
            text="📊 Planificador Inteligente",
            font=("Arial", 20, "bold"),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        titulo.pack(pady=20)
        
        # Subtítulo
        subtitulo = tk.Label(
            self.root,
            text="Procesa archivos Excel y genera reportes de planificación optimizados",
            font=("Arial", 11),
            bg='#f0f0f0',
            fg='#7f8c8d'
        )
        subtitulo.pack(pady=(0, 30))
        
        # Frame principal
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Estado del servidor
        self.estado_frame = tk.Frame(main_frame, bg='#f0f0f0')
        self.estado_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.estado_label = tk.Label(
            self.estado_frame,
            text="🔄 Iniciando servidor...",
            font=("Arial", 10),
            bg='#f0f0f0',
            fg='#f39c12'
        )
        self.estado_label.pack(side=tk.LEFT)
        
        # Sección 1: Descargar plantilla
        self.crear_seccion_plantilla(main_frame)
        
        # Sección 2: Procesar archivo
        self.crear_seccion_procesar(main_frame)
        
        # Sección 3: Resultados
        self.crear_seccion_resultados(main_frame)
        
        # Logs
        self.crear_seccion_logs(main_frame)
        
    def crear_seccion_plantilla(self, parent):
        """Crea la sección de descarga de plantilla"""
        frame = tk.LabelFrame(parent, text="1️⃣ Descargar Plantilla Excel", 
                             font=("Arial", 12, "bold"), bg='#f0f0f0')
        frame.pack(fill=tk.X, pady=(0, 20))
        
        desc = tk.Label(frame, 
                       text="Descarga una plantilla Excel con el formato correcto para tus datos",
                       font=("Arial", 10), bg='#f0f0f0', fg='#555')
        desc.pack(pady=10)
        
        btn_plantilla = tk.Button(frame,
                                 text="📥 Descargar Plantilla",
                                 command=self.descargar_plantilla,
                                 font=("Arial", 11, "bold"),
                                 bg='#3498db',
                                 fg='white',
                                 padx=20,
                                 pady=10)
        btn_plantilla.pack(pady=10)
        
    def crear_seccion_procesar(self, parent):
        """Crea la sección de procesamiento"""
        frame = tk.LabelFrame(parent, text="2️⃣ Procesar Archivo Excel", 
                             font=("Arial", 12, "bold"), bg='#f0f0f0')
        frame.pack(fill=tk.X, pady=(0, 20))
        
        desc = tk.Label(frame, 
                       text="Selecciona tu archivo Excel con datos de procesos y recursos",
                       font=("Arial", 10), bg='#f0f0f0', fg='#555')
        desc.pack(pady=10)
        
        # Frame para archivo seleccionado
        archivo_frame = tk.Frame(frame, bg='#f0f0f0')
        archivo_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.archivo_label = tk.Label(archivo_frame,
                                     text="Ningún archivo seleccionado",
                                     font=("Arial", 10),
                                     bg='#f0f0f0',
                                     fg='#7f8c8d')
        self.archivo_label.pack(side=tk.LEFT)
        
        # Botones
        btn_frame = tk.Frame(frame, bg='#f0f0f0')
        btn_frame.pack(pady=10)
        
        btn_seleccionar = tk.Button(btn_frame,
                                   text="📂 Seleccionar Archivo",
                                   command=self.seleccionar_archivo,
                                   font=("Arial", 11),
                                   bg='#95a5a6',
                                   fg='white',
                                   padx=15,
                                   pady=8)
        btn_seleccionar.pack(side=tk.LEFT, padx=5)
        
        self.btn_procesar = tk.Button(btn_frame,
                                     text="⚙️ Procesar Archivo",
                                     command=self.procesar_archivo,
                                     font=("Arial", 11, "bold"),
                                     bg='#27ae60',
                                     fg='white',
                                     padx=15,
                                     pady=8,
                                     state=tk.DISABLED)
        self.btn_procesar.pack(side=tk.LEFT, padx=5)
        
        # Barra de progreso
        self.progreso = ttk.Progressbar(frame, mode='indeterminate')
        self.progreso.pack(fill=tk.X, padx=20, pady=10)
        
    def crear_seccion_resultados(self, parent):
        """Crea la sección de resultados"""
        frame = tk.LabelFrame(parent, text="3️⃣ Resultados y Descargas", 
                             font=("Arial", 12, "bold"), bg='#f0f0f0')
        frame.pack(fill=tk.X, pady=(0, 20))
        
        # Métricas
        self.metricas_frame = tk.Frame(frame, bg='#f0f0f0')
        self.metricas_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.metricas_text = tk.Text(self.metricas_frame, height=6, width=70,
                                    font=("Courier", 10),
                                    bg='#ecf0f1',
                                    relief=tk.SUNKEN,
                                    state=tk.DISABLED)
        self.metricas_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para métricas
        scrollbar = tk.Scrollbar(self.metricas_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.metricas_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.metricas_text.yview)
        
        # Botón descargar
        self.btn_descargar = tk.Button(frame,
                                      text="📊 Descargar Resultados",
                                      command=self.descargar_resultados,
                                      font=("Arial", 11, "bold"),
                                      bg='#e74c3c',
                                      fg='white',
                                      padx=20,
                                      pady=10,
                                      state=tk.DISABLED)
        self.btn_descargar.pack(pady=10)
        
    def crear_seccion_logs(self, parent):
        """Crea la sección de logs"""
        frame = tk.LabelFrame(parent, text="📋 Registro de Actividad", 
                             font=("Arial", 10, "bold"), bg='#f0f0f0')
        frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Área de logs
        logs_frame = tk.Frame(frame, bg='#f0f0f0')
        logs_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.logs_text = tk.Text(logs_frame, height=8,
                                font=("Courier", 9),
                                bg='#2c3e50',
                                fg='#ecf0f1',
                                relief=tk.SUNKEN)
        self.logs_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar para logs
        logs_scrollbar = tk.Scrollbar(logs_frame, orient=tk.VERTICAL)
        logs_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.logs_text.config(yscrollcommand=logs_scrollbar.set)
        logs_scrollbar.config(command=self.logs_text.yview)
        
        # Botón limpiar logs
        btn_limpiar = tk.Button(frame,
                               text="🧹 Limpiar Logs",
                               command=self.limpiar_logs,
                               font=("Arial", 9),
                               bg='#34495e',
                               fg='white',
                               padx=10,
                               pady=5)
        btn_limpiar.pack(pady=5)
        
    def log(self, mensaje):
        """Añade un mensaje al log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_line = f"[{timestamp}] {mensaje}\n"
        
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.insert(tk.END, log_line)
        self.logs_text.see(tk.END)
        self.logs_text.config(state=tk.DISABLED)
        
    def limpiar_logs(self):
        """Limpia el área de logs"""
        self.logs_text.config(state=tk.NORMAL)
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.config(state=tk.DISABLED)
        
    def iniciar_servidor(self):
        """Inicia el servidor FastAPI en un hilo separado"""
        def iniciar():
            try:
                self.log("🔄 Iniciando servidor interno...")
                
                # Verificar si Python está disponible
                resultado = subprocess.run([sys.executable, "--version"], 
                                         capture_output=True, text=True)
                if resultado.returncode != 0:
                    raise Exception("Python no encontrado")
                    
                # Iniciar servidor
                self.servidor_proceso = subprocess.Popen([
                    sys.executable, "-m", "uvicorn",
                    "interface.api.main:app",
                    "--host", "127.0.0.1",
                    "--port", "8000",
                    "--log-level", "warning"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                # Esperar a que el servidor esté listo
                time.sleep(3)
                
                # Verificar que el servidor está funcionando
                try:
                    response = requests.get("http://127.0.0.1:8000/health", timeout=5)
                    if response.status_code == 200:
                        self.servidor_activo = True
                        self.estado_label.config(text="✅ Servidor listo", fg='#27ae60')
                        self.log("✅ Servidor iniciado correctamente")
                    else:
                        raise Exception("Servidor no responde correctamente")
                except requests.exceptions.RequestException:
                    raise Exception("No se puede conectar al servidor")
                    
            except Exception as e:
                self.servidor_activo = False
                self.estado_label.config(text="❌ Error en servidor", fg='#e74c3c')
                self.log(f"❌ Error iniciando servidor: {str(e)}")
                messagebox.showerror("Error", f"No se pudo iniciar el servidor:\n{str(e)}")
                
        threading.Thread(target=iniciar, daemon=True).start()
        
    def descargar_plantilla(self):
        """Descarga la plantilla Excel"""
        if not self.servidor_activo:
            messagebox.showerror("Error", "El servidor no está activo")
            return
            
        try:
            self.log("📥 Descargando plantilla Excel...")
            
            response = requests.get("http://127.0.0.1:8000/api/excel/plantilla", timeout=10)
            
            if response.status_code == 200:
                # Guardar archivo
                archivo_destino = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    title="Guardar plantilla como...",
                    initialfile="plantilla_planificador.xlsx"
                )
                
                if archivo_destino:
                    with open(archivo_destino, 'wb') as f:
                        f.write(response.content)
                    
                    self.log(f"✅ Plantilla descargada: {os.path.basename(archivo_destino)}")
                    messagebox.showinfo("Éxito", 
                                      f"Plantilla descargada exitosamente:\n{archivo_destino}")
                    
                    # Preguntar si abrir el archivo
                    if messagebox.askyesno("Abrir archivo", 
                                         "¿Deseas abrir la plantilla en Excel?"):
                        os.startfile(archivo_destino)
                        
            else:
                raise Exception(f"Error HTTP {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Error descargando plantilla: {str(e)}")
            messagebox.showerror("Error", f"No se pudo descargar la plantilla:\n{str(e)}")
            
    def seleccionar_archivo(self):
        """Permite seleccionar un archivo Excel"""
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if archivo:
            self.archivo_excel = archivo
            self.archivo_label.config(text=f"📄 {os.path.basename(archivo)}", fg='#2c3e50')
            self.btn_procesar.config(state=tk.NORMAL)
            self.log(f"📂 Archivo seleccionado: {os.path.basename(archivo)}")
            
    def procesar_archivo(self):
        """Procesa el archivo Excel seleccionado"""
        if not self.archivo_excel:
            messagebox.showerror("Error", "Por favor selecciona un archivo Excel")
            return
            
        if not self.servidor_activo:
            messagebox.showerror("Error", "El servidor no está activo")
            return
            
        def procesar():
            try:
                self.btn_procesar.config(state=tk.DISABLED)
                self.progreso.start()
                self.log(f"⚙️ Procesando archivo: {os.path.basename(self.archivo_excel)}")
                
                # Procesar archivo
                with open(self.archivo_excel, 'rb') as f:
                    files = {'archivo': (os.path.basename(self.archivo_excel), f, 
                                        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                    response = requests.post("http://127.0.0.1:8000/api/excel/procesar", 
                                           files=files, timeout=30)
                
                if response.status_code == 200:
                    resultado = response.json()
                    
                    # Mostrar métricas
                    self.mostrar_metricas(resultado)
                    
                    # Guardar nombre del archivo de resultados
                    self.archivo_resultados = resultado.get('archivo_resultados')
                    
                    # Habilitar descarga
                    self.btn_descargar.config(state=tk.NORMAL)
                    
                    self.log("✅ Archivo procesado exitosamente")
                    messagebox.showinfo("Éxito", "¡Archivo procesado exitosamente!\nYa puedes descargar los resultados.")
                    
                else:
                    raise Exception(f"Error HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                self.log(f"❌ Error procesando archivo: {str(e)}")
                messagebox.showerror("Error", f"No se pudo procesar el archivo:\n{str(e)}")
                
            finally:
                self.progreso.stop()
                self.btn_procesar.config(state=tk.NORMAL)
                
        threading.Thread(target=procesar, daemon=True).start()
        
    def mostrar_metricas(self, resultado):
        """Muestra las métricas del análisis"""
        resumen = resultado.get('resumen', {})
        
        metricas = f"""
📊 RESULTADOS DEL ANÁLISIS
{'='*50}
📋 Procesos analizados: {resultado.get('procesos_leidos', 0)}
👥 Recursos analizados: {resultado.get('recursos_leidos', 0)}

📈 MÉTRICAS CALCULADAS
{'='*50}
🎯 Eficiencia proyectada: {resumen.get('eficiencia_proyectada', 0)}%
💰 Costo total estimado: ${resumen.get('costo_total', 0):,.2f}
⏱️ Tiempo total requerido: {resumen.get('tiempo_total_horas', 0):,.1f} horas
🔧 Capacidad total disponible: {resumen.get('capacidad_total_horas', 0):,.1f} horas

📊 ANÁLISIS DE CAPACIDAD
{'='*50}
"""
        
        tiempo_total = resumen.get('tiempo_total_horas', 0)
        capacidad_total = resumen.get('capacidad_total_horas', 0)
        
        if tiempo_total > capacidad_total:
            deficit = tiempo_total - capacidad_total
            metricas += f"⚠️ Déficit de capacidad: {deficit:.1f} horas\n"
            metricas += "💡 Recomendación: Considerar recursos adicionales\n"
        else:
            margen = capacidad_total - tiempo_total
            metricas += f"✅ Capacidad suficiente con {margen:.1f} horas de margen\n"
            
        self.metricas_text.config(state=tk.NORMAL)
        self.metricas_text.delete(1.0, tk.END)
        self.metricas_text.insert(1.0, metricas)
        self.metricas_text.config(state=tk.DISABLED)
        
    def descargar_resultados(self):
        """Descarga el archivo de resultados"""
        if not self.archivo_resultados:
            messagebox.showerror("Error", "No hay resultados para descargar")
            return
            
        try:
            self.log("📥 Descargando resultados...")
            
            response = requests.get(f"http://127.0.0.1:8000/api/excel/descargar/{self.archivo_resultados}", 
                                   timeout=10)
            
            if response.status_code == 200:
                # Guardar archivo
                archivo_destino = filedialog.asksaveasfilename(
                    defaultextension=".xlsx",
                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                    title="Guardar resultados como...",
                    initialfile=self.archivo_resultados
                )
                
                if archivo_destino:
                    with open(archivo_destino, 'wb') as f:
                        f.write(response.content)
                    
                    self.log(f"✅ Resultados descargados: {os.path.basename(archivo_destino)}")
                    messagebox.showinfo("Éxito", 
                                      f"Resultados descargados exitosamente:\n{archivo_destino}")
                    
                    # Preguntar si abrir el archivo
                    if messagebox.askyesno("Abrir archivo", 
                                         "¿Deseas abrir los resultados en Excel?"):
                        os.startfile(archivo_destino)
                        
            else:
                raise Exception(f"Error HTTP {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ Error descargando resultados: {str(e)}")
            messagebox.showerror("Error", f"No se pudo descargar los resultados:\n{str(e)}")
            
    def cerrar_aplicacion(self):
        """Cierra la aplicación y el servidor"""
        if self.servidor_proceso:
            self.servidor_proceso.terminate()
            self.servidor_proceso.wait()
            
        self.root.destroy()

def main():
    """Función principal"""
    root = tk.Tk()
    app = PlanificadorApp(root)
    
    # Manejar cierre de ventana
    root.protocol("WM_DELETE_WINDOW", app.cerrar_aplicacion)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        app.cerrar_aplicacion()

if __name__ == "__main__":
    main()
