from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QLabel,
    QMessageBox
)

from PySide6.QtGui import (
    QPixmap,
    QIntValidator
)
from utils import ruta_recurso


from PySide6.QtCore import Qt

from database import SessionLocal
from models import Usuario
from ui.main_window import MainWindow
from session import set_usuario


class Login(QWidget):

    def __init__(self):
        super().__init__()

        # ===== CONFIGURACION DE VENTANA =====

        self.setWindowTitle("INGRESAR")

        # tamaño fijo profesional
        self.setFixedSize(420, 520)

        # ===== LAYOUT =====

        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignCenter)

        layout.setSpacing(15)

        layout.setContentsMargins(
            40,
            40,
            40,
            40
        )

        # ===== IMAGEN / LOGO =====

        self.logo = QLabel()

        ruta = ruta_recurso("img/login2.png")

        self.setStyleSheet(f"""
            QWidget {{
                background-image: url({ruta});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        pixmap = QPixmap(ruta)

        self.logo.setPixmap(pixmap)

        self.logo.setScaledContents(True)

        self.logo.setFixedHeight(180)

        self.logo.setAlignment(Qt.AlignCenter)

        # ===== TITULO =====

        self.titulo = QLabel(
            "Sistema de Control de Cilindros"
        )
        self.titulo2 = QLabel(
            "Ingrese su DNI:"
        )

        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo2.setAlignment(Qt.AlignCenter)

        self.titulo.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1F3A5F;
            }
        """)

        # ===== CAMPO DNI =====

        self.dni = QLineEdit()
        # solo 8 caracteres
        

        self.dni.setPlaceholderText("DNI")
        self.dni.setMaxLength(8)

        

        # solo números
        self.dni.setValidator(
            QIntValidator(0, 99999999)
        )

        # centrado
        self.dni.setAlignment(
            Qt.AlignCenter
        )

        self.dni.setStyleSheet("""
            QLineEdit {
                font-size: 18px;
                padding: 8px;
                border: 2px solid #2E75B6;
                border-radius: 4px;
            }
        """)

        # ===== BOTON INGRESAR =====

        self.btn = QPushButton(
            "Ingresar"
        )

        self.btn.setStyleSheet("""
            QPushButton {
                background-color: #2E75B6;
                color: white;
                font-size: 14px;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }

            QPushButton:hover {
                background-color: #1F5A8A;
            }
        """)

        # ENTER ejecuta login
        self.btn.clicked.connect(
            self.login
        )

        self.dni.returnPressed.connect(
            self.login
        )

        # ===== MENSAJE =====

        self.msg = QLabel("")

        self.msg.setAlignment(
            Qt.AlignCenter
        )

        self.msg.setStyleSheet("""
            QLabel {
                color: red;
                font-size: 12px;
            }
        """)

        # ===== AGREGAR AL LAYOUT =====

        layout.addWidget(self.logo)

        layout.addSpacing(10)

        layout.addWidget(self.titulo)
        layout.addSpacing(15)
        layout.addWidget(self.titulo2)

        layout.addSpacing(1)

        layout.addWidget(self.dni)

        layout.addWidget(self.btn)

        layout.addWidget(self.msg)

        self.setLayout(layout)

        # foco directo al DNI
        self.dni.setFocus()

    # ===== LOGIN =====

    def login(self):

        dni_ingresado = self.dni.text().strip()

        # validar longitud exacta
        if len(dni_ingresado) != 8:

            QMessageBox.warning(
                self,
                "Error",
                "El DNI debe tener 8 dígitos"
            )

            return

        db = SessionLocal()

        try:

            usuario = db.query(
                Usuario
            ).filter_by(
                dni=dni_ingresado
            ).first()

            if usuario:

                # guardar sesión
                set_usuario(usuario)

                # abrir sistema
                self.main = MainWindow(
                    usuario.nombre
                )

                self.main.show()

                self.close()

            else:

                self.msg.setText(
                    "❌ DNI no registrado"
                )

        finally:

            db.close()