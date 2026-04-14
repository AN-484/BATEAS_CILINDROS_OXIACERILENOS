import sys
from PySide6.QtWidgets import QApplication
from ui.login import Login
from utils import app_icon

def main():
    app = QApplication(sys.argv)

    # ⭐ ICONO GLOBAL DE TODA LA APLICACIÓN
    app.setWindowIcon(app_icon())

    login = Login()
    login.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()