from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QTableWidget, QMessageBox, QWidget
from PySide6.QtCore import Qt

from ..components.base_tab import BaseTab

class Reporte1Tab(BaseTab):
    def __init__(self, db_connection, theme_manager):
        super().__init__(db_connection, theme_manager, "Reporte 1")
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Reporte 1 - Análisis de Devoluciones")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.btn_generar_reporte1 = QPushButton('Generar Reporte 1')
        self.btn_generar_reporte1.clicked.connect(self.generar_reporte1)
        layout.addWidget(self.btn_generar_reporte1)
        
        self.tabla_reporte1 = QTableWidget()
        layout.addWidget(self.tabla_reporte1)
        
        self.setLayout(layout)
    
    def generar_reporte1(self):
        QMessageBox.information(self, "Reporte 1", "Generando reporte tipo 1...")
