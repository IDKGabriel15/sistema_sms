# Contenido modificado para: main.py

import sys
import os
import logging # <-- Añadir import

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PySide6.QtWidgets import QApplication, QDialog, QMessageBox # QMessageBox añadido
from src.app import SistemaDevoluciones
from src.database.connection import DatabaseConnection 
from src.ui.login_dialog import LoginDialog 
from src.config.themes import ThemeManager 
# --- INICIO CAMBIOS LOGGING ---
from src.utils.logger_setup import log, set_current_user # Importar logger y función
# --- FIN CAMBIOS LOGGING ---


if __name__ == '__main__':
    # --- INICIO CAMBIOS LOGGING ---
    # Configurar logging ANTES que nada
    log.info("=====================================")
    log.info("Iniciando Sistema de Devoluciones...")
    # --- FIN CAMBIOS LOGGING ---
    
    app = QApplication(sys.argv)
    
    theme_manager = ThemeManager()
    theme_manager.apply_theme() 
    
    db_conn = DatabaseConnection()
    if not db_conn.connect():
         # --- INICIO CAMBIOS LOGGING ---
         log.critical("Error crítico: No se pudo conectar a la base de datos.")
         # --- FIN CAMBIOS LOGGING ---
         QMessageBox.critical(None, "Error Crítico", 
                              "No se pudo conectar a la base de datos.\nLa aplicación no puede continuar.")
         sys.exit(1) 
    # --- INICIO CAMBIOS LOGGING ---
    log.info("Conexión a la base de datos establecida.")
    # --- FIN CAMBIOS LOGGING ---

    login_dialog = LoginDialog(db_conn, theme_manager)
    
    if login_dialog.exec() == QDialog.Accepted:
        # --- INICIO CAMBIOS LOGGING ---
        # Guardar el nombre de usuario para los logs
        logged_in_user = login_dialog.username_input.text().strip()
        set_current_user(logged_in_user) 
        log.info(f"Usuario '{logged_in_user}' inició sesión exitosamente.")
        # --- FIN CAMBIOS LOGGING ---
        
        # Pasar el nombre de usuario a la clase principal de la app
        window = SistemaDevoluciones(db_conn, logged_in_user) 
        window.show()
        exit_code = app.exec()
        log.info(f"Aplicación cerrada con código de salida: {exit_code}")
        sys.exit(exit_code)
    else:
        # --- INICIO CAMBIOS LOGGING ---
        log.warning("Login cancelado o fallido. Cerrando aplicación.")
        # --- FIN CAMBIOS LOGGING ---
        db_conn.close()
        sys.exit(0)