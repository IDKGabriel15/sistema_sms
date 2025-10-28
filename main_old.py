import sys
import pandas as pd
import psycopg2
import os
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, 
                               QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, 
                               QFileDialog, QMessageBox, QLabel, QProgressBar, QListWidget,
                               QHeaderView, QAbstractItemView, QGroupBox, QFrame, QSizePolicy)
from PySide6.QtCore import QThread, Signal, Qt, QSettings
from PySide6.QtGui import QAction, QFont, QColor, QPalette, QIcon

class DatabaseConnection:
    """Clase para manejar conexión a PostgreSQL"""
    def __init__(self):
        self.connection = None
    
    def connect(self, host, port, database, user, password):
        try:
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False

class ThemeManager:
    """Gestor de temas para la aplicación"""
    def __init__(self):
        self.settings = QSettings("MiEmpresa", "SistemaDevoluciones")
        self.current_theme = self.settings.value("theme", "system")
    
    def apply_theme(self, app, theme=None):
        if theme:
            self.current_theme = theme
            self.settings.setValue("theme", theme)
        else:
            theme = self.current_theme
        
        if theme == "dark" or (theme == "system" and self.is_system_dark()):
            self.apply_dark_theme(app)
        else:
            self.apply_light_theme(app)
    
    def is_system_dark(self):
        palette = QApplication.palette()
        return palette.window().color().lightness() < 128
    
    def apply_dark_theme(self, app):
        app.setStyle("Fusion")
        dark_palette = QPalette()
        
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)
        
        app.setPalette(dark_palette)
        
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #353535;
                color: white;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #404040;
            }
            QTabBar::tab {
                background-color: #505050;
                color: white;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2a82da;
            }
            QPushButton {
                background-color: #505050;
                color: white;
                border: 1px solid #666666;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #606060;
            }
            QPushButton:pressed {
                background-color: #2a82da;
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #808080;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555555;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QListWidget {
                border: 1px solid #666666;
                border-radius: 4px;
                background-color: #2d2d2d;
            }
            QProgressBar {
                border: 1px solid #666666;
                border-radius: 4px;
                text-align: center;
                background-color: #2d2d2d;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
                border-radius: 3px;
            }
        """)
    
    def apply_light_theme(self, app):
        app.setStyle("Fusion")
        app.setPalette(QApplication.style().standardPalette())
        app.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #f5f5f5;
                color: #333333;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e8e8e8;
                color: #333333;
                padding: 8px 16px;
                margin: 2px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: #2a82da;
                color: white;
            }
            QPushButton {
                background-color: #e8e8e8;
                color: #333333;
                border: 1px solid #c0c0c0;
                padding: 8px 12px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #d8d8d8;
            }
            QPushButton:pressed {
                background-color: #2a82da;
                color: white;
            }
            QPushButton:disabled {
                background-color: #f0f0f0;
                color: #a0a0a0;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #c0c0c0;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QListWidget {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                background-color: white;
            }
            QProgressBar {
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                text-align: center;
                background-color: white;
            }
            QProgressBar::chunk {
                background-color: #2a82da;
                border-radius: 3px;
            }
        """)

class ProcessingThread(QThread):
    """Hilo para procesamiento pesado de múltiples archivos"""
    update_progress = Signal(int)
    update_status = Signal(str)
    finished_processing = Signal(dict)
    error_occurred = Signal(str)

    def __init__(self, file_paths, db_connection):
        super().__init__()
        self.file_paths = file_paths
        self.db_connection = db_connection
        self.caracteres_permitidos = ' É_!"#\'¤%&()*+-./<=>?$@0ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;\''
        self.columnas_requeridas = [
            'clienteid', 'nombre', 'apellidopaterno', 'apellidomaterno', 'numtelefono', 
            'mensaje', 'variable1', 'variable2', 'variable3', 'variable4', 'variable5', 
            'fechainsercion', 'fechaaenviar', 'horaaenviar', 'campana'
        ]

    def run(self):
        try:
            all_dataframes = {}
            tabla_resumen_data = []
            total_files = len(self.file_paths)
            
            for i, file_path in enumerate(self.file_paths):
                self.update_status.emit(f"Procesando archivo {i+1}/{total_files}: {os.path.basename(file_path)}")
                progress = int((i / total_files) * 80)
                self.update_progress.emit(progress)
                
                # Detectar separador y leer archivo
                df = self.detectar_y_leer_archivo(file_path)
                if df is None:
                    continue
                
                # Validar estructura del archivo
                if not self.validar_estructura_archivo(df):
                    self.error_occurred.emit(f"El archivo {os.path.basename(file_path)} no tiene la estructura requerida")
                    return
                
                # Validar mensajes
                mensajes_invalidos = self.validar_mensajes(df)
                if mensajes_invalidos:
                    self.error_occurred.emit(f"Caracteres no permitidos encontrados en el archivo {os.path.basename(file_path)}:\n{mensajes_invalidos}")
                    return
                
                # Procesar por campaña
                campanas = df['campana'].unique()
                for campana in campanas:
                    df_campana = df[df['campana'] == campana].copy()
                    
                    # Guardar en el diccionario
                    if campana not in all_dataframes:
                        all_dataframes[campana] = []
                    all_dataframes[campana].append(df_campana)
                    
                    # Agregar a tabla resumen
                    tabla_resumen_data.append({
                        'Campaña': campana,
                        'Registros': len(df_campana)
                    })
            
            # Consolidar DataFrames por campaña
            dataframes_consolidados = {}
            for campana, dfs in all_dataframes.items():
                if dfs:
                    dataframes_consolidados[campana] = pd.concat(dfs, ignore_index=True)
            
            self.update_progress.emit(100)
            self.update_status.emit("Procesamiento completado")
            
            # Crear DataFrame de resumen
            df_resumen = pd.DataFrame(tabla_resumen_data)
            if not df_resumen.empty:
                df_resumen = df_resumen.groupby('Campaña').sum().reset_index()
            
            resultado = {
                'dataframes': dataframes_consolidados,
                'resumen': df_resumen
            }
            self.finished_processing.emit(resultado)
                
        except Exception as e:
            self.error_occurred.emit(str(e))

    def detectar_y_leer_archivo(self, file_path):
        """Detecta el separador del archivo y lo lee"""
        try:
            # Leer primeras líneas para detectar separador
            with open(file_path, 'r', encoding='utf-8') as f:
                primeras_lineas = [f.readline() for _ in range(5)]
            
            # Contar pipes y comas
            conteo_pipes = sum(line.count('|') for line in primeras_lineas)
            conteo_comas = sum(line.count(',') for line in primeras_lineas)
            
            # Determinar separador
            separador = '|' if conteo_pipes > conteo_comas else ','
            
            # Leer archivo con el separador detectado
            df = pd.read_csv(file_path, sep=separador, encoding='utf-8')
            
            # Limpiar nombres de columnas (eliminar espacios extras)
            df.columns = df.columns.str.strip()
            
            return df
            
        except Exception as e:
            self.error_occurred.emit(f"Error al leer archivo {os.path.basename(file_path)}: {str(e)}")
            return None

    def validar_estructura_archivo(self, df):
        """Valida que el archivo tenga las columnas requeridas"""
        columnas_archivo = set(df.columns.str.strip().str.lower())
        columnas_requeridas = set(col.lower() for col in self.columnas_requeridas)
        
        return columnas_requeridas.issubset(columnas_archivo)

    def validar_mensajes(self, df):
        """Valida que los mensajes solo contengan caracteres permitidos"""
        mensajes_invalidos = []
        
        for idx, mensaje in df['mensaje'].items():
            if pd.notna(mensaje):
                mensaje_str = str(mensaje)
                for char in mensaje_str:
                    if char not in self.caracteres_permitidos:
                        mensajes_invalidos.append(f"Fila {idx+2}: '{mensaje_str}' - Carácter no permitido: '{char}'")
                        if len(mensajes_invalidos) >= 10:  # Limitar a 10 errores
                            mensajes_invalidos.append("... (más errores encontrados)")
                            return "\n".join(mensajes_invalidos)
        
        return "\n".join(mensajes_invalidos) if mensajes_invalidos else ""

class DevolucionesTab(QWidget):
    def __init__(self, db_connection, theme_manager):
        super().__init__()
        self.db_connection = db_connection
        self.theme_manager = theme_manager
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

# Las clases Reporte1Tab, Reporte2Tab, Reporte3Tab se mantienen igual...
class Reporte1Tab(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Reporte 1 - Análisis de Devoluciones"))
        
        self.btn_generar_reporte1 = QPushButton('Generar Reporte 1')
        self.btn_generar_reporte1.clicked.connect(self.generar_reporte1)
        layout.addWidget(self.btn_generar_reporte1)
        
        self.tabla_reporte1 = QTableWidget()
        layout.addWidget(self.tabla_reporte1)
        
        self.setLayout(layout)
    
    def generar_reporte1(self):
        QMessageBox.information(self, "Reporte 1", "Generando reporte tipo 1...")

class Reporte2Tab(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Reporte 2 - Estadísticas por Producto"))
        
        self.btn_generar_reporte2 = QPushButton('Generar Reporte 2')
        self.btn_generar_reporte2.clicked.connect(self.generar_reporte2)
        layout.addWidget(self.btn_generar_reporte2)
        
        self.tabla_reporte2 = QTableWidget()
        layout.addWidget(self.tabla_reporte2)
        
        self.setLayout(layout)
    
    def generar_reporte2(self):
        QMessageBox.information(self, "Reporte 2", "Generando reporte tipo 2...")

class Reporte3Tab(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Reporte 3 - Resumen Mensual"))
        
        self.btn_generar_reporte3 = QPushButton('Generar Reporte 3')
        self.btn_generar_reporte3.clicked.connect(self.generar_reporte3)
        layout.addWidget(self.btn_generar_reporte3)
        
        self.tabla_reporte3 = QTableWidget()
        layout.addWidget(self.tabla_reporte3)
        
        self.setLayout(layout)
    
    def generar_reporte3(self):
        QMessageBox.information(self, "Reporte 3", "Generando reporte tipo 3...")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseConnection()
        self.theme_manager = ThemeManager()
        self.init_ui()
        self.conectar_base_datos()

    def init_ui(self):
        self.setWindowTitle('📊 Sistema de Devoluciones y Reportes')
        self.setGeometry(100, 100, 1400, 900)

        # Widget central con pestañas
        tab_widget = QTabWidget()

        # Pestaña de devoluciones
        self.devoluciones_tab = DevolucionesTab(self.db, self.theme_manager)
        tab_widget.addTab(self.devoluciones_tab, "📁 Generar Devoluciones")

        # Pestañas de reportes específicos
        self.reporte1_tab = Reporte1Tab(self.db)
        self.reporte2_tab = Reporte2Tab(self.db)
        self.reporte3_tab = Reporte3Tab(self.db)
        
        tab_widget.addTab(self.reporte1_tab, "📈 Reporte 1")
        tab_widget.addTab(self.reporte2_tab, "📊 Reporte 2")
        tab_widget.addTab(self.reporte3_tab, "📋 Reporte 3")

        self.setCentralWidget(tab_widget)

        # Barra de menú
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
        """Cambia el tema de la aplicación y actualiza todos los estilos"""
        self.theme_manager.apply_theme(QApplication.instance(), tema)
        # Actualizar todos los estilos en la pestaña de devoluciones
        self.devoluciones_tab.actualizar_todos_los_estilos()
        # Si hay datos mostrados, volver a renderizar la tabla para actualizar colores
        if self.devoluciones_tab.df_resumen is not None:
            self.devoluciones_tab.mostrar_resultados({
                'dataframes': self.devoluciones_tab.dataframes_procesados,
                'resumen': self.devoluciones_tab.df_resumen
            })

    def conectar_base_datos(self):
        conexion_exitosa = self.db.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="Roman_3119"
        )
        
        if not conexion_exitosa:
            QMessageBox.warning(
                self, 
                "⚠️ Conexión Fallida", 
                "No se pudo conectar a la base de datos. La aplicación funcionará sin conexión a BD."
            )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    theme_manager = ThemeManager()
    theme_manager.apply_theme(app)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())