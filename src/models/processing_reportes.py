# Contenido para: src/models/processing_reportes.py

import pandas as pd
import os
from PySide6.QtCore import QThread, Signal
# Este SÍ es un import correcto para este archivo
from src.utils.file_handlers import detectar_separador_archivo 

class ReportesProcessingThread(QThread):
    """
    Hilo para procesar los archivos de reportes simples y generar estadísticas.
    """
    update_progress = Signal(int)
    update_status = Signal(str)
    finished_processing = Signal(pd.DataFrame) 
    error_occurred = Signal(str)
    
    columnas_requeridas = [
        'clienteid', 'numtelefono', 'identificador', 'estatus', 'clic',
        'rcs_entregable', 'articulo_clic', 'campaña', 'modalidad', 'leido'
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
                
                df = self.detectar_y_leer_archivo(file_path)
                if df is None:
                    continue 
                
                if not self.validar_estructura_archivo(df):
                    self.error_occurred.emit(f"El archivo {file_name} no tiene la estructura requerida.")
                    return
                
                df['estatus'] = pd.to_numeric(df['estatus'], errors='coerce').fillna(0).astype(int)
                df['leido'] = pd.to_numeric(df['leido'], errors='coerce').fillna(0).astype(int)
                df['modalidad'] = df['modalidad'].str.lower().str.strip()
                df['clic'] = df['clic'].str.lower().str.strip()

                total_original = len(df)
                enviados_rcs = len(df[(df['estatus'] == 1) & (df['modalidad'] == 'simple')])
                enviados_sms = len(df[(df['estatus'] == 1) & (df['modalidad'] == 'sms')])
                no_enviados = len(df[df['estatus'] == 0])
                clics = len(df[df['clic'] == 'si'])
                leidos_unicos = len(df[(df['estatus'] == 1) & (df['leido'] == 1) & (df['modalidad'] == 'simple')])
                no_leidos = len(df[df['leido'] == 0])

                stats = {
                    'CAMPAÑA': file_name,
                    'Total Original': total_original,
                    'Total Generada': total_original,
                    'Excluidos': 0,
                    'ENVIADOS RCS': enviados_rcs,
                    'ENVIADOS SMS': enviados_sms,
                    'NO ENVIADOS': no_enviados,
                    'CLICS': clics,
                    'LEIDOS UNICO': leidos_unicos,
                    'NO LEIDOS': no_leidos
                }
                all_stats.append(stats)
                self.update_progress.emit(progress)

            df_resumen = pd.DataFrame(all_stats)
            self.update_progress.emit(100)
            self.update_status.emit("Procesamiento de reportes completado")
            self.finished_processing.emit(df_resumen)
                
        except Exception as e:
            self.error_occurred.emit(f"Error inesperado en el procesamiento: {str(e)}")

    def detectar_y_leer_archivo(self, file_path):
        try:
            separador = detectar_separador_archivo(file_path)
            df = pd.read_csv(file_path, sep=separador, encoding='utf-8', low_memory=False)
            df.columns = df.columns.str.strip().str.lower()
            return df
        except Exception as e:
            self.error_occurred.emit(f"Error al leer archivo {os.path.basename(file_path)}: {str(e)}")
            return None

    def validar_estructura_archivo(self, df):
        columnas_archivo = set(df.columns)
        columnas_requeridas_set = set(col.lower() for col in self.columnas_requeridas)
        return columnas_requeridas_set.issubset(columnas_archivo)