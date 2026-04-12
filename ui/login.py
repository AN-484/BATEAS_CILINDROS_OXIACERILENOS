from PySide6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel
from database import SessionLocal
from models import Acceso
from ui.main_window import MainWindow

class Login(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")

        layout = QVBoxLayout()

        self.user = QLineEdit()
        self.user.setPlaceholderText("Usuario")

        self.passw = QLineEdit()
        self.passw.setPlaceholderText("Password")
        self.passw.setEchoMode(QLineEdit.Password)

        btn = QPushButton("Ingresar")
        btn.clicked.connect(self.login)

        self.msg = QLabel("")

        layout.addWidget(self.user)
        layout.addWidget(self.passw)
        layout.addWidget(btn)
        layout.addWidget(self.msg)

        self.setLayout(layout)

    def login(self):
        db = SessionLocal()

        u = db.query(Acceso).filter_by(
            usuario=self.user.text(),
            password=self.passw.text()
        ).first()

        db.close()

        if u:
            self.main = MainWindow(self.user.text())
            self.main.show()
            self.close()
        else:
            self.msg.setText("❌ Usuario incorrecto")