# Contenido completo para: src/models/processing_reportes.py

import pandas as pd
import os
from PySide6.QtCore import QThread, Signal
# --- INICIO CAMBIOS LOGGING ---
from src.utils.logger_setup import log # Importar el logger configurado
# --- FIN CAMBIOS LOGGING ---
from src.utils.file_handlers import detectar_separador_archivo 

class ReportesProcessingThread(QThread):
    """
    Hilo para procesar los archivos de reportes simples y generar estadísticas.
    """
    update_progress = Signal(int)
    update_status = Signal(str)
    # Emitirá un DataFrame de pandas con los resultados
    finished_processing = Signal(pd.DataFrame) 
    error_occurred = Signal(str)
    
    # Columnas esperadas en los CSV de reportes
    columnas_requeridas = [
        'clienteid', 'numtelefono', 'identificador', 'estatus', 'clic',
        'rcs_entregable', 'articulo_clic', 'campaña', 'modalidad', 'leido'
    ]

    def __init__(self, file_paths, db_connection):
        super().__init__()
        self.file_paths = file_paths
        self.db_connection = db_connection # Guardado para futuras implementaciones

    def run(self):
        log.info(f"Inicio del procesamiento de Reportes Simples para {len(self.file_paths)} archivo(s).") # <--- LOG Inicio
        try:
            all_stats = []
            total_files = len(self.file_paths)
            
            for i, file_path in enumerate(self.file_paths):
                file_name = os.path.basename(file_path)
                log.debug(f"Procesando archivo ({i+1}/{total_files}): {file_name}") # <--- LOG Archivo actual
                self.update_status.emit(f"Procesando archivo {i+1}/{total_files}: {file_name}")
                progress = int(((i + 1) / total_files) * 95) # Dejar espacio al final
                
                # 1. Detectar separador y leer archivo
                df = self.detectar_y_leer_archivo(file_path)
                if df is None:
                    # El error ya fue logueado en detectar_y_leer_archivo
                    continue 
                
                log.debug(f"Archivo leído: {file_name}, {len(df)} registros.") # <--- LOG Lectura
                
                # 2. Validar estructura
                if not self.validar_estructura_archivo(df):
                    error_msg = f"El archivo {file_name} no tiene la estructura requerida."
                    log.error(f"Error de estructura en Reportes Simples: {error_msg}") # <--- LOG Error Estructura
                    self.error_occurred.emit(error_msg)
                    return # Detener si un archivo es inválido
                
                # 3. Limpiar y convertir tipos de datos (¡Muy importante!)
                log.debug(f"Limpiando y convirtiendo tipos de datos para {file_name}...") # <--- LOG Limpieza
                try:
                    df['estatus'] = pd.to_numeric(df['estatus'], errors='coerce').fillna(0).astype(int)
                    df['leido'] = pd.to_numeric(df['leido'], errors='coerce').fillna(0).astype(int)
                    # Comprobar si hubo errores de conversión (NaN antes de fillna)
                    if df['estatus'].isna().any() or df['leido'].isna().any():
                         log.warning(f"Se encontraron valores no numéricos en columnas 'estatus' o 'leido' en {file_name}. Se convirtieron a 0.")
                except KeyError as ke:
                    log.error(f"Error de clave al convertir tipos en {file_name}: Columna {ke} no encontrada (esto no debería pasar si la validación funcionó).")
                    self.error_occurred.emit(f"Error interno: Falta columna {ke} en {file_name}.")
                    return
                except Exception as ex_convert: # Captura otros errores de conversión
                    log.exception(f"Error inesperado al convertir tipos de datos en {file_name}:")
                    self.error_occurred.emit(f"Error al convertir datos en {file_name}: {ex_convert}")
                    return

                df['modalidad'] = df['modalidad'].astype(str).str.lower().str.strip() # Asegurar que sea string
                df['clic'] = df['clic'].astype(str).str.lower().str.strip() # Asegurar que sea string
                log.debug(f"Tipos de datos convertidos para {file_name}.") # <--- LOG Limpieza Fin

                # 4. Calcular estadísticas según tu lógica
                log.debug(f"Calculando estadísticas para {file_name}...") # <--- LOG Cálculo
                total_original = len(df)
                enviados_rcs = len(df[(df['estatus'] == 1) & (df['modalidad'] == 'simple')])
                enviados_sms = len(df[(df['estatus'] == 1) & (df['modalidad'] == 'sms')])
                no_enviados = len(df[df['estatus'] == 0]) # Estatus 0 implica no enviado
                clics = len(df[df['clic'] == 'si'])
                leidos_unicos = len(df[(df['estatus'] == 1) & (df['leido'] == 1) & (df['modalidad'] == 'simple')])
                no_leidos = len(df[df['leido'] == 0]) # Leido 0 implica no leído
                log.debug(f"Estadísticas calculadas para {file_name}.") # <--- LOG Cálculo Fin

                # 5. Guardar resultados para este archivo
                stats = {
                    'CAMPAÑA': file_name,
                    'Total Original': total_original,
                    'Total Generada': total_original, # Como indicaste
                    'Excluidos': 0, # Como indicaste
                    'ENVIADOS RCS': enviados_rcs,
                    'ENVIADOS SMS': enviados_sms,
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
            log.info(f"Procesamiento de Reportes Simples completado exitosamente. {len(df_resumen)} archivo(s) procesado(s).") # <--- LOG Éxito Final
            self.finished_processing.emit(df_resumen)
                
        except Exception as e:
            log.exception("Error inesperado durante el procesamiento de Reportes Simples:") # <--- LOG Excepción General
            self.error_occurred.emit(f"Error inesperado en el procesamiento: {str(e)}")

    def detectar_y_leer_archivo(self, file_path):
        """Detecta el separador y lee el CSV."""
        file_name = os.path.basename(file_path) # Nombre para logs
        try:
            log.debug(f"Intentando detectar separador y leer (Reportes Simples): {file_name}") # <--- LOG Inicio Lectura
            separador = detectar_separador_archivo(file_path)
            log.debug(f"Separador detectado para {file_name}: '{separador}'") # <--- LOG Separador
            
            df = pd.read_csv(file_path, sep=separador, encoding='utf-8', low_memory=False)
            
            original_columns = df.columns.tolist()
            df.columns = df.columns.str.strip().str.lower() # Normalizar headers
            new_columns = df.columns.tolist()
            if original_columns != new_columns:
                 log.debug(f"Columnas normalizadas en {file_name}: {original_columns} -> {new_columns}")
                 
            # Renombrar 'clientid' a 'clienteid' si existe
            if 'clientid' in df.columns and 'clienteid' not in df.columns:
                 df.rename(columns={'clientid': 'clienteid'}, inplace=True)
                 log.debug(f"Columna 'clientid' renombrada a 'clienteid' en {file_name}")

            return df
            
        except FileNotFoundError:
            log.error(f"Error Crítico: Archivo no encontrado al intentar leer (Reportes Simples): {file_path}") # <--- LOG Error Archivo No Encontrado
            self.error_occurred.emit(f"Error: No se encontró el archivo {file_name}")
            return None
        except pd.errors.ParserError as pe:
            log.error(f"Error de formato CSV/TSV al leer {file_name}: {pe}") # <--- LOG Error Formato
            self.error_occurred.emit(f"Error de formato en {file_name}. Verifique las columnas y separadores.")
            return None
        except Exception as e:
            log.exception(f"Error inesperado al leer el archivo {file_name} (Reportes Simples):") # <--- LOG Error Genérico Lectura
            self.error_occurred.emit(f"Error al leer archivo {file_name}: {str(e)}")
            return None

    def validar_estructura_archivo(self, df):
        """Valida que el archivo tenga las columnas requeridas."""
        try:
            columnas_archivo = set(df.columns) # Ya están normalizadas
            columnas_requeridas_set = set(self.columnas_requeridas) # Definidas en minúsculas
            
            missing_cols = columnas_requeridas_set - columnas_archivo
            if missing_cols:
                log.warning(f"Validación de estructura fallida (Reportes Simples). Faltan columnas: {missing_cols}") # <--- LOG Columnas Faltantes
                return False
            
            # Log éxito (opcional, puede ser verboso)
            # log.debug("Validación de estructura (Reportes Simples) completada exitosamente.")
            return True
        except Exception as e:
            log.exception("Error inesperado durante la validación de estructura (Reportes Simples):") # <--- LOG Error Validación
            self.error_occurred.emit(f"Error al validar estructura: {str(e)}") 
            return False