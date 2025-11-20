# Contenido modificado para: main.py

import sys
import os
import logging 

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox 
from src.app import SistemaDevoluciones
# --- MODIFICADO --- Comentar la importación de DatabaseConnection si no la usas temporalmente
# from src.database.connection import DatabaseConnection 
# --- MODIFICADO --- Comentar la importación de LoginDialog
# from src.ui.login_dialog import LoginDialog 
from src.config.themes import ThemeManager 
from src.utils.logger_setup import log, set_current_user 


if __name__ == '__main__':
    log.info("=====================================")
    log.info("Iniciando Sistema de Devoluciones (MODO SIN LOGIN)...") # Mensaje modificado
    
    app = QApplication(sys.argv)
    
    theme_manager = ThemeManager()
    theme_manager.apply_theme() 
    
    # --- MODIFICADO --- Inicio: Saltar conexión y login ---
    # 1. Comentar la creación y conexión de la BD real
    # db_conn = DatabaseConnection()
    # if not db_conn.connect():
    #      log.critical("Error crítico: No se pudo conectar a la base de datos.")
    #      QMessageBox.critical(None, "Error Crítico", 
    #                           "No se pudo conectar a la base de datos.\nLa aplicación no puede continuar.")
    #      sys.exit(1) 
    # log.info("Conexión a la base de datos establecida.")
    
    # 2. Comentar la creación y ejecución del diálogo de Login
    # login_dialog = LoginDialog(db_conn, theme_manager)
    # if login_dialog.exec() == QDialog.Accepted:
        # logged_in_user = login_dialog.username_input.text().strip()
        # set_current_user(logged_in_user) 
        # log.info(f"Usuario '{logged_in_user}' inició sesión exitosamente.")
        
        # --- Simular usuario y conexión nula ---
    db_conn = None # Pasar None como conexión
    logged_in_user = "UsuarioPrueba" # Usar un nombre de usuario temporal
    set_current_user(logged_in_user)
    log.info(f"Ejecutando en modo sin login como '{logged_in_user}'. Conexión a BD desactivada.")
        
        # --- Crear y mostrar la ventana principal directamente ---
    window = SistemaDevoluciones(db_conn, logged_in_user) # Pasar None y usuario de prueba
    window.show()
    exit_code = app.exec()
    log.info(f"Aplicación cerrada con código de salida: {exit_code}")
    sys.exit(exit_code)
        
    # else: # Este 'else' ya no es necesario si siempre entramos
    #     log.warning("Login cancelado o fallido. Cerrando aplicación.")
    #     # if db_conn: # Cerrar solo si se creó
    #     #     db_conn.close()
    #     sys.exit(0) 
    # --- MODIFICADO --- Fin: Saltar conexión y login ---