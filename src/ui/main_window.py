from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtGui import QAction

from src.ui.tabs.DevolucionesTab import DevolucionesTab
from src.ui.tabs.ReportesSimplesTab import ReportesSimplesTab 
from src.ui.tabs.ReportesBasicTab import ReportesBasicTab
from src.ui.tabs.ReportesDirectoTab import ReportesDirectoTab 


from src.config.themes import ThemeManager

class MainWindow(QMainWindow):
    def __init__(self, db_connection, config):
        super().__init__()
        self.db_connection = db_connection
        self.config = config
        self.theme_manager = ThemeManager()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('📊 Sistema de Devoluciones y Reportes')
        self.setGeometry(100, 100, 1400, 900)

        tab_widget = QTabWidget()

        # --- Crear pestañas ---
        self.devoluciones_tab = DevolucionesTab(self.db_connection, self.theme_manager)
        self.reporte1_tab = ReportesSimplesTab(self.db_connection, self.theme_manager) 
        self.reporte2_tab = ReportesBasicTab(self.db_connection, self.theme_manager)
        self.reporte_directo_tab = ReportesDirectoTab(self.db_connection, self.theme_manager) # <-- Añadir
        
        # --- Añadir pestañas al widget ---
        tab_widget.addTab(self.devoluciones_tab, "📁 " + self.devoluciones_tab.get_title())
        tab_widget.addTab(self.reporte1_tab, "📈 " + self.reporte1_tab.get_title())
        tab_widget.addTab(self.reporte2_tab, "📊 " + self.reporte2_tab.get_title())
        tab_widget.addTab(self.reporte_directo_tab, "📊 " + self.reporte_directo_tab.get_title()) # <-- Añadir (ícono puede cambiar)
        
        self.setCentralWidget(tab_widget)
        self.create_menus()
    
    # ... (El resto del archivo 'main_window.py' no necesita cambios) ...

    def create_menus(self):
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu('📁 Archivo')
        exit_action = QAction('🚪 Salir', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        theme_menu = menubar.addMenu('🎨 Tema')
        
        system_theme_action = QAction('🌓 Tema del Sistema', self)
        system_theme_action.triggered.connect(lambda: self.cambiar_tema("system"))
        theme_menu.addAction(system_theme_action)
        
        light_theme_action = QAction('☀️ Tema Claro', self)
        light_theme_action.triggered.connect(lambda: self.cambiar_tema("light"))
        theme_menu.addAction(light_theme_action)
        
        dark_theme_action = QAction('🌙 Tema Oscuro', self)
        dark_theme_action.triggered.connect(lambda: self.cambiar_tema("dark"))
        theme_menu.addAction(dark_theme_action)

    def cambiar_tema(self, tema):
        self.theme_manager.apply_theme(tema)
        for i in range(self.centralWidget().count()):
            tab = self.centralWidget().widget(i)
            if hasattr(tab, 'update_styles'):
                tab.update_styles()