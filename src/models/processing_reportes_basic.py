# Contenido completo para: src/models/processing_basic.py (o el nombre que le hayas dado)

import pandas as pd
import os
from PySide6.QtCore import QThread, Signal
# --- INICIO CAMBIOS LOGGING ---
from src.utils.logger_setup import log # Importar el logger configurado
# --- FIN CAMBIOS LOGGING ---
from src.utils.file_handlers import detectar_separador_archivo 

class ReportesBasicProcessingThread(QThread):
    """
    Hilo para procesar los archivos de reportes BASIC y generar estadísticas.
    """
    update_progress = Signal(int)
    update_status = Signal(str)
    # Emitirá un DataFrame de pandas con los resultados
    finished_processing = Signal(pd.DataFrame) 
    error_occurred = Signal(str)
    
    # Columnas requeridas para los reportes BASIC (asegúrate que coincidan con tu archivo)
    columnas_requeridas = [
        'clienteid', 'telefono', 'estatus', 'modalidad', 'leido'
    ]

    def __init__(self, file_paths, db_connection):
        super().__init__()
        self.file_paths = file_paths
        self.db_connection = db_connection

    def run(self):
        log.info(f"Inicio del procesamiento de Reportes BASIC para {len(self.file_paths)} archivo(s).") # <--- LOG Inicio
        try:
            all_stats = []
            total_files = len(self.file_paths)
            
            for i, file_path in enumerate(self.file_paths):
                file_name = os.path.basename(file_path)
                log.debug(f"Procesando archivo BASIC ({i+1}/{total_files}): {file_name}") # <--- LOG Archivo actual
                self.update_status.emit(f"Procesando archivo {i+1}/{total_files}: {file_name}")
                progress = int(((i + 1) / total_files) * 95) 
                
                # 1. Detectar y leer
                df = self.detectar_y_leer_archivo(file_path)
                if df is None:
                    # El error ya fue logueado
                    continue 
                
                log.debug(f"Archivo BASIC leído: {file_name}, {len(df)} registros.") # <--- LOG Lectura
                
                # 2. Validar estructura
                if not self.validar_estructura_archivo(df):
                    error_msg = f"El archivo {file_name} no tiene la estructura requerida (BASIC)."
                    log.error(f"Error de estructura en Reportes BASIC: {error_msg}") # <--- LOG Error Estructura
                    self.error_occurred.emit(error_msg)
                    return # Detener si un archivo es inválido
                
                # 3. Limpiar y convertir tipos de datos
                log.debug(f"Limpiando y convirtiendo tipos de datos para {file_name} (BASIC)...") # <--- LOG Limpieza
                try:
                    df['estatus'] = pd.to_numeric(df['estatus'], errors='coerce').fillna(0).astype(int)
                    df['leido'] = pd.to_numeric(df['leido'], errors='coerce').fillna(0).astype(int)
                    # Comprobar si hubo errores de conversión
                    if df['estatus'].isna().any() or df['leido'].isna().any():
                         log.warning(f"Se encontraron valores no numéricos en 'estatus' o 'leido' en {file_name} (BASIC). Se convirtieron a 0.")
                except KeyError as ke:
                    log.error(f"Error de clave al convertir tipos en {file_name} (BASIC): Columna {ke} no encontrada.")
                    self.error_occurred.emit(f"Error interno: Falta columna {ke} en {file_name}.")
                    return
                except Exception as ex_convert: 
                    log.exception(f"Error inesperado al convertir tipos de datos en {file_name} (BASIC):")
                    self.error_occurred.emit(f"Error al convertir datos en {file_name}: {ex_convert}")
                    return
                    
                df['modalidad'] = df['modalidad'].astype(str).str.lower().str.strip() # Asegurar que sea string
                log.debug(f"Tipos de datos convertidos para {file_name} (BASIC).") # <--- LOG Limpieza Fin

                # 4. Calcular estadísticas (Lógica para BASIC)
                log.debug(f"Calculando estadísticas BASIC para {file_name}...") # <--- LOG Cálculo
                total_original = len(df)
                
                # (estatus = 1 Y modalidad = 'basic') - Asegúrate que 'basic' sea el valor correcto
                enviados_rcs = len(df[(df['estatus'] == 1) & (df['modalidad'] == 'basic')]) 
                
                # (estatus = 1 Y modalidad = 'sms')
                enviados_sms = len(df[(df['estatus'] == 1) & (df['modalidad'] == 'sms')])
                
                # (estatus = 0)
                no_enviados = len(df[df['estatus'] == 0])
                
                # (clics = 0) - Como indicaste
                clics = 0 
                
                # (estatus = 1 Y leido = 1 Y modalidad = 'basic')
                leidos_unicos = len(df[(df['estatus'] == 1) & (df['leido'] == 1) & (df['modalidad'] == 'basic')])
                
                # (leido = 0)
                no_leidos = len(df[df['leido'] == 0])
                log.debug(f"Estadísticas BASIC calculadas para {file_name}.") # <--- LOG Cálculo Fin

                # 5. Guardar resultados para este archivo
                stats = {
                    'CAMPAÑA': file_name,
                    'Total Original': total_original,
                    'Total Generada': total_original,
                    'Excluidos': 0,
                    'Enviados (RCS)': enviados_rcs, # Cambiado nombre para claridad
                    'Enviados (SMS)': enviados_sms, # Cambiado nombre para claridad
                    'NO ENVIADOS': no_enviados,
                    'CLICS': clics,
                    'LEIDOS UNICO': leidos_unicos,
                    'NO LEIDOS': no_leidos
                }
                all_stats.append(stats)
                self.update_progress.emit(progress)

            # 6. Crear DataFrame final y emitir
            df_resumen = pd.DataFrame(all_stats)
            
            self.update_progress.emit(100)
            self.update_status.emit("Procesamiento de reportes completado")
            log.info(f"Procesamiento de Reportes BASIC completado exitosamente. {len(df_resumen)} archivo(s) procesado(s).") # <--- LOG Éxito Final
            self.finished_processing.emit(df_resumen)
                
        except Exception as e:
            log.exception("Error inesperado durante el procesamiento de Reportes BASIC:") # <--- LOG Excepción General
            self.error_occurred.emit(f"Error inesperado en el procesamiento: {str(e)}")

    def detectar_y_leer_archivo(self, file_path):
        """Detecta el separador y lee el CSV."""
        file_name = os.path.basename(file_path) # Nombre para logs
        try:
            log.debug(f"Intentando detectar separador y leer (Reportes BASIC): {file_name}") # <--- LOG Inicio Lectura
            separador = detectar_separador_archivo(file_path)
            log.debug(f"Separador detectado para {file_name}: '{separador}'") # <--- LOG Separador
            
            df = pd.read_csv(file_path, sep=separador, encoding='utf-8', low_memory=False)
            
            original_columns = df.columns.tolist()
            df.columns = df.columns.str.strip().str.lower() # Normalizar headers
            new_columns = df.columns.tolist()
            if original_columns != new_columns:
                 log.debug(f"Columnas normalizadas en {file_name} (BASIC): {original_columns} -> {new_columns}")
                 
            # Renombrar 'clientid' a 'clienteid' si existe
            if 'clientid' in df.columns and 'clienteid' not in df.columns:
                 df.rename(columns={'clientid': 'clienteid'}, inplace=True)
                 log.debug(f"Columna 'clientid' renombrada a 'clienteid' en {file_name} (BASIC)")
                 
            # Renombrar 'number' a 'telefono' si existe (basado en tus columnas requeridas)
            if 'number' in df.columns and 'telefono' not in df.columns:
                 df.rename(columns={'number': 'telefono'}, inplace=True)
                 log.debug(f"Columna 'number' renombrada a 'telefono' en {file_name} (BASIC)")


            return df
            
        except FileNotFoundError:
            log.error(f"Error Crítico: Archivo no encontrado al intentar leer (Reportes BASIC): {file_path}") # <--- LOG Error Archivo No Encontrado
            self.error_occurred.emit(f"Error: No se encontró el archivo {file_name}")
            return None
        except pd.errors.ParserError as pe:
            log.error(f"Error de formato CSV/TSV al leer {file_name} (BASIC): {pe}") # <--- LOG Error Formato
            self.error_occurred.emit(f"Error de formato en {file_name}. Verifique las columnas y separadores.")
            return None
        except Exception as e:
            log.exception(f"Error inesperado al leer el archivo {file_name} (Reportes BASIC):") # <--- LOG Error Genérico Lectura
            self.error_occurred.emit(f"Error al leer archivo {file_name}: {str(e)}")
            return None

    def validar_estructura_archivo(self, df):
        """Valida que el archivo tenga las columnas requeridas."""
        try:
            columnas_archivo = set(df.columns) # Ya están normalizadas
            columnas_requeridas_set = set(self.columnas_requeridas) # Definidas en minúsculas
            
            missing_cols = columnas_requeridas_set - columnas_archivo
            if missing_cols:
                log.warning(f"Validación de estructura fallida (Reportes BASIC). Faltan columnas: {missing_cols}") # <--- LOG Columnas Faltantes
                return False
                
            log.debug("Validación de estructura (Reportes BASIC) completada exitosamente.") # <--- LOG Éxito Validación
            return True
        except Exception as e:
            log.exception("Error inesperado durante la validación de estructura (Reportes BASIC):") # <--- LOG Error Validación
            self.error_occurred.emit(f"Error al validar estructura: {str(e)}") 
            return False