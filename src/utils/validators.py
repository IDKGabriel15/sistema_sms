import pandas as pd

def validar_estructura_archivo(df, columnas_requeridas):
    """Valida que el archivo tenga las columnas requeridas"""
    columnas_archivo = set(df.columns.str.strip().str.lower())
    columnas_requeridas = set(col.lower() for col in columnas_requeridas)
    return columnas_requeridas.issubset(columnas_archivo)

def validar_mensajes(df, caracteres_permitidos):
    """Valida que los mensajes solo contengan caracteres permitidos"""
    mensajes_invalidos = []
    
    for idx, mensaje in df['mensaje'].items():
        if pd.notna(mensaje):
            mensaje_str = str(mensaje)
            for char in mensaje_str:
                if char not in caracteres_permitidos:
                    mensajes_invalidos.append(f"Fila {idx+2}: '{mensaje_str}' - Carácter no permitido: '{char}'")
                    if len(mensajes_invalidos) >= 10:
                        mensajes_invalidos.append("... (más errores encontrados)")
                        return "\n".join(mensajes_invalidos)
    
    return "\n".join(mensajes_invalidos) if mensajes_invalidos else ""