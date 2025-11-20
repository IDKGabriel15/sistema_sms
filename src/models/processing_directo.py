# Contenido completo para: src/models/processing_directo.py

import pandas as pd
import os
from PySide6.QtCore import QThread, Signal
# --- INICIO CAMBIOS LOGGING ---
from src.utils.logger_setup import log # Importar el logger configurado
# --- FIN CAMBIOS LOGGING ---
# Importar detector de separador (aunque no se use aquí, por consistencia)
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
        log.info(f"Inicio del procesamiento de Reportes Directo para {len(self.file_paths)} archivo(s).") # <--- LOG Inicio
        try:
            all_dataframes = [] # Lista para guardar los DataFrames leídos
            total_files = len(self.file_paths)
            
            for i, file_path in enumerate(self.file_paths):
                file_name = os.path.basename(file_path)
                log.debug(f"Procesando archivo Directo ({i+1}/{total_files}): {file_name}") # <--- LOG Archivo actual
                self.update_status.emit(f"Procesando archivo {i+1}/{total_files}: {file_name}")
                progress = int(((i + 1) / total_files) * 80) # Dejar margen para agregación
                
                # 1. Leer archivo (separador '|' fijo)
                df = self.detectar_y_leer_archivo(file_path)
                if df is None:
                    # El error ya fue logueado
                    continue 
                
                log.debug(f"Archivo Directo leído: {file_name}, {len(df)} registros.") # <--- LOG Lectura
                
                # 2. Validar estructura
                if not self.validar_estructura_archivo(df):
                    error_msg = f"El archivo {file_name} no tiene la estructura requerida (clienteid, number, status)."
                    log.error(f"Error de estructura en Reportes Directo: {error_msg}") # <--- LOG Error Estructura
                    self.error_occurred.emit(error_msg)
                    return # Detener si un archivo es inválido
                
                # 3. Guardar el DataFrame leído
                all_dataframes.append(df)
                self.update_progress.emit(progress)

            if not all_dataframes:
                log.warning("No se procesaron archivos válidos en Reportes Directo.") # <--- LOG Sin archivos válidos
                self.update_status.emit("⚠️ No se procesaron archivos válidos.")
                self.finished_processing.emit(pd.DataFrame()) # Emitir DataFrame vacío
                return

            # 4. Concatenar todos los DataFrames en uno solo
            log.info("Agregando resultados de Reportes Directo...") # <--- LOG Agregación
            self.update_status.emit("Agregando resultados...")
            df_consolidado = pd.concat(all_dataframes, ignore_index=True)
            log.info(f"Total de registros consolidados (Directo): {len(df_consolidado)}") # <--- LOG Total consolidado
            
            # 5. Limpiar y convertir tipos de datos
            log.debug("Limpiando y convirtiendo tipos de datos (Directo)...") # <--- LOG Limpieza
            try:
                # Usar -1 para errores de conversión, como antes
                df_consolidado['status'] = pd.to_numeric(df_consolidado['status'], errors='coerce').fillna(-1).astype(int) 
                if df_consolidado['status'].eq(-1).any():
                     log.warning("Se encontraron valores no numéricos en la columna 'status' (Directo). Se marcaron como -1.")
            except KeyError as ke:
                 log.error(f"Error de clave al convertir 'status' (Directo): Columna {ke} no encontrada.")
                 self.error_occurred.emit(f"Error interno: Falta columna {ke} en consolidado.")
                 return
            except Exception as ex_convert:
                 log.exception("Error inesperado al convertir 'status' (Directo):")
                 self.error_occurred.emit(f"Error al convertir 'status': {ex_convert}")
                 return
            log.debug("Tipos de datos convertidos (Directo).") # <--- LOG Limpieza Fin

            # 6. Calcular estadísticas AGREGADAS
            log.debug("Calculando estadísticas agregadas (Directo)...") # <--- LOG Cálculo
            total_original = len(df_consolidado)
            
            # Status = 1
            enviados = len(df_consolidado[df_consolidado['status'] == 1])
            
            # Status != 1 (incluye errores de conversión como -1)
            no_enviados = len(df_consolidado[df_consolidado['status'] != 1])
            log.debug("Estadísticas agregadas calculadas (Directo).") # <--- LOG Cálculo Fin

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
            log.info("Procesamiento de Reportes Directo completado exitosamente.") # <--- LOG Éxito Final
            self.finished_processing.emit(df_resumen)
                
        except Exception as e:
            log.exception("Error inesperado durante el procesamiento de Reportes Directo:") # <--- LOG Excepción General
            self.error_occurred.emit(f"Error inesperado en el procesamiento: {str(e)}")

    def detectar_y_leer_archivo(self, file_path):
        """Lee el CSV (separador '|' fijo) y normaliza columnas."""
        file_name = os.path.basename(file_path) # Nombre para logs
        try:
            log.debug(f"Intentando leer archivo Directo (sep='|'): {file_name}") # <--- LOG Inicio Lectura
            # Separador '|' fijo para este tipo de reporte
            df = pd.read_csv(file_path, sep='|', encoding='utf-8', low_memory=False) 
            
            original_columns = df.columns.tolist()
            # Normalizar todos los headers a minúsculas y sin espacios
            df.columns = df.columns.str.strip().str.lower() 
            new_columns = df.columns.tolist()
            if original_columns != new_columns:
                 log.debug(f"Columnas normalizadas en {file_name} (Directo): {original_columns} -> {new_columns}")
            
            # Renombrar 'clientid' a 'clienteid' si existe
            if 'clientid' in df.columns and 'clienteid' not in df.columns:
                 df.rename(columns={'clientid': 'clienteid'}, inplace=True)
                 log.debug(f"Columna 'clientid' renombrada a 'clienteid' en {file_name} (Directo)")

            return df
            
        except FileNotFoundError:
            log.error(f"Error Crítico: Archivo no encontrado al intentar leer (Directo): {file_path}") # <--- LOG Error Archivo No Encontrado
            self.error_occurred.emit(f"Error: No se encontró el archivo {file_name}")
            return None
        except pd.errors.ParserError as pe:
            log.error(f"Error de formato '|' al leer {file_name} (Directo): {pe}") # <--- LOG Error Formato
            self.error_occurred.emit(f"Error de formato en {file_name}. Verifique las columnas y separador '|'.")
            return None
        except Exception as e:
            log.exception(f"Error inesperado al leer el archivo {file_name} (Directo):") # <--- LOG Error Genérico Lectura
            self.error_occurred.emit(f"Error al leer archivo {file_name}: {str(e)}")
            return None
    
    def validar_estructura_archivo(self, df):
        """Valida que el archivo tenga las columnas requeridas."""
        try:
            columnas_archivo = set(df.columns) # Ya están normalizadas
            columnas_requeridas_set = set(self.columnas_requeridas) # Definidas en minúsculas
            
            missing_cols = columnas_requeridas_set - columnas_archivo
            if missing_cols:
                log.warning(f"Validación de estructura fallida (Directo). Faltan columnas: {missing_cols}") # <--- LOG Columnas Faltantes
                return False
                
            log.debug("Validación de estructura (Directo) completada exitosamente.") # <--- LOG Éxito Validación
            return True
        except Exception as e:
            log.exception("Error inesperado durante la validación de estructura (Directo):") # <--- LOG Error Validación
            self.error_occurred.emit(f"Error al validar estructura: {str(e)}") 
            return False