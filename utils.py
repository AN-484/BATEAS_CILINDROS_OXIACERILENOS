import sys
import os

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