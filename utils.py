import sys
import os
from PySide6.QtGui import QIcon

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
    ruta = "img/logo.ico"

    
    return QIcon(ruta_recurso(ruta))