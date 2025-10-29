from PySide6.QtCore import QSettings

class AppConfig:
    def __init__(self):
        self.settings = QSettings("MiEmpresa", "SistemaDevoluciones")
    
    def get_database_config(self):
        return {
            'host': self.settings.value("db_host", "localhost"),
            'port': self.settings.value("db_port", "5432"),
            'database': self.settings.value("db_name", "postgres"),
            'user': self.settings.value("db_user", "postgres"),
            'password': self.settings.value("db_password", "Roman_3119")
        }
    
    def set_database_config(self, config):
        for key, value in config.items():
            self.settings.setValue(f"db_{key}", value)
    
    def get_theme(self):
        return self.settings.value("theme", "system")
    
    def set_theme(self, theme):
        self.settings.setValue("theme", theme)