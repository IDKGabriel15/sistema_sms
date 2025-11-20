# Contenido COMPLETO y CORREGIDO para: src/ui/main_window.py

from PySide6.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, QLabel)
from PySide6.QtGui import QAction, QIcon
import os
import sys

# Importar las pestañas
from src.ui.tabs.DevolucionesTab import DevolucionesTab
from src.ui.tabs.ReportesSimplesTab import ReportesSimplesTab
from src.ui.tabs.ReportesDirectoTab import ReportesDirectoTab
# --- INICIO CAMBIO ---
# 1. Importar la nueva pestaña (asegúrate de que el archivo y la clase existan)
from src.ui.tabs.ReportesBasicTab import ReportesBasicTab
# --- FIN CAMBIO ---

# Importar ThemeManager y AboutDialog
from src.config.themes import ThemeManager
from .about_dialog import AboutDialog

# Función auxiliar para obtener la ruta correcta a los recursos
# (Asegúrate de que esta función esté definida en tu archivo)
def resource_path(relative_path):
    """ Obtiene la ruta absoluta al recurso, funciona para dev y para PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self, db_connection, config):
        super().__init__()
        self.db_connection = db_connection
        self.config = config
        self.theme_manager = ThemeManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Sistema de SMS') # Título actualizado
        self.setGeometry(100, 100, 1400, 900)

        # --- ICONO DE VENTANA ---
        icon_path_ventana = resource_path("app_icon.png") # O "app_icon.ico"

        if os.path.exists(icon_path_ventana):
             self.setWindowIcon(QIcon(icon_path_ventana))
        else:
             print(f"Advertencia: No se encontró el icono de la ventana en {icon_path_ventana}")
        # --- FIN ICONO ---

        # Widget central con pestañas
        tab_widget = QTabWidget()

        # Crear pestañas (pasando theme_manager)
        self.devoluciones_tab = DevolucionesTab(self.db_connection, self.theme_manager)
        self.reporte1_tab = ReportesSimplesTab(self.db_connection, self.theme_manager)
        self.reporte_directo_tab = ReportesDirectoTab(self.db_connection, self.theme_manager)
        # --- INICIO CAMBIO ---
        # 2. Crear instancia de la nueva pestaña
        self.reporte_basic_tab = ReportesBasicTab(self.db_connection, self.theme_manager)
        # --- FIN CAMBIO ---

        # Añadir pestañas al widget
        tab_widget.addTab(self.devoluciones_tab, "📁 " + self.devoluciones_tab.get_title())
        tab_widget.addTab(self.reporte1_tab, "📈 " + self.reporte1_tab.get_title())
        tab_widget.addTab(self.reporte_basic_tab, "📄 " + self.reporte_basic_tab.get_title())
        tab_widget.addTab(self.reporte_directo_tab, "📊 " + self.reporte_directo_tab.get_title())
        # --- FIN CAMBIO ---

        self.setCentralWidget(tab_widget)

        # --- BARRA DE ESTADO ---
        self.statusBar = QStatusBar(self)
        self.setStatusBar(self.statusBar)
        self.credits_label = QLabel("Desarrollado por Gabriel Roman - PDI")
        self.statusBar.addPermanentWidget(self.credits_label)
        self.update_status_bar_style()
        # --- FIN BARRA DE ESTADO ---

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

        # Menú Ayuda
        help_menu = menubar.addMenu('❓ Ayuda')
        about_action = QAction('ℹ️ Acerca de...', self)
        about_action.triggered.connect(self.show_about_dialog)
        help_menu.addAction(about_action)

    def cambiar_tema(self, tema):
        """Cambia el tema de la aplicación y actualiza estilos."""
        self.theme_manager.apply_theme(tema)

        if self.centralWidget():
            for i in range(self.centralWidget().count()):
                tab = self.centralWidget().widget(i)
                if hasattr(tab, 'update_styles'):
                    tab.update_styles()

        self.update_status_bar_style()

    def update_status_bar_style(self):
        """Actualiza el color del texto de créditos en la barra de estado."""
        if hasattr(self, 'credits_label'):
            is_dark = self.theme_manager.current_theme == "dark" or (
                self.theme_manager.current_theme == "system" and
                self.theme_manager.is_system_dark()
            )
            if is_dark:
                self.credits_label.setStyleSheet("color: #AAAAAA;")
            else:
                self.credits_label.setStyleSheet("color: #555555;")

    def show_about_dialog(self):
        """Muestra el diálogo 'Acerca de...'."""
        dialog = AboutDialog(self.theme_manager, self)
        dialog.exec()