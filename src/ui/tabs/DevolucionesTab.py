from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                               QTableWidgetItem, QFileDialog, QMessageBox, QLabel, 
                               QProgressBar, QListWidget, QHeaderView, QAbstractItemView, 
                               QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor
import os
import re
import pandas as pd

from ..components.base_tab import BaseTab
from src.models.processing import ProcessingThread
from src.utils.file_handlers import crear_nombre_archivo_seguro
from src.utils.validators import validar_estructura_archivo, validar_mensajes

class DevolucionesTab(BaseTab):
    def __init__(self, db_connection, theme_manager):
        super().__init__(db_connection, theme_manager, "Generar Devoluciones")
        self.dataframes_procesados = {}
        self.df_resumen = None
        self.selected_files = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        # ========== GRUPO 1: SELECCIÓN DE ARCHIVOS ==========
        file_group = QGroupBox("Gestión de Archivos")
        file_layout = QVBoxLayout()
        
        # Botones de archivos en una fila
        file_buttons_layout = QHBoxLayout()
        
        self.btn_cargar = QPushButton('📁 Cargar CSV')
        self.btn_cargar.clicked.connect(self.cargar_archivos)
        self.btn_cargar.setToolTip("Seleccionar archivos CSV para procesar")
        file_buttons_layout.addWidget(self.btn_cargar)
        
        self.btn_limpiar = QPushButton('🗑️ Limpiar')
        self.btn_limpiar.clicked.connect(self.limpiar_seleccion)
        self.btn_limpiar.setToolTip("Limpiar lista de archivos seleccionados")
        file_buttons_layout.addWidget(self.btn_limpiar)
        
        self.btn_procesar = QPushButton('⚡ Procesar')
        self.btn_procesar.clicked.connect(self.procesar_archivos)
        self.btn_procesar.setEnabled(False)
        self.btn_procesar.setToolTip("Procesar archivos seleccionados")
        file_buttons_layout.addWidget(self.btn_procesar)
        
        file_buttons_layout.addStretch(1)  # Espacio flexible
        
        # Contador de archivos
        self.lbl_archivos_seleccionados = QLabel('0 archivos')
        self.lbl_archivos_seleccionados.setStyleSheet("font-weight: bold; color: #2a82da;")
        file_buttons_layout.addWidget(self.lbl_archivos_seleccionados)
        
        file_layout.addLayout(file_buttons_layout)
        
        # Lista de archivos
        self.lista_archivos = QListWidget()
        self.lista_archivos.setMaximumHeight(120)
        self.lista_archivos.setToolTip("Archivos seleccionados para procesar")
        file_layout.addWidget(self.lista_archivos)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)

        # ========== GRUPO 2: PROGRESO Y ESTADO ==========
        progress_group = QGroupBox("Progreso")
        progress_layout = QVBoxLayout()
        
        # Etiqueta de estado - CORREGIDO: Manejo dinámico de colores
        self.lbl_estado = QLabel('Listo para procesar')
        self.actualizar_estilo_estado()  # Aplicar estilo según tema
        progress_layout.addWidget(self.lbl_estado)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(20)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        main_layout.addWidget(progress_group)

        # ========== GRUPO 3: RESULTADOS ==========
        results_group = QGroupBox("Resultados del Procesamiento")
        results_layout = QVBoxLayout()
        
        # Tabla de resumen
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
        
        # Información resumida - CORREGIDO: Manejo dinámico de colores
        self.lbl_info_adicional = QLabel('')
        self.actualizar_estilo_info_adicional()  # Aplicar estilo según tema
        results_layout.addWidget(self.lbl_info_adicional)
        
        # Botón de exportación
        export_layout = QHBoxLayout()
        export_layout.addStretch(1)
        
        self.btn_exportar = QPushButton('📤 Exportar Resultados')
        self.btn_exportar.clicked.connect(self.exportar_resultados)
        self.btn_exportar.setEnabled(False)
        self.btn_exportar.setToolTip("Exportar archivos procesados por campaña")
        export_layout.addWidget(self.btn_exportar)
        
        results_layout.addLayout(export_layout)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        # Espaciador final
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)

    
    def actualizar_estilo_estado(self):
        """Actualiza el estilo de la etiqueta de estado según el tema"""
        if self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        ):
            # Estilo para modo oscuro
            self.lbl_estado.setStyleSheet("""
                QLabel {
                    padding: 5px;
                    background-color: #1e3a5f;
                    border-radius: 3px;
                    color: white;
                }
            """)
        else:
            # Estilo para modo claro
            self.lbl_estado.setStyleSheet("""
                QLabel {
                    padding: 5px;
                    background-color: #e8f4fd;
                    border-radius: 3px;
                    color: #333333;
                }
            """)

    def actualizar_estilo_info_adicional(self):
        """Actualiza el estilo de la información adicional según el tema"""
        if self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        ):
            # Estilo para modo oscuro
            self.lbl_info_adicional.setStyleSheet("""
                QLabel {
                    background-color: #2d2d2d;
                    color: #ffffff;
                    padding: 8px;
                    border-radius: 3px;
                    border: 1px solid #555555;
                    font-weight: bold;
                    margin-top: 5px;
                }
            """)
        else:
            # Estilo para modo claro
            self.lbl_info_adicional.setStyleSheet("""
                QLabel {
                    background-color: #e9ecef;
                    color: #212529;
                    padding: 8px;
                    border-radius: 3px;
                    border: 1px solid #ced4da;
                    font-weight: bold;
                    margin-top: 5px;
                }
            """)

    def actualizar_estilo_tabla(self):
        """Actualiza el estilo de la tabla según el tema actual"""
        if self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        ):
            # Estilo para modo oscuro
            self.tabla_resumen.setStyleSheet("""
                QTableWidget {
                    background-color: #2d2d2d;
                    alternate-background-color: #3a3a3a;
                    gridline-color: #555555;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    color: #ffffff;
                }
                QTableWidget::item {
                    padding: 6px;
                    border: none;
                }
                QTableWidget::item:selected {
                    background-color: #2a82da;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #404040;
                    color: white;
                    padding: 8px;
                    border: 1px solid #555555;
                    font-weight: bold;
                }
            """)
        else:
            # Estilo para modo claro
            self.tabla_resumen.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    alternate-background-color: #f8f9fa;
                    gridline-color: #dee2e6;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    color: #212529;
                }
                QTableWidget::item {
                    padding: 6px;
                    border: none;
                }
                QTableWidget::item:selected {
                    background-color: #007bff;
                    color: white;
                }
                QHeaderView::section {
                    background-color: #343a40;
                    color: white;
                    padding: 8px;
                    border: 1px solid #454d55;
                    font-weight: bold;
                }
            """)

    def actualizar_todos_los_estilos(self):
        """Actualiza todos los estilos cuando cambia el tema"""
        self.actualizar_estilo_estado()
        self.actualizar_estilo_info_adicional()
        self.actualizar_estilo_tabla()

    def cargar_archivos(self):
        file_paths, _ = QFileDialog.getOpenFileNames(
            self, 
            'Seleccionar archivos CSV', 
            '', 
            'Archivos CSV (*.csv);;Todos los archivos (*)'
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
        self.lbl_estado.setText("Iniciando procesamiento...")

        self.thread = ProcessingThread(self.selected_files, self.db_connection)
        self.thread.update_progress.connect(self.progress_bar.setValue)
        self.thread.update_status.connect(self.lbl_estado.setText)
        self.thread.finished_processing.connect(self.mostrar_resultados)
        self.thread.error_occurred.connect(self.mostrar_error)
        self.thread.start()

    def mostrar_resultados(self, resultado):
        self.dataframes_procesados = resultado['dataframes']
        self.df_resumen = resultado['resumen']
        
        self.progress_bar.setVisible(False)
        self.btn_cargar.setEnabled(True)
        self.btn_procesar.setEnabled(True)
        self.btn_limpiar.setEnabled(True)
        self.btn_exportar.setEnabled(len(self.dataframes_procesados) > 0)

        if not self.df_resumen.empty:
            self.tabla_resumen.setRowCount(self.df_resumen.shape[0])
            self.tabla_resumen.setColumnCount(self.df_resumen.shape[1])
            self.tabla_resumen.setHorizontalHeaderLabels(self.df_resumen.columns.tolist())

            font_contenido = QFont()
            font_contenido.setPointSize(9)

            # Determinar colores según el tema
            if self.theme_manager.current_theme == "dark" or (
                self.theme_manager.current_theme == "system" and 
                self.theme_manager.is_system_dark()
            ):
                color_fila_par = QColor(45, 45, 45)
                color_fila_impar = QColor(58, 58, 58)
                color_texto = QColor(255, 255, 255)
            else:
                color_fila_par = QColor(255, 255, 255)
                color_fila_impar = QColor(248, 249, 250)
                color_texto = QColor(33, 37, 41)

            for row in range(self.df_resumen.shape[0]):
                for col in range(self.df_resumen.shape[1]):
                    value = str(self.df_resumen.iat[row, col])
                    item = QTableWidgetItem(value)
                    item.setFont(font_contenido)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(color_texto)
                    
                    if row % 2 == 0:
                        item.setBackground(color_fila_par)
                    else:
                        item.setBackground(color_fila_impar)
                    
                    self.tabla_resumen.setItem(row, col, item)

            self.tabla_resumen.resizeColumnsToContents()
            
            total_registros = self.df_resumen['Registros'].sum()
            total_campanas = len(self.dataframes_procesados)
            
            info_text = f"📊 RESUMEN EJECUTIVO | Campañas: {total_campanas} | Registros Totales: {total_registros:,}"
            self.lbl_info_adicional.setText(info_text)
            
            self.lbl_estado.setText(f"✅ Procesamiento completado - {total_campanas} campañas, {total_registros:,} registros")
        else:
            self.lbl_estado.setText("⚠️ Procesamiento completado pero no se encontraron datos válidos")
            self.lbl_info_adicional.setText("No se encontraron datos válidos para mostrar")

    def exportar_resultados(self):
        if not self.dataframes_procesados:
            QMessageBox.warning(self, "Advertencia", "No hay datos procesados para exportar")
            return

        carpeta_destino = QFileDialog.getExistingDirectory(
            self,
            'Seleccionar carpeta para guardar los archivos'
        )
        
        if not carpeta_destino:
            return

        try:
            archivos_exportados = []
            for campana, df in self.dataframes_procesados.items():
                df_exportar = self.preparar_dataframe_exportacion(df)
                nombre_archivo = self.crear_nombre_archivo_seguro(campana) + '.csv'
                ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
                
                df_exportar.to_csv(ruta_completa, index=False, encoding='utf-8', sep='|')
                archivos_exportados.append(nombre_archivo)
            
            mensaje = f"Se exportaron {len(archivos_exportados)} archivos:\n" + "\n".join(archivos_exportados)
            QMessageBox.information(self, '✅ Éxito', f'Archivos exportados correctamente en:\n{carpeta_destino}\n\n{mensaje}')
            self.lbl_estado.setText(f'📤 Exportados {len(archivos_exportados)} archivos')
            
        except Exception as e:
            QMessageBox.critical(self, '❌ Error', f'Error al exportar:\n{str(e)}')

    def preparar_dataframe_exportacion(self, df):
        columnas_requeridas = ['clienteid', 'numtelefono', 'mensaje']
        columnas_disponibles = {col.lower(): col for col in df.columns}
        columnas_exportar = []
        
        for col in columnas_requeridas:
            if col in columnas_disponibles:
                columnas_exportar.append(columnas_disponibles[col])
        
        return df[columnas_exportar] if columnas_exportar else pd.DataFrame()

    def crear_nombre_archivo_seguro(self, nombre):
        nombre_seguro = re.sub(r'[<>:"/\\|?*]', '_', str(nombre))
        return nombre_seguro[:100]

    def mostrar_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.btn_cargar.setEnabled(True)
        self.btn_procesar.setEnabled(True)
        self.btn_limpiar.setEnabled(True)
        QMessageBox.critical(self, '❌ Error', f'Error al procesar los archivos:\n{error_msg}')
        self.lbl_estado.setText('❌ Error en el procesamiento')
