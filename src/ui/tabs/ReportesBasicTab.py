from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                               QTableWidgetItem, QFileDialog, QMessageBox, QLabel, 
                               QProgressBar, QListWidget, QHeaderView, QAbstractItemView, 
                               QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import os
import pandas as pd

from ..components.base_tab import BaseTab
# ¡Importamos el NUEVO hilo de procesamiento!
from src.models.processing_reportes_basic import ReportesBasicProcessingThread 

class ReportesBasicTab(BaseTab):
    def __init__(self, db_connection, theme_manager):
        # Título de la pestaña
        super().__init__(db_connection, theme_manager, "Reportes Basic")
        self.df_resultados = pd.DataFrame() 
        self.selected_files = []
        self.init_ui()
    
    def init_ui(self):
        # La UI es idéntica a la de Reportes Simples, solo cambiamos títulos
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ========== GRUPO 1: SELECCIÓN DE ARCHIVOS ==========
        file_group = QGroupBox("Gestión de Reportes Basic") # Título cambiado
        file_layout = QVBoxLayout()
        
        file_buttons_layout = QHBoxLayout()
        
        self.btn_cargar = QPushButton('📁 Cargar CSV')
        self.btn_cargar.clicked.connect(self.cargar_archivos)
        self.btn_cargar.setToolTip("Seleccionar reportes BASIC para procesar") # Tooltip cambiado
        file_buttons_layout.addWidget(self.btn_cargar)
        
        self.btn_limpiar = QPushButton('🗑️ Limpiar')
        self.btn_limpiar.clicked.connect(self.limpiar_seleccion)
        self.btn_limpiar.setToolTip("Limpiar lista de archivos seleccionados")
        file_buttons_layout.addWidget(self.btn_limpiar)
        
        self.btn_procesar = QPushButton('⚡ Procesar')
        self.btn_procesar.clicked.connect(self.procesar_archivos)
        self.btn_procesar.setEnabled(False)
        self.btn_procesar.setToolTip("Procesar reportes seleccionados")
        file_buttons_layout.addWidget(self.btn_procesar)
        
        file_buttons_layout.addStretch(1)
        
        self.lbl_archivos_seleccionados = QLabel('0 archivos')
        self.lbl_archivos_seleccionados.setStyleSheet("font-weight: bold; color: #2a82da;")
        file_buttons_layout.addWidget(self.lbl_archivos_seleccionados)
        
        file_layout.addLayout(file_buttons_layout)
        
        self.lista_archivos = QListWidget()
        self.lista_archivos.setMaximumHeight(120)
        self.lista_archivos.setToolTip("Archivos seleccionados para procesar")
        file_layout.addWidget(self.lista_archivos)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # ========== GRUPO 2: PROGRESO Y ESTADO ==========
        progress_group = QGroupBox("Progreso")
        progress_layout = QVBoxLayout()
        
        self.lbl_estado = QLabel('Listo para procesar')
        self.actualizar_estilo_estado()
        progress_layout.addWidget(self.lbl_estado)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

        # ========== GRUPO 3: RESULTADOS ==========
        results_group = QGroupBox("Resultados de Reportes Basic") # Título cambiado
        results_layout = QVBoxLayout()
        
        self.tabla_resumen = QTableWidget()
        self.actualizar_estilo_tabla()
        self.tabla_resumen.setAlternatingRowColors(True)
        self.tabla_resumen.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_resumen.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_resumen.setSortingEnabled(True)
        self.tabla_resumen.setMinimumHeight(250)
        
        header = self.tabla_resumen.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setStretchLastSection(True)
        
        vertical_header = self.tabla_resumen.verticalHeader()
        vertical_header.setDefaultSectionSize(35)
        
        results_layout.addWidget(self.tabla_resumen)
        
        self.lbl_info_adicional = QLabel('')
        self.actualizar_estilo_info_adicional()
        results_layout.addWidget(self.lbl_info_adicional)
        
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

    # --- MÉTODOS DE ESTILO (Idénticos) ---

    def actualizar_estilo_estado(self):
        if self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        ):
            self.lbl_estado.setStyleSheet("QLabel { padding: 5px; background-color: #1e3a5f; border-radius: 3px; color: white; }")
        else:
            self.lbl_estado.setStyleSheet("QLabel { padding: 5px; background-color: #e8f4fd; border-radius: 3px; color: #333333; }")

    def actualizar_estilo_info_adicional(self):
        if self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        ):
            self.lbl_info_adicional.setStyleSheet("QLabel { background-color: #2d2d2d; color: #ffffff; padding: 8px; border-radius: 3px; border: 1px solid #555555; font-weight: bold; margin-top: 5px; }")
        else:
            self.lbl_info_adicional.setStyleSheet("QLabel { background-color: #e9ecef; color: #212529; padding: 8px; border-radius: 3px; border: 1px solid #ced4da; font-weight: bold; margin-top: 5px; }")

    def actualizar_estilo_tabla(self):
        dark_style = """
            QTableWidget { background-color: #2d2d2d; alternate-background-color: #3a3a3a; gridline-color: #555555; border: 1px solid #555555; border-radius: 4px; color: #ffffff; }
            QTableWidget::item { padding: 6px; border: none; }
            QTableWidget::item:selected { background-color: #2a82da; color: white; }
            QHeaderView::section { background-color: #404040; color: white; padding: 8px; border: 1px solid #555555; font-weight: bold; }
        """
        light_style = """
            QTableWidget { background-color: white; alternate-background-color: #f8f9fa; gridline-color: #dee2e6; border: 1px solid #dee2e6; border-radius: 4px; color: #212529; }
            QTableWidget::item { padding: 6px; border: none; }
            QTableWidget::item:selected { background-color: #007bff; color: white; }
            QHeaderView::section { background-color: #343a40; color: white; padding: 8px; border: 1px solid #454d55; font-weight: bold; }
        """
        if self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        ):
            self.tabla_resumen.setStyleSheet(dark_style)
        else:
            self.tabla_resumen.setStyleSheet(light_style)

    def update_styles(self):
        self.actualizar_estilo_estado()
        self.actualizar_estilo_info_adicional()
        self.actualizar_estilo_tabla()
        if not self.df_resultados.empty:
            self.mostrar_resultados(self.df_resultados)

    # --- MÉTODOS DE FUNCIONALIDAD (Actualizados) ---

    def cargar_archivos(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 'Seleccionar archivos CSV', '', 'Archivos CSV (*.csv);;Todos los archivos (*)'
        )
        if file_paths:
            self.selected_files.extend(file_paths)
            self.actualizar_lista_archivos()
            self.btn_procesar.setEnabled(len(self.selected_files) > 0)
            self.lbl_estado.setText(f"{len(file_paths)} archivo(s) agregado(s)")

    def limpiar_seleccion(self):
        self.selected_files.clear()
        self.lista_archivos.clear()
        self.lbl_archivos_seleccionados.setText('0 archivos')
        self.btn_procesar.setEnabled(False)
        self.lbl_estado.setText('Selección limpiada')
        self.tabla_resumen.setRowCount(0)
        self.tabla_resumen.setColumnCount(0)
        self.lbl_info_adicional.setText('')
        self.df_resultados = pd.DataFrame() 

    def actualizar_lista_archivos(self):
        self.lista_archivos.clear()
        for file_path in self.selected_files:
            self.lista_archivos.addItem(os.path.basename(file_path))
        self.lbl_archivos_seleccionados.setText(f'{len(self.selected_files)} archivos')

    def procesar_archivos(self):
        if not self.selected_files:
            QMessageBox.warning(self, "Advertencia", "No hay archivos seleccionados para procesar")
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.btn_cargar.setEnabled(False)
        self.btn_procesar.setEnabled(False)
        self.btn_limpiar.setEnabled(False)
        self.lbl_estado.setText("Iniciando procesamiento de reportes...")

        # ¡Usamos el hilo de BASIC!
        self.thread = ReportesBasicProcessingThread(self.selected_files, self.db_connection)
        self.thread.update_progress.connect(self.progress_bar.setValue)
        self.thread.update_status.connect(self.lbl_estado.setText)
        self.thread.finished_processing.connect(self.mostrar_resultados)
        self.thread.error_occurred.connect(self.mostrar_error)
        self.thread.start()

    def mostrar_resultados(self, df_resumen):
        self.df_resultados = df_resumen
        
        self.progress_bar.setVisible(False)
        self.btn_cargar.setEnabled(True)
        self.btn_procesar.setEnabled(True)
        self.btn_limpiar.setEnabled(True)

        if not self.df_resultados.empty:
            headers = self.df_resultados.columns.tolist()
            self.tabla_resumen.setRowCount(self.df_resultados.shape[0])
            self.tabla_resumen.setColumnCount(self.df_resultados.shape[1])
            self.tabla_resumen.setHorizontalHeaderLabels(headers)

            font_contenido = QFont()
            font_contenido.setPointSize(9)

            is_dark = self.theme_manager.current_theme == "dark" or (
                self.theme_manager.current_theme == "system" and 
                self.theme_manager.is_system_dark()
            )
            color_texto = QColor(255, 255, 255) if is_dark else QColor(33, 37, 41)
            
            for row in range(self.df_resultados.shape[0]):
                if is_dark:
                    bg_color = QColor(45, 45, 45) if row % 2 == 0 else QColor(58, 58, 58)
                else:
                    bg_color = QColor(255, 255, 255) if row % 2 == 0 else QColor(248, 249, 250)

                for col in range(self.df_resultados.shape[1]):
                    value = str(self.df_resultados.iat[row, col])
                    item = QTableWidgetItem(value)
                    item.setFont(font_contenido)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(color_texto)
                    item.setBackground(bg_color)
                    self.tabla_resumen.setItem(row, col, item)

            self.tabla_resumen.resizeColumnsToContents()
            
            total_archivos = len(self.df_resultados)
            # Sumamos el total de registros de la columna
            total_registros = self.df_resultados['Total Original'].sum()
            
            info_text = f"📊 RESUMEN | Reportes Procesados: {total_archivos} | Registros Totales: {total_registros:,}"
            self.lbl_info_adicional.setText(info_text)
            
            self.lbl_estado.setText(f"✅ Procesamiento completado - {total_archivos} reportes, {total_registros:,} registros analizados")
        else:
            self.lbl_estado.setText("⚠️ Procesamiento completado pero no se encontraron datos válidos")
            self.lbl_info_adicional.setText("No se encontraron datos válidos para mostrar")

    def mostrar_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.btn_cargar.setEnabled(True)
        self.btn_procesar.setEnabled(True)
        self.btn_limpiar.setEnabled(True)
        QMessageBox.critical(self, '❌ Error', f'Error al procesar los archivos:\n{error_msg}')
        self.lbl_estado.setText('❌ Error en el procesamiento')