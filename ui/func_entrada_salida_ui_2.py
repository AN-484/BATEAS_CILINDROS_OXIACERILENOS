from PySide6.QtWidgets import QMessageBox


def _obtener_estado(estado_actual):
    if not estado_actual:
        return None

    if isinstance(estado_actual, dict):
        return estado_actual.get("estado")

    return getattr(estado_actual, "estado", None)


def verificar_entrada_de_cilindro(movimiento, estado_actual, parent):
    estado = _obtener_estado(estado_actual)

    if movimiento == "INGRESO":
        if estado_actual and estado != "EN PROVEEDOR":
            QMessageBox.warning(
                parent,
                "Error",
                f"❌ No se puede ingresar el cilindro.\nEstado actual: {estado}\n\nSolo se permite si está en EN PROVEEDOR."
            )
            return False

    return True


def verificar_salida_de_cilindro(movimiento, estado_actual, parent):
    estado = _obtener_estado(estado_actual)

    if movimiento == "RECARGA":
        if not estado_actual or estado != "VACIO":
            estado_msg = "No registrado" if not estado_actual else estado
            QMessageBox.warning(
                parent,
                "Error",
                f"❌ No se puede dar salida.\nEstado actual: {estado_msg}\n\nSolo se permite si está en VACIO."
            )
            return False

    return True