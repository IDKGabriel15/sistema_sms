import pandas as pd
import os
from PySide6.QtCore import QThread, Signal

class ProcessingThread(QThread):
    update_progress = Signal(int)
    update_status = Signal(str)
    finished_processing = Signal(dict)
    error_occurred = Signal(str)
    
    def __init__(self, file_paths, db_connection):
        super().__init__()
        self.file_paths = file_paths
        self.db_connection = db_connection
        self.caracteres_permitidos = ' É_!"#\'¤%&()*+-./<=>?$@0ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;\''
        self.columnas_requeridas = [
            'clienteid', 'nombre', 'apellidopaterno', 'apellidomaterno', 'numtelefono', 
            'mensaje', 'variable1', 'variable2', 'variable3', 'variable4', 'variable5', 
            'fechainsercion', 'fechaaenviar', 'horaaenviar', 'campana'
        ]
    
        def run(self):
            try:
                all_dataframes = {}
                tabla_resumen_data = []
                total_files = len(self.file_paths)
                
                for i, file_path in enumerate(self.file_paths):
                    self.update_status.emit(f"Procesando archivo {i+1}/{total_files}: {os.path.basename(file_path)}")
                    progress = int((i / total_files) * 80)
                    self.update_progress.emit(progress)
                    
                    # Detectar separador y leer archivo
                    df = self.detectar_y_leer_archivo(file_path)
                    if df is None:
                        continue
                    
                    # Validar estructura del archivo
                    if not self.validar_estructura_archivo(df):
                        self.error_occurred.emit(f"El archivo {os.path.basename(file_path)} no tiene la estructura requerida")
                        return
                    
                    # Validar mensajes
                    mensajes_invalidos = self.validar_mensajes(df)
                    if mensajes_invalidos:
                        self.error_occurred.emit(f"Caracteres no permitidos encontrados en el archivo {os.path.basename(file_path)}:\n{mensajes_invalidos}")
                        return
                    
                    # Procesar por campaña
                    campanas = df['campana'].unique()
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
                for campana, dfs in all_dataframes.items():
                    if dfs:
                        dataframes_consolidados[campana] = pd.concat(dfs, ignore_index=True)
                
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
                self.finished_processing.emit(resultado)
                    
            except Exception as e:
                self.error_occurred.emit(str(e))

    
    def detectar_y_leer_archivo(self, file_path):
        """Detecta el separador del archivo y lo lee"""
        try:
            # Leer primeras líneas para detectar separador
            with open(file_path, 'r', encoding='utf-8') as f:
                primeras_lineas = [f.readline() for _ in range(5)]
            
            # Contar pipes y comas
            conteo_pipes = sum(line.count('|') for line in primeras_lineas)
            conteo_comas = sum(line.count(',') for line in primeras_lineas)
            
            # Determinar separador
            separador = '|' if conteo_pipes > conteo_comas else ','
            
            # Leer archivo con el separador detectado
            df = pd.read_csv(file_path, sep=separador, encoding='utf-8')
            
            # Limpiar nombres de columnas (eliminar espacios extras)
            df.columns = df.columns.str.strip()
            
            return df
            
        except Exception as e:
            self.error_occurred.emit(f"Error al leer archivo {os.path.basename(file_path)}: {str(e)}")
            return None

    def validar_estructura_archivo(self, df):
        """Valida que el archivo tenga las columnas requeridas"""
        columnas_archivo = set(df.columns.str.strip().str.lower())
        columnas_requeridas = set(col.lower() for col in self.columnas_requeridas)
        
        return columnas_requeridas.issubset(columnas_archivo)

    def validar_mensajes(self, df):
        """Valida que los mensajes solo contengan caracteres permitidos"""
        mensajes_invalidos = []
        
        for idx, mensaje in df['mensaje'].items():
            if pd.notna(mensaje):
                mensaje_str = str(mensaje)
                for char in mensaje_str:
                    if char not in self.caracteres_permitidos:
                        mensajes_invalidos.append(f"Fila {idx+2}: '{mensaje_str}' - Carácter no permitido: '{char}'")
                        if len(mensajes_invalidos) >= 10:  # Limitar a 10 errores
                            mensajes_invalidos.append("... (más errores encontrados)")
                            return "\n".join(mensajes_invalidos)
        
        return "\n".join(mensajes_invalidos) if mensajes_invalidos else ""
