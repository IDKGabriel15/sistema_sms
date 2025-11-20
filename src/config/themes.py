from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPalette, QColor

class ThemeManager:
    def __init__(self):
        self.settings = QSettings("MiEmpresa", "SistemaDevoluciones")
        self.current_theme = self.settings.value("theme", "system")
    
    def apply_theme(self, theme=None):
        """Aplica el tema a la aplicación completa"""
        app = QApplication.instance()
        if not app:
            return
            
        if theme:
            self.current_theme = theme
            self.settings.setValue("theme", theme)
        else:
            theme = self.current_theme
        
        if theme == "dark" or (theme == "system" and self.is_system_dark()):
            self.apply_dark_theme(app)
        else:
            self.apply_light_theme(app)
    
    def is_system_dark(self):
        palette = QApplication.palette()
        return palette.window().color().lightness() < 128
    
    def apply_dark_theme(self, app):
        """Aplica el tema oscuro"""
        from PySide6.QtWidgets import QApplication
        app.setStyle("Fusion")
        
        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        
        app.setPalette(dark_palette)
        
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #353535;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #404040;
            }
            QTabBar::tab {
                background-color: #505050;
                color: white;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2a82da;
            }
            QPushButton {
                background-color: #505050;
                color: white;
                border: 1px solid #666666;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #2a82da;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QListWidget {
                border: 1px solid #666666;
                border-radius: 4px;
                background-color: #2d2d2d;
                color: white;
            }
            QProgressBar {
                border: 1px solid #666666;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d2d;
                color: white;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
                border-radius: 3px;
            }
            QLabel {
                color: white;
            }
        """)
    
    def apply_light_theme(self, app):
        """Aplica el tema claro"""
        from PySide6.QtWidgets import QApplication
        app.setStyle("Fusion")
        app.setPalette(QApplication.style().standardPalette())
        
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e8e8e8;
                color: #333333;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2a82da;
                color: white;
            }
            QPushButton {
                background-color: #e8e8e8;
                color: #333333;
                border: 1px solid #c0c0c0;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
            }
            QPushButton:pressed {
                background-color: #2a82da;
                color: white;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #a0a0a0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #c0c0c0;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QListWidget {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                background-color: white;
                color: #333333;
            }
            QProgressBar {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                text-align: center;
                background-color: white;
                color: #333333;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
                border-radius: 3px;
            }
            QLabel {
                color: #333333;
            }
        """)