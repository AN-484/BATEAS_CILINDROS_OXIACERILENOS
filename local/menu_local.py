from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel
)
from PySide6.QtCore import Qt

from utils import app_icon

ESTILO_BTN = """
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
"""

ESTILO_BTN_SEC = """
    QPushButton {
        background-color: #7F8C8D;
        color: white;
        font-size: 13px;
        padding: 8px;
        border-radius: 4px;
    }
    QPushButton:hover {
        background-color: #5F6A6A;
    }
"""


class MenuLocal(QWidget):
    """Menú de funciones que no requieren internet."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("MODO LOCAL")
        self.setWindowIcon(app_icon())
        self.setFixedSize(420, 360)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        layout.setContentsMargins(40, 40, 40, 40)

        titulo = QLabel("Funciones Locales")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: #1F3A5F;"
        )

        self.btn_sds = QPushButton("SDS")
        self.btn_sds.setStyleSheet(ESTILO_BTN)
        self.btn_sds.clicked.connect(self.abrir_sds)

        self.btn_volver = QPushButton("Volver")
        self.btn_volver.setStyleSheet(ESTILO_BTN_SEC)
        self.btn_volver.clicked.connect(self.volver)

        layout.addWidget(titulo)
        layout.addSpacing(10)
        layout.addWidget(self.btn_sds)
        layout.addStretch()
        layout.addWidget(self.btn_volver)

        self.setLayout(layout)

    def abrir_sds(self):
        from local.sds.editor import SDSEditor

        self.sds = SDSEditor(self)
        self.sds.showMaximized()
        self.hide()

    def volver(self):
        from ui.login import Login

        self.login = Login()
        self.login.show()
        self.close()
