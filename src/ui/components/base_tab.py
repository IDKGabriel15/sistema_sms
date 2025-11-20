from PySide6.QtWidgets import QWidget

class BaseTab(QWidget):
    """Clase base para todas las pestañas"""
    
    def __init__(self, db_connection, theme_manager, title="Tab"):
        super().__init__()
        self.db_connection = db_connection
        self.theme_manager = theme_manager
        self.title = title
    
    def init_ui(self):
        """Método que deben implementar las subclases"""
        raise NotImplementedError("Las subclases deben implementar init_ui")
    
    def update_styles(self):
        """Actualizar estilos cuando cambia el tema"""
        pass
    
    def get_title(self):
        return self.title