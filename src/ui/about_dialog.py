# Contenido COMPLETO y CORREGIDO para: src/ui/about_dialog.py

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, __version__ as PySideVersion
import sys 

class AboutDialog(QDialog):
    # 1. Modificar __init__ para aceptar theme_manager
    def __init__(self, theme_manager, parent=None): 
        super().__init__(parent)
        self.theme_manager = theme_manager # Guardar theme_manager
        self.setWindowTitle("Acerca de Sistema de SMS")
        self.setMinimumWidth(350)
        
        self.init_ui()
        self.apply_styles() # Aplicar estilos basados en el tema

    def init_ui(self):
        # (El layout y los widgets no cambian, solo sus estilos)
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)

        title_label = QLabel("Sistema de Devoluciones y Reportes")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("aboutTitleLabel")
        layout.addWidget(title_label)
        
        version_label = QLabel("Versión 1.0.0") 
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setObjectName("aboutVersionLabel")
        layout.addWidget(version_label)
        
        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Fixed))

        credits_label = QLabel("Desarrollado por:")
        layout.addWidget(credits_label)
        
        developer_label = QLabel("  • Gabriel Roman") 
        developer_label.setObjectName("aboutDeveloperLabel")
        layout.addWidget(developer_label)

        area_label = QLabel("  • Procesamiento de Información (PDI)")
        area_label.setObjectName("aboutAreaLabel")
        layout.addWidget(area_label)

        layout.addSpacerItem(QSpacerItem(20, 15, QSizePolicy.Minimum, QSizePolicy.Expanding))


        button_layout = QHBoxLayout()
        button_layout.addStretch(1) 
        close_button = QPushButton("Cerrar")
        close_button.clicked.connect(self.accept) 
        button_layout.addWidget(close_button)
        button_layout.addStretch(1) 
        
        layout.addLayout(button_layout)

    # 2. Reemplazar apply_styles con lógica de tema
    def apply_styles(self):
        """Aplica estilos según el tema actual."""
        is_dark = self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        )

        if is_dark:
            # --- ESTILOS OSCUROS ---
            self.setStyleSheet("""
                QDialog {
                    background-color: #353535; 
                    color: white;
                }
                QLabel { /* Estilo general etiquetas */
                    color: white;
                }
                QLabel#aboutTitleLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #e0e0e0;
                    margin-bottom: 2px;
                }
                 QLabel#aboutVersionLabel {
                    font-size: 11px;
                    color: #aaaaaa; /* Gris claro */
                    margin-bottom: 10px;
                }
                QLabel#aboutDeveloperLabel, QLabel#aboutAreaLabel {
                    font-size: 12px;
                    margin-left: 10px; 
                }
                 QLabel#aboutTechLabel {
                    font-size: 10px;
                    color: #999999; /* Gris medio */
                    margin-top: 10px;
                }
                QPushButton { /* Hereda estilos globales del tema oscuro */
                    padding: 5px 15px;
                    min-width: 70px;
                    /* Estilos específicos si son necesarios */
                }
            """)
        else:
            # --- ESTILOS CLAROS ---
            self.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5; 
                    color: #333333;
                }
                 QLabel { 
                    color: #333333;
                }
                QLabel#aboutTitleLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #111111; /* Negro */
                    margin-bottom: 2px;
                }
                 QLabel#aboutVersionLabel {
                    font-size: 11px;
                    color: #555555; /* Gris oscuro */
                    margin-bottom: 10px;
                }
                QLabel#aboutDeveloperLabel, QLabel#aboutAreaLabel {
                    font-size: 12px;
                    margin-left: 10px; 
                }
                 QLabel#aboutTechLabel {
                    font-size: 10px;
                    color: #777777; /* Gris medio */
                    margin-top: 10px;
                }
                QPushButton { /* Hereda estilos globales del tema claro */
                    padding: 5px 15px;
                    min-width: 70px;
                    /* Estilos específicos si son necesarios */
                }
            """)