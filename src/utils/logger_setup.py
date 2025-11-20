# Contenido para: src/utils/logger_setup.py

import logging
import os
from logging.handlers import RotatingFileHandler

# Variable global para almacenar el nombre de usuario actual
_current_user = "System" 

def set_current_user(username):
    """Establece el nombre de usuario global para los logs."""
    global _current_user
    _current_user = username if username else "Unknown"

class UserLogFilter(logging.Filter):
    """Filtro para añadir el nombre de usuario a cada registro de log."""
    def filter(self, record):
        record.username = _current_user
        return True

def setup_logging():
    """Configura el sistema de logging para la aplicación."""

    # Crear la carpeta 'logs' si no existe (en la raíz del proyecto)
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    log_file = os.path.join(log_dir, 'app.log')

    # Configurar el formato del log
    log_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(username)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Configurar el manejador de archivos rotativos
    # Rotará cuando el archivo alcance 1MB, manteniendo 5 archivos de respaldo.
    file_handler = RotatingFileHandler(
        log_file, maxBytes=1*1024*1024, backupCount=5, encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    file_handler.addFilter(UserLogFilter()) # Añadir nuestro filtro de usuario

    # Obtener el logger raíz y configurarlo
    logger = logging.getLogger()
    logger.setLevel(logging.INFO) # Nivel mínimo para registrar (INFO, WARNING, ERROR, CRITICAL)

    # Evitar añadir manejadores duplicados si setup_logging se llama varias veces
    if not logger.hasHandlers():
        logger.addHandler(file_handler)

        # Opcional: Añadir un manejador para mostrar logs en consola también
        # console_handler = logging.StreamHandler()
        # console_handler.setFormatter(log_format)
        # console_handler.addFilter(UserLogFilter())
        # logger.addHandler(console_handler)

    return logger

# Configurar el logging al importar este módulo por primera vez
log = setup_logging()

# Ejemplo de uso (no es necesario llamarlo directamente desde otros módulos):
# log.info("Mensaje informativo")
# log.warning("Advertencia")
# log.error("Ocurrió un error")