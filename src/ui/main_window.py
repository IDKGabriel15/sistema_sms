from PySide6.QtWidgets import QMainWindow, QTabWidget
from PySide6.QtGui import QAction

from src.ui.tabs.DevolucionesTab import DevolucionesTab
from src.ui.tabs.Reporte1Tab import Reporte1Tab
from src.ui.tabs.Reporte2Tab import Reporte2Tab
from src.ui.tabs.Reporte3Tab import Reporte3Tab

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

        # Widget central con pestañas
        tab_widget = QTabWidget()

        # Crear pestañas
        self.devoluciones_tab = DevolucionesTab(self.db_connection, self.theme_manager)
        self.reporte1_tab = Reporte1Tab(self.db_connection, self.theme_manager)
        self.reporte2_tab = Reporte2Tab(self.db_connection, self.theme_manager)
        self.reporte3_tab = Reporte3Tab(self.db_connection, self.theme_manager)
        
        tab_widget.addTab(self.devoluciones_tab, "📁 " + self.devoluciones_tab.get_title())
        tab_widget.addTab(self.reporte1_tab, "📈 " + self.reporte1_tab.get_title())
        tab_widget.addTab(self.reporte2_tab, "📊 " + self.reporte2_tab.get_title())
        tab_widget.addTab(self.reporte3_tab, "📋 " + self.reporte3_tab.get_title())

        self.setCentralWidget(tab_widget)
        self.create_menus()
    
    def create_menus(self):
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu('📁 Archivo')
        exit_action = QAction('🚪 Salir', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Tema
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
        """Cambia el tema de la aplicación"""
        self.theme_manager.apply_theme(tema)
        # Actualizar todas las pestañas
        for i in range(self.centralWidget().count()):
            tab = self.centralWidget().widget(i)
            if hasattr(tab, 'update_styles'):
                tab.update_styles()