# Contenido para: src/ui/login_dialog.py

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QPushButton, QMessageBox, QSpacerItem, 
                               QSizePolicy)
from PySide6.QtCore import Qt
import bcrypt 

class LoginDialog(QDialog):
    def __init__(self, db_connection, theme_manager, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.theme_manager = theme_manager
        self.setWindowTitle("Iniciar Sesión - Sistema Devoluciones")
        self.setModal(True) # Bloquea la ventana principal hasta que se cierre
        self.setMinimumWidth(350)
        
        self.init_ui()
        self.apply_styles() # Para consistencia con el tema

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # Título
        title_label = QLabel("Bienvenido")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("loginTitleLabel") # Para aplicar estilo
        layout.addWidget(title_label)
        
        # Usuario
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre de Usuario")
        layout.addWidget(QLabel("Usuario:"))
        layout.addWidget(self.username_input)

        # Contraseña
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password) # Ocultar contraseña
        layout.addWidget(QLabel("Contraseña:"))
        layout.addWidget(self.password_input)
        
        # Espaciador
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Botones
        button_layout = QHBoxLayout()
        button_layout.addStretch(1) # Empuja los botones a la derecha

        self.login_button = QPushButton("Ingresar")
        self.login_button.setDefault(True) # Permite presionar Enter para ingresar
        self.login_button.clicked.connect(self.attempt_login)
        button_layout.addWidget(self.login_button)

        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.clicked.connect(self.reject) # reject() cierra el diálogo con resultado Cancel
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        # Conectar Enter en campo de contraseña al botón de login
        self.password_input.returnPressed.connect(self.login_button.click)
        self.username_input.returnPressed.connect(self.password_input.setFocus) # Enter en usuario va a contraseña

    # En: src/ui/login_dialog.py (Reemplaza el método apply_styles existente)

    def apply_styles(self):
        """Aplica estilos según el tema actual gestionado por ThemeManager."""

        # Determinar si el tema actual es oscuro
        is_dark = self.theme_manager.current_theme == "dark" or (
            self.theme_manager.current_theme == "system" and 
            self.theme_manager.is_system_dark()
        )

        if is_dark:
            # --- ESTILOS PARA TEMA OSCURO ---
            self.setStyleSheet("""
                QDialog {
                    background-color: #353535; /* Fondo oscuro */
                    color: white; /* Texto blanco */
                }
                QLabel { /* Estilo general para etiquetas */
                    color: white; 
                }
                QLabel#loginTitleLabel {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: #e0e0e0; /* Un blanco un poco menos brillante */
                }
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #555555; /* Borde gris oscuro */
                    border-radius: 4px;
                    background-color: #2d2d2d; /* Fondo de input oscuro */
                    color: white; /* Texto de input blanco */
                }
                QPushButton {
                    padding: 8px 15px;
                    border: 1px solid #666666; /* Borde gris medio */
                    border-radius: 4px;
                    background-color: #505050; /* Botón gris oscuro */
                    color: white;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #606060; /* Un poco más claro al pasar el ratón */
                }
                QPushButton:pressed {
                    background-color: #2a82da; /* Azul al presionar */
                }
                QPushButton:default { /* Botón "Ingresar" */
                    background-color: #2a82da; /* Azul por defecto */
                    border-color: #2a82da;
                    color: white;
                }
                QPushButton:default:hover {
                    background-color: #3a93ea; /* Azul más claro al pasar el ratón */
                }
            """)
        else:
            # --- ESTILOS PARA TEMA CLARO ---
            self.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5; /* Fondo claro */
                    color: #333333; /* Texto oscuro */
                }
                QLabel { 
                    color: #333333; 
                }
                QLabel#loginTitleLabel {
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 10px;
                    color: #111111; /* Negro */
                }
                QLineEdit {
                    padding: 8px;
                    border: 1px solid #c0c0c0; /* Borde gris claro */
                    border-radius: 4px;
                    background-color: white; /* Fondo blanco */
                    color: #333333; /* Texto oscuro */
                }
                QPushButton {
                    padding: 8px 15px;
                    border: 1px solid #c0c0c0; /* Borde gris claro */
                    border-radius: 4px;
                    background-color: #e8e8e8; /* Botón gris claro */
                    color: #333333;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #d8d8d8; /* Más oscuro al pasar el ratón */
                }
                QPushButton:pressed {
                    background-color: #2a82da; /* Azul al presionar */
                    color: white;
                }
                QPushButton:default { /* Botón "Ingresar" */
                    background-color: #2a82da; /* Azul por defecto */
                    border-color: #2a82da;
                    color: white;
                }
                QPushButton:default:hover {
                    background-color: #3a93ea; /* Azul más claro al pasar el ratón */
                }
            """)
    
    def attempt_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text() # No quitar espacios de la contraseña

        if not username or not password:
            QMessageBox.warning(self, "Campos Vacíos", "Por favor, ingresa usuario y contraseña.")
            return

        # Buscar hash en la base de datos
        stored_hash = self.db_connection.get_user_hash(username)

        if stored_hash:
            # Convertir a bytes para bcrypt
            stored_hash_bytes = stored_hash.encode('utf-8')
            password_bytes = password.encode('utf-8')
            
            # Verificar contraseña
            if bcrypt.checkpw(password_bytes, stored_hash_bytes):
                self.accept() # ¡Login exitoso! Cierra el diálogo con resultado OK
            else:
                QMessageBox.warning(self, "Error de Acceso", "Nombre de usuario o contraseña incorrectos.")
                self.password_input.clear() # Limpiar contraseña
        else:
            QMessageBox.warning(self, "Error de Acceso", "Nombre de usuario o contraseña incorrectos.")
            self.password_input.clear() # Limpiar contraseña