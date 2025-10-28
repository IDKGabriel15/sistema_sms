from PySide6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QTableWidget, QMessageBox, QWidget
from PySide6.QtCore import Qt

from ..components.base_tab import BaseTab

class Reporte2Tab(BaseTab):
    def __init__(self, db_connection, theme_manager):
        super().__init__(db_connection, theme_manager, "Reporte 2")
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("Reporte 2 - Estadísticas por Producto")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.btn_generar_reporte2 = QPushButton('Generar Reporte 2')
        self.btn_generar_reporte2.clicked.connect(self.generar_reporte2)
        layout.addWidget(self.btn_generar_reporte2)
        
        self.tabla_reporte2 = QTableWidget()
        layout.addWidget(self.tabla_reporte2)
        
        self.setLayout(layout)
    
    def generar_reporte2(self):
        QMessageBox.information(self, "Reporte 2", "Generando reporte tipo 2...")
