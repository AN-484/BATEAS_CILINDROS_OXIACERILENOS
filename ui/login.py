from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMessageBox
from database import SessionLocal
from models import Usuario
from ui.main_window import MainWindow
from session import set_usuario


class Login(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login por DNI")

        layout = QVBoxLayout()

        # 🔥 DNI
        self.dni = QLineEdit()
        self.dni.setPlaceholderText("Ingrese DNI")

        btn = QPushButton("Ingresar")
        btn.clicked.connect(self.login)

        self.msg = QLabel("")

        layout.addWidget(self.dni)
        layout.addWidget(btn)
        layout.addWidget(self.msg)

        self.setLayout(layout)

    def login(self):

        dni_ingresado = self.dni.text().strip()

        if not dni_ingresado:

            QMessageBox.warning(
                self,
                "Error",
                "Ingrese DNI"
            )

            return

        db = SessionLocal()

        try:

            usuario = db.query(Usuario).filter_by(
                dni=dni_ingresado
            ).first()

            if usuario:

                # 🔥 guardar sesión
                set_usuario(usuario)

                self.main = MainWindow(usuario.nombre)
                self.main.show()

                self.close()

            else:

                self.msg.setText("❌ DNI no registrado")

        finally:

            db.close()