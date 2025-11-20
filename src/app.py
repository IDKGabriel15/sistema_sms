from PySide6.QtWidgets import QMessageBox
from .config.settings import AppConfig
from .ui.main_window import MainWindow
from .database.connection import DatabaseConnection
from .config.themes import ThemeManager

class SistemaDevoluciones:
    def __init__(self, db_connection, username):
        self.config = AppConfig()
        self.db = db_connection
        self.current_user = username 
        self.theme_manager = ThemeManager()
        self.main_window = MainWindow(self.db, self.config)
    
    def setup_application(self):
        """Configuración inicial de la aplicación"""
        # Aplicar tema al inicio
        self.theme_manager.apply_theme()
        
        if not self.db.connect():
            QMessageBox.warning(
                None,
                "Conexión Fallida",
                "No se pudo conectar a la base de datos. La aplicación funcionará sin conexión a BD."
            )
    
    def show(self):
        self.main_window.show()