import pandas as pd
import os
import re

def detectar_separador_archivo(file_path):
    """Detecta el separador del archivo (coma o pipe)"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            primeras_lineas = [f.readline() for _ in range(5)]
        
        conteo_pipes = sum(line.count('|') for line in primeras_lineas)
        conteo_comas = sum(line.count(',') for line in primeras_lineas)
        
        return '|' if conteo_pipes > conteo_comas else ','
    except Exception as e:
        raise Exception(f"Error al detectar separador: {str(e)}")

def leer_archivo_csv(file_path):
    """Lee un archivo CSV detectando automáticamente el separador"""
    separador = detectar_separador_archivo(file_path)
    df = pd.read_csv(file_path, sep=separador, encoding='utf-8')
    df.columns = df.columns.str.strip()
    return df

def crear_nombre_archivo_seguro(nombre):
    """Crea un nombre de archivo seguro eliminando caracteres problemáticos"""
    nombre_seguro = re.sub(r'[<>:"/\\|?*]', '_', str(nombre))
    return nombre_seguro[:100]

def preparar_dataframe_exportacion(df):
    """Prepara el DataFrame con solo las columnas requeridas para exportación"""
    columnas_requeridas = ['clienteid', 'numtelefono', 'mensaje']
    columnas_disponibles = {col.lower(): col for col in df.columns}
    columnas_exportar = []
    
    for col in columnas_requeridas:
        if col in columnas_disponibles:
            columnas_exportar.append(columnas_disponibles[col])
    
    return df[columnas_exportar] if columnas_exportar else pd.DataFrame()