from PySide6.QtWidgets import *

def verificar_entrada_de_cilindro(movimiento, estado_actual, parent):
    if movimiento == "ENTRADA":
        if estado_actual and estado_actual.estado != "EN PROVEEDOR":
            QMessageBox.warning(
                parent,
                "Error",
                f"❌ No se puede ingresar el cilindro.\nEstado actual: {estado_actual.estado}\n\nSolo se permite si está en EN PROVEEDOR."
            )
            return False
    return True


def verificar_salida_de_cilindro(movimiento, estado_actual, parent):
    if movimiento == "SALIDA":
        if not estado_actual or estado_actual.estado != "VACIO":
            estado_msg = "No registrado" if not estado_actual else estado_actual.estado
            QMessageBox.warning(
                parent,
                "Error",
                f"❌ No se puede dar salida.\nEstado actual: {estado_msg}\n\nSolo se permite si está en VACIO."
            )
            return False
    return True