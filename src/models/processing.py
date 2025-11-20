# Contenido completo para: src/models/processing.py

import pandas as pd
import os
from PySide6.QtCore import QThread, Signal
# --- INICIO CAMBIOS LOGGING ---
from src.utils.logger_setup import log # Importar el logger configurado
# --- FIN CAMBIOS LOGGING ---
# Importar la utilidad para detectar separador si no está aquí ya
from src.utils.file_handlers import detectar_separador_archivo 

class ProcessingThread(QThread):
    update_progress = Signal(int)
    update_status = Signal(str)
    finished_processing = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, file_paths, db_connection):
        super().__init__()
        self.file_paths = file_paths
        self.db_connection = db_connection
        #CAMBIAR A REGEX
        
        self.caracteres_permitidos = ' É_!"#\'¤%&()*+-./<=>?$@0ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;\''
        self.columnas_requeridas = [
            'clienteid', 'nombre', 'apellidopaterno', 'apellidomaterno', 'numtelefono', 
            'mensaje', 'variable1', 'variable2', 'variable3', 'variable4', 'variable5', 
            'fechainsercion', 'fechaaenviar', 'horaaenviar', 'campana'
        ]
    
    def run(self):
        # Log del inicio del proceso
        log.info(f"Inicio del procesamiento de devoluciones para {len(self.file_paths)} archivo(s).") 
        try:
            all_dataframes = {}
            tabla_resumen_data = []
            total_files = len(self.file_paths)
            
            for i, file_path in enumerate(self.file_paths):
                file_name = os.path.basename(file_path) # Usar file_name para logs
                self.update_status.emit(f"Procesando archivo {i+1}/{total_files}: {file_name}")
                progress = int((i / total_files) * 80)
                self.update_progress.emit(progress)
                
                # Detectar separador y leer archivo
                df = self.detectar_y_leer_archivo(file_path)
                
                if df is None:
                    # El error ya fue logueado en detectar_y_leer_archivo
                    continue
                
                # Log después de leer (nivel DEBUG es menos prioritario)
                log.debug(f"Archivo leído: {file_name}, {len(df)} registros.") 
                
                # Validar estructura del archivo
                if not self.validar_estructura_archivo(df):
                    error_msg = f"El archivo {file_name} no tiene la estructura requerida"
                    log.error(f"Error de estructura: {error_msg}") # Log del error
                    self.error_occurred.emit(error_msg)
                    return # Detener el proceso si un archivo es inválido
                
                # Validar mensajes
                mensajes_invalidos = self.validar_mensajes(df)
                if mensajes_invalidos:
                    # Mostramos el detalle en la UI, pero logueamos algo más breve
                    error_msg_ui = f"Caracteres no permitidos encontrados en {file_name}:\n{mensajes_invalidos}"
                    log.error(f"Error de caracteres inválidos en archivo: {file_name}") # Log del error
                    self.error_occurred.emit(error_msg_ui)
                    return # Detener el proceso
                
                # Procesar por campaña
                campanas = df['campana'].unique()
                log.debug(f"Archivo {file_name}: Campañas encontradas: {list(campanas)}") # Log de campañas
                for campana in campanas:
                    df_campana = df[df['campana'] == campana].copy()
                    
                    # Guardar en el diccionario
                    if campana not in all_dataframes:
                        all_dataframes[campana] = []
                    all_dataframes[campana].append(df_campana)
                    
                    # Agregar a tabla resumen
                    tabla_resumen_data.append({
                        'Campaña': campana,
                        'Registros': len(df_campana)
                    })
            
            # Consolidar DataFrames por campaña
            dataframes_consolidados = {}
            log.info("Consolidando DataFrames por campaña...") # Log de consolidación
            for campana, dfs in all_dataframes.items():
                if dfs:
                    dataframes_consolidados[campana] = pd.concat(dfs, ignore_index=True)
                    log.debug(f"Campaña '{campana}' consolidada con {len(dataframes_consolidados[campana])} registros.")
            
            self.update_progress.emit(100)
            self.update_status.emit("Procesamiento completado")
            
            # Crear DataFrame de resumen
            df_resumen = pd.DataFrame(tabla_resumen_data)
            if not df_resumen.empty:
                df_resumen = df_resumen.groupby('Campaña').sum().reset_index()
            
            resultado = {
                'dataframes': dataframes_consolidados,
                'resumen': df_resumen
            }
            # Log de éxito final
            log.info(f"Procesamiento de devoluciones completado exitosamente. {len(dataframes_consolidados)} campañas procesadas.") 
            self.finished_processing.emit(resultado)
                
        except Exception as e:
            # Loguea la excepción completa (incluye traceback)
            log.exception("Error inesperado durante el procesamiento de devoluciones:") 
            self.error_occurred.emit(f"Error inesperado: {str(e)}") # Mensaje más simple para la UI

    
    def detectar_y_leer_archivo(self, file_path):
        """Detecta el separador del archivo y lo lee"""
        file_name = os.path.basename(file_path) # Nombre para logs
        try:
            log.debug(f"Intentando detectar separador y leer: {file_name}") # Log inicio lectura
            # Usamos la función de utilidades para detectar separador
            separador = detectar_separador_archivo(file_path)
            log.debug(f"Separador detectado para {file_name}: '{separador}'") # Log separador
            
            # Leer archivo con el separador detectado
            df = pd.read_csv(file_path, sep=separador, encoding='utf-8', low_memory=False)
            
            # Limpiar nombres de columnas
            original_columns = df.columns.tolist()
            df.columns = df.columns.str.strip().str.lower() # Normalizar a minúsculas
            new_columns = df.columns.tolist()
            if original_columns != new_columns:
                 log.debug(f"Columnas normalizadas en {file_name}: {original_columns} -> {new_columns}")

            # --- Añadir renombrado si es necesario (como vimos para clienteid/ClientID) ---
            # df.rename(columns={'clientid': 'clienteid'}, inplace=True) 
            # log.debug(f"Columna 'clientid' renombrada a 'clienteid' si existía en {file_name}")
            # --- Fin renombrado ---
            
            return df
            
        except FileNotFoundError:
            log.error(f"Error Crítico: Archivo no encontrado al intentar leer: {file_path}")
            self.error_occurred.emit(f"Error: No se encontró el archivo {file_name}")
            return None
        except pd.errors.ParserError as pe:
            log.error(f"Error de formato CSV/TSV al leer {file_name}: {pe}")
            self.error_occurred.emit(f"Error de formato en {file_name}. Verifique las columnas y separadores.")
            return None
        except Exception as e:
            # Loguear error genérico de lectura
            log.exception(f"Error inesperado al leer el archivo {file_name}:") 
            self.error_occurred.emit(f"Error al leer archivo {file_name}: {str(e)}")
            return None

    def validar_estructura_archivo(self, df):
        """Valida que el archivo tenga las columnas requeridas"""
        try:
            columnas_archivo = set(df.columns) # Ya están en minúsculas por detectar_y_leer_archivo
            columnas_requeridas_set = set(col.lower() for col in self.columnas_requeridas)
            
            missing_cols = columnas_requeridas_set - columnas_archivo
            if missing_cols:
                log.warning(f"Validación de estructura fallida. Faltan columnas: {missing_cols}") # Log columnas faltantes
                return False
                
            # Opcional: Loguear si hay columnas extra (puede ser normal)
            # extra_cols = columnas_archivo - columnas_requeridas_set
            # if extra_cols:
            #    log.debug(f"Columnas extra encontradas (ignoradas): {extra_cols}")
                
            return True
        except Exception as e:
            log.exception("Error inesperado durante la validación de estructura:")
            # Considera si quieres emitir un error aquí o simplemente retornar False
            self.error_occurred.emit(f"Error al validar estructura: {str(e)}") 
            return False


    def validar_mensajes(self, df):
        """Valida que los mensajes solo contengan caracteres permitidos"""
        mensajes_invalidos = []
        try:
            for idx, mensaje in df['mensaje'].items():
                if pd.notna(mensaje):
                    mensaje_str = str(mensaje)
                    for i, char in enumerate(mensaje_str):
                        if char not in self.caracteres_permitidos:
                            # Construir mensaje de error
                            error_detail = f"Fila {idx+2}: Carácter '{char}' (posición {i}) no permitido en mensaje."
                            mensajes_invalidos.append(error_detail)
                            
                            # Limitar el número de errores reportados para no sobrecargar
                            if len(mensajes_invalidos) >= 10: 
                                mensajes_invalidos.append("... (más errores encontrados)")
                                log.warning(f"Validación de mensajes detenida (límite alcanzado). Primer error: {mensajes_invalidos[0]}") # Log primer error
                                return "\n".join(mensajes_invalidos)
            
            if mensajes_invalidos:
                 log.warning(f"Se encontraron {len(mensajes_invalidos)} errores de caracteres en mensajes.") # Log resumen de errores
            else:
                 log.debug("Validación de caracteres en mensajes completada sin errores.") # Log éxito

            return "\n".join(mensajes_invalidos) if mensajes_invalidos else ""

        except KeyError:
            # Esto no debería pasar si validar_estructura_archivo funcionó
            log.error("Error crítico: La columna 'mensaje' no se encontró durante la validación de caracteres.")
            self.error_occurred.emit("Error interno: Falta la columna 'mensaje'.")
            return "Error interno: Falta la columna 'mensaje'." # Retornar mensaje de error
        except Exception as e:
            log.exception("Error inesperado durante la validación de mensajes:")
            self.error_occurred.emit(f"Error al validar mensajes: {str(e)}")
            return f"Error inesperado al validar mensajes: {str(e)}" # Retornar mensaje de error