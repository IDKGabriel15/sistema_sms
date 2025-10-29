# Contenido completo y corregido para: src/ui/tabs/DevolucionesTab.py

from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                               QTableWidgetItem, QFileDialog, QMessageBox, QLabel, 
                               QProgressBar, QListWidget, QHeaderView, QAbstractItemView, 
                               QGroupBox, QSizePolicy)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QColor, QGuiApplication, QPixmap
import os
import re
import pandas as pd

from ..components.base_tab import BaseTab
from src.models.processing import ProcessingThread
from src.utils.file_handlers import crear_nombre_archivo_seguro, preparar_dataframe_exportacion

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
        results_group = QGroupBox("Resultados del Procesamiento")
        results_layout = QVBoxLayout()
        
        # --- INICIO DE CORRECCIÓN ---
        self.tabla_resumen = QTableWidget()
        
        # Política de tamaño:
        # Horizontal: Su tamaño debe ser el de su contenido (Preferred)
        # Vertical: Debe expandirse para llenar el GroupBox (Expanding)
        self.tabla_resumen.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        self.actualizar_estilo_tabla()
        self.tabla_resumen.setAlternatingRowColors(True)
        self.tabla_resumen.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabla_resumen.setSelectionMode(QAbstractItemView.SingleSelection)
        self.tabla_resumen.setSortingEnabled(True)
        # Eliminamos la altura mínima para que sea flexible
        
        header = self.tabla_resumen.horizontalHeader()
        
        # Comportamiento por defecto: TODAS las columnas se ajustan al contenido.
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        # No queremos que la última sección se estire por sí sola
        header.setStretchLastSection(False)
        # --- FIN DE CORRECCIÓN ---
        
        results_layout.addWidget(self.tabla_resumen)
        
        self.lbl_info_adicional = QLabel('')
        self.actualizar_estilo_info_adicional()
        results_layout.addWidget(self.lbl_info_adicional)
        
        # Botones de resultados
        results_buttons_layout = QHBoxLayout()
        results_buttons_layout.addStretch(1)
        
        self.btn_copiar_tabla = QPushButton('📸 Copiar Imagen')
        self.btn_copiar_tabla.clicked.connect(self.copiar_tabla)
        self.btn_copiar_tabla.setEnabled(False)
        self.btn_copiar_tabla.setToolTip("Copiar una imagen de la tabla al portapapeles")
        results_buttons_layout.addWidget(self.btn_copiar_tabla)
        
        self.btn_exportar = QPushButton('📤 Exportar Resultados')
        self.btn_exportar.clicked.connect(self.exportar_resultados)
        self.btn_exportar.setEnabled(False)
        self.btn_exportar.setToolTip("Exportar archivos procesados por campaña")
        results_buttons_layout.addWidget(self.btn_exportar)
        
        results_layout.addLayout(results_buttons_layout)
        results_group.setLayout(results_layout)
        main_layout.addWidget(results_group)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

    
    def actualizar_estilo_estado(self):
        """Actualiza el estilo de la etiqueta de estado según el tema"""
        if self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        ):
            self.lbl_estado.setStyleSheet("QLabel { padding: 5px; background-color: #1e3a5f; border-radius: 3px; color: white; }")
        else:
            self.lbl_estado.setStyleSheet("QLabel { padding: 5px; background-color: #e8f4fd; border-radius: 3px; color: #333333; }")

    def actualizar_estilo_info_adicional(self):
        """Actualiza el estilo de la información adicional según el tema"""
        if self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        ):
            self.lbl_info_adicional.setStyleSheet("QLabel { background-color: #2d2d2d; color: #ffffff; padding: 8px; border-radius: 3px; border: 1px solid #555555; font-weight: bold; margin-top: 5px; }")
        else:
            self.lbl_info_adicional.setStyleSheet("QLabel { background-color: #e9ecef; color: #212529; padding: 8px; border-radius: 3px; border: 1px solid #ced4da; font-weight: bold; margin-top: 5px; }")

    def actualizar_estilo_tabla(self):
        """Actualiza el estilo de la tabla según el tema actual"""
        # (El código de estilo que tenías estaba bien, no se toca)
        if self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        ):
            self.tabla_resumen.setStyleSheet("""
                QTableWidget {
                    background-color: #2d2d2d;
                    alternate-background-color: #3a3a3a;
                    gridline-color: #555555;
                    border: 1px solid #555555;
                    border-radius: 4px;
                    color: #ffffff;
                }
                QTableWidget::item { padding: 6px; border: none; }
                QTableWidget::item:selected { background-color: #2a82da; color: white; }
                QHeaderView::section {
                    background-color: #404040; color: white; padding: 8px;
                    border: 1px solid #555555; font-weight: bold;
                }
            """)
        else:
            self.tabla_resumen.setStyleSheet("""
                QTableWidget {
                    background-color: white;
                    alternate-background-color: #f8f9fa;
                    gridline-color: #dee2e6;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    color: #212529;
                }
                QTableWidget::item { padding: 6px; border: none; }
                QTableWidget::item:selected { background-color: #007bff; color: white; }
                QHeaderView::section {
                    background-color: #343a40; color: white; padding: 8px;
                    border: 1px solid #454d55; font-weight: bold;
                }
            """)

    def update_styles(self):
        """Actualiza todos los estilos cuando cambia el tema"""
        self.actualizar_estilo_estado()
        self.actualizar_estilo_info_adicional()
        self.actualizar_estilo_tabla()
        # Si hay datos, volvemos a pintar la tabla para refrescar colores
        if self.df_resumen is not None and not self.df_resumen.empty:
            self.mostrar_resultados({
                'dataframes': self.dataframes_procesados,
                'resumen': self.df_resumen
            })


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
        self.btn_exportar.setEnabled(False) 
        self.btn_copiar_tabla.setEnabled(False)
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
        self.btn_copiar_tabla.setEnabled(not self.df_resumen.empty) 

        if not self.df_resumen.empty:
            self.tabla_resumen.setRowCount(self.df_resumen.shape[0])
            self.tabla_resumen.setColumnCount(self.df_resumen.shape[1])
            self.tabla_resumen.setHorizontalHeaderLabels(self.df_resumen.columns.tolist())

            font_contenido = QFont()
            font_contenido.setPointSize(9)

            is_dark = self.theme_manager.current_theme == "dark" or (
                self.theme_manager.current_theme == "system" and 
                self.theme_manager.is_system_dark()
            )
            color_texto = QColor(255, 255, 255) if is_dark else QColor(33, 37, 41)

            for row in range(self.df_resumen.shape[0]):
                bg_color = QColor(45, 45, 45) if is_dark and row % 2 == 0 else \
                           QColor(58, 58, 58) if is_dark else \
                           QColor(255, 255, 255) if not is_dark and row % 2 == 0 else \
                           QColor(248, 249, 250)

                for col in range(self.df_resumen.shape[1]):
                    value = str(self.df_resumen.iat[row, col])
                    item = QTableWidgetItem(value)
                    item.setFont(font_contenido)
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setForeground(color_texto)
                    item.setBackground(bg_color)
                    self.tabla_resumen.setItem(row, col, item)

            # --- INICIO DE CORRECCIÓN ---
            # 1. Forzamos a TODAS las columnas a re-ajustarse a su contenido.
            #    Esto hará que la tabla sea compacta y sin scroll horizontal.
            self.tabla_resumen.resizeColumnsToContents()
            # --- FIN DE CORRECCIÓN ---
            
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
        carpeta_destino = QFileDialog.getExistingDirectory(self, 'Seleccionar carpeta para guardar los archivos')
        if not carpeta_destino:
            return
        try:
            archivos_exportados = []
            for campana, df in self.dataframes_procesados.items():
                df_exportar = preparar_dataframe_exportacion(df)
                nombre_archivo = crear_nombre_archivo_seguro(campana) + '.csv'
                ruta_completa = os.path.join(carpeta_destino, nombre_archivo)
                df_exportar.to_csv(ruta_completa, index=False, encoding='utf-8', sep='|')
                archivos_exportados.append(nombre_archivo)
            
            mensaje = f"Se exportaron {len(archivos_exportados)} archivos:\n" + "\n".join(archivos_exportados)
            QMessageBox.information(self, '✅ Éxito', f'Archivos exportados correctamente en:\n{carpeta_destino}\n\n{mensaje}')
            self.lbl_estado.setText(f'📤 Exportados {len(archivos_exportados)} archivos')
        except Exception as e:
            QMessageBox.critical(self, '❌ Error', f'Error al exportar:\n{str(e)}')

    def mostrar_error(self, error_msg):
        self.progress_bar.setVisible(False)
        self.btn_cargar.setEnabled(True)
        self.btn_procesar.setEnabled(True)
        self.btn_limpiar.setEnabled(True)
        QMessageBox.critical(self, '❌ Error', f'Error al procesar los archivos:\n{error_msg}')
        self.lbl_estado.setText('❌ Error en el procesamiento')

    def copiar_tabla(self):
        """
        Copia una captura de pantalla (PNG) compacta y auto-ajustada
        de la tabla actual al portapapeles.
        """
        # (Este método ya estaba correcto y no se toca)
        if self.tabla_resumen.rowCount() == 0:
            QMessageBox.warning(self, "Sin datos", "No hay tabla para copiar.")
            return

        header = self.tabla_resumen.horizontalHeader()
        original_resize_modes = [header.sectionResizeMode(col) for col in range(header.count())]
        vh_visible = self.tabla_resumen.verticalHeader().isVisible()
        original_size = self.tabla_resumen.size()

        try:
            self.tabla_resumen.verticalHeader().setVisible(False)
            for col in range(header.count()):
                header.setSectionResizeMode(col, QHeaderView.ResizeToContents)

            ideal_width = header.length()
            ideal_height = header.height()
            for row in range(self.tabla_resumen.rowCount()):
                ideal_height += self.tabla_resumen.rowHeight(row)
            
            self.tabla_resumen.resize(ideal_width + 2, ideal_height + 2)
            pixmap = self.tabla_resumen.grab()
            
            clipboard = QGuiApplication.clipboard()
            clipboard.setPixmap(pixmap)
            self.lbl_estado.setText("✅ ¡Imagen de la tabla copiada al portapapeles!")

        except Exception as e:
            QMessageBox.critical(self, "Error al copiar", f"No se pudo copiar la imagen de la tabla: {str(e)}")
            self.lbl_estado.setText("❌ Error al copiar imagen")
        
        finally:
            for col, mode in enumerate(original_resize_modes):
                header.setSectionResizeMode(col, mode)
            self.tabla_resumen.verticalHeader().setVisible(vh_visible)
            self.tabla_resumen.resize(original_size)