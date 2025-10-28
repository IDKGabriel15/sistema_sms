from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QTableWidget, QMessageBox, QWidget
from PySide6.QtCore import Qt

from ..components.base_tab import BaseTab


class Reporte3Tab(BaseTab):
    def __init__(self, db_connection, theme_manager):
        super().__init__(db_connection, theme_manager, "Reporte 3")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Reporte 3 - Resumen Mensual")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.btn_generar_reporte3 = QPushButton('Generar Reporte 3')
        self.btn_generar_reporte3.clicked.connect(self.generar_reporte3)
        layout.addWidget(self.btn_generar_reporte3)
        
        self.tabla_reporte3 = QTableWidget()
        layout.addWidget(self.tabla_reporte3)
        
        self.setLayout(layout)
    
    def generar_reporte3(self):
        QMessageBox.information(self, "Reporte 3", "Generando reporte tipo 3...")
        