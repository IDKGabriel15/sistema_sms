# Contenido para: src/models/processing_directo.py

import pandas as pd
import os
from PySide6.QtCore import QThread, Signal
from src.utils.file_handlers import detectar_separador_archivo

class DirectoProcessingThread(QThread):
    """
    Hilo para procesar los archivos de reportes directo y generar estadísticas agregadas.
    """
    update_progress = Signal(int)
    update_status = Signal(str)
    # Emitirá un DataFrame de pandas con la fila única de resultados
    finished_processing = Signal(pd.DataFrame) 
    error_occurred = Signal(str)

    # Columnas esperadas (normalizadas a minúsculas)
    columnas_requeridas = ['clienteid', 'number', 'status']

    def __init__(self, file_paths, db_connection):
        super().__init__()
        self.file_paths = file_paths
        self.db_connection = db_connection

    def run(self):
        try:
            all_dataframes = [] # Lista para guardar los DataFrames leídos
            total_files = len(self.file_paths)

            for i, file_path in enumerate(self.file_paths):
                file_name = os.path.basename(file_path)
                self.update_status.emit(f"Procesando archivo {i+1}/{total_files}: {file_name}")
                progress = int(((i + 1) / total_files) * 80) # Dejar margen para agregación

                # 1. Detectar separador y leer archivo
                df = self.detectar_y_leer_archivo(file_path)
                if df is None:
                    continue 

                # 2. Validar estructura
                if not self.validar_estructura_archivo(df):
                    self.error_occurred.emit(f"El archivo {file_name} no tiene la estructura requerida (clienteid, number, status).")
                    return # Detener si un archivo es inválido

                # 3. Guardar el DataFrame leído
                all_dataframes.append(df)
                self.update_progress.emit(progress)

            if not all_dataframes:
                self.update_status.emit("⚠️ No se procesaron archivos válidos.")
                self.finished_processing.emit(pd.DataFrame()) # Emitir DataFrame vacío
                return

            # 4. Concatenar todos los DataFrames en uno solo
            self.update_status.emit("Agregando resultados...")
            df_consolidado = pd.concat(all_dataframes, ignore_index=True)

            # 5. Limpiar y convertir tipos de datos (muy importante)
            df_consolidado['status'] = pd.to_numeric(df_consolidado['status'], errors='coerce').fillna(-1).astype(int) # Usar -1 para errores

            # 6. Calcular estadísticas AGREGADAS
            total_original = len(df_consolidado)

            # Status = 1
            enviados = len(df_consolidado[df_consolidado['status'] == 1])

            # Status != 1 (incluye errores de conversión como -1)
            no_enviados = len(df_consolidado[df_consolidado['status'] != 1])

            # 7. Crear DataFrame final (una sola fila)
            stats = {
                'Campaña': ["# MX - DEVOLUCIONES"], # Nombre fijo
                'Total Original': [total_original],
                'Total Generada': [total_original],
                'Excluidos': [0],
                'Enviados': [enviados],
                'No enviados': [no_enviados]
            }
            df_resumen = pd.DataFrame(stats)

            self.update_progress.emit(100)
            self.update_status.emit("Procesamiento completado")
            self.finished_processing.emit(df_resumen)

        except Exception as e:
            self.error_occurred.emit(f"Error inesperado en el procesamiento: {str(e)}")

    def detectar_y_leer_archivo(self, file_path):
        """Detecta el separador, lee el CSV y normaliza la columna de cliente."""
        try:
            df = pd.read_csv(file_path, sep='|', encoding='utf-8', low_memory=False)
            
            # 1. Normalizar todos los headers a minúsculas y sin espacios
            df.columns = df.columns.str.strip().str.lower() 
            
            # --- INICIO DE CORRECCIÓN ---
            # 2. Renombrar específicamente 'clientid' (sin la 'e') a 'clienteid'
            #    Esto asegura que tanto 'clienteid' como 'clientid' (o 'ClientID') 
            #    terminen siendo 'clienteid'.
            df.rename(columns={'clientid': 'clienteid'}, inplace=True)
            # --- FIN DE CORRECCIÓN ---

            return df
        except Exception as e:
            self.error_occurred.emit(f"Error al leer archivo {os.path.basename(file_path)}: {str(e)}")
            return None
    
    def validar_estructura_archivo(self, df):
        """Valida que el archivo tenga las columnas requeridas."""
        columnas_archivo = set(df.columns)
        columnas_requeridas_set = set(self.columnas_requeridas)
        return columnas_requeridas_set.issubset(columnas_archivo)