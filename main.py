import sys
from PySide6.QtWidgets import QApplication
from ui.login import Login

def main():
    app = QApplication(sys.argv)

    login = Login()
    login.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()