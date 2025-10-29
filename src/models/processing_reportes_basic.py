import pandas as pd
import os
from PySide6.QtCore import QThread, Signal
from src.utils.file_handlers import detectar_separador_archivo # Reutilizamos el detector

class ReportesBasicProcessingThread(QThread):
    """
    Hilo para procesar los archivos de reportes BASIC y generar estadísticas.
    """
    update_progress = Signal(int)
    update_status = Signal(str)
    finished_processing = Signal(pd.DataFrame) 
    error_occurred = Signal(str)
    
    # Columnas requeridas para los reportes BASIC
    columnas_requeridas = [
        'clienteid', 'telefono', 'estatus', 'modalidad', 'leido'
    ]

    def __init__(self, file_paths, db_connection):
        super().__init__()
        self.file_paths = file_paths
        self.db_connection = db_connection

    def run(self):
        try:
            all_stats = []
            total_files = len(self.file_paths)
            
            for i, file_path in enumerate(self.file_paths):
                file_name = os.path.basename(file_path)
                self.update_status.emit(f"Procesando archivo {i+1}/{total_files}: {file_name}")
                progress = int(((i + 1) / total_files) * 95) 
                
                # 1. Detectar y leer
                df = self.detectar_y_leer_archivo(file_path)
                if df is None:
                    continue 
                
                # 2. Validar estructura
                if not self.validar_estructura_archivo(df):
                    self.error_occurred.emit(f"El archivo {file_name} no tiene la estructura requerida.")
                    return
                
                # 3. Limpiar y convertir tipos de datos
                df['estatus'] = pd.to_numeric(df['estatus'], errors='coerce').fillna(0).astype(int)
                df['leido'] = pd.to_numeric(df['leido'], errors='coerce').fillna(0).astype(int)
                df['modalidad'] = df['modalidad'].str.lower().str.strip()

                # 4. Calcular estadísticas (Lógica para BASIC)
                total_original = len(df)
                
                # (estatus = 1 Y modalidad = 'basic')
                enviados_rcs = len(df[
                    (df['estatus'] == 1) & (df['modalidad'] == 'basic')
                ])
                
                # (estatus = 1 Y modalidad = 'sms')
                enviados_sms = len(df[
                    (df['estatus'] == 1) & (df['modalidad'] == 'sms')
                ])
                
                # (estatus = 0)
                no_enviados = len(df[df['estatus'] == 0])
                
                # (clics = 0)
                clics = 0
                
                # (estatus = 1 Y leido = 1 Y modalidad = 'basic')
                leidos_unicos = len(df[
                    (df['estatus'] == 1) & (df['leido'] == 1) & (df['modalidad'] == 'basic')
                ])
                
                # (leido = 0)
                no_leidos = len(df[df['leido'] == 0])

                # 5. Guardar resultados para este archivo
                stats = {
                    'CAMPAÑA': file_name,
                    'Total Original': total_original,
                    'Total Generada': total_original,
                    'Excluidos': 0,
                    'Enviados (RCS)': enviados_rcs,
                    'Enviados (SMS)': enviados_sms,
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
            self.finished_processing.emit(df_resumen)
                
        except Exception as e:
            self.error_occurred.emit(f"Error inesperado en el procesamiento: {str(e)}")

    def detectar_y_leer_archivo(self, file_path):
        """Detecta el separador y lee el CSV."""
        try:
            separador = detectar_separador_archivo(file_path)
            df = pd.read_csv(file_path, sep=separador, encoding='utf-8', low_memory=False)
            df.columns = df.columns.str.strip().str.lower() # Normalizar headers
            return df
        except Exception as e:
            self.error_occurred.emit(f"Error al leer archivo {os.path.basename(file_path)}: {str(e)}")
            return None

    def validar_estructura_archivo(self, df):
        """Valida que el archivo tenga las columnas requeridas."""
        columnas_archivo = set(df.columns)
        columnas_requeridas_set = set(col.lower() for col in self.columnas_requeridas)
        
        return columnas_requeridas_set.issubset(columnas_archivo)