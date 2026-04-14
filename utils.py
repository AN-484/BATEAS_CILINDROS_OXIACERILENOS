import sys
import os
from PySide6.QtGui import QIcon
from utils import ruta_recurso

def ruta_recurso(rel_path):
    """
    Devuelve la ruta correcta tanto en desarrollo
    como en el ejecutable (.exe)
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, rel_path)


def app_icon():
    """
    Icono global de la aplicación
    """
    ruta = ruta_recurso("img/logo.ico")

    self.setStyleSheet(f"""
        QWidget {{
            background-image: url({ruta});
            background-repeat: no-repeat;
            background-position: center;
        }}
    """)
    return QIcon(ruta_recurso(ruta))