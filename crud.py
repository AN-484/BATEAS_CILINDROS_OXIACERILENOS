from datetime import datetime

from supabase_api import (
    obtener_estado_cilindro_por_codigo,
    obtener_cilindro_por_codigo,
    crear_estado_cilindro,
    actualizar_estado_cilindro_api,
    actualizar_cilindro_api
)


def obtener_estado_actual(db, cilindro):
    # db se mantiene solo por compatibilidad
    return obtener_estado_cilindro_por_codigo(cilindro)


def obtener_cilindro_actual(db, cilindro):
    # db se mantiene solo por compatibilidad
    return obtener_cilindro_por_codigo(cilindro)


def actualizar_estado(db, cilindro, nuevo_estado, ubicacion, material=None, fecha_mov=None, propietario=None):
    # db se mantiene solo por compatibilidad
    if fecha_mov is None:
        fecha_mov = datetime.now().date()

    if hasattr(fecha_mov, "strftime"):
        fecha_mov_str = fecha_mov.strftime("%Y-%m-%d")
    else:
        fecha_mov_str = str(fecha_mov)

    estado = obtener_estado_actual(db, cilindro)

    payload = {
        "cilindro": cilindro,
        "estado": nuevo_estado,
        "fecha_mov": fecha_mov_str,
        "ubicacion": ubicacion,
    }

    if material is not None:
        payload["material"] = material

    if propietario is not None:
        payload["propietario"] = propietario

    if estado:
        actualizar_estado_cilindro_api(cilindro, payload)
    else:
        payload.setdefault("material", material or "")
        payload.setdefault("propietario", propietario or "")
        crear_estado_cilindro(payload)

    return payload


def actualizar_cilindro(db, codigo):
    # db se mantiene solo por compatibilidad
    actualizar_cilindro_api(codigo, {"nuevo": "NO"})
    cilindro = obtener_cilindro_actual(db, codigo)
    return cilindro


def validar_despacho(db, cilindro):
    estado = obtener_estado_actual(db, cilindro)

    if estado and estado.get("estado") == "EN CLIENTE":
        return False, "❌ Cilindro ya está en cliente"

    return True, ""


def validar_recepcion(db, cilindro):
    estado = obtener_estado_actual(db, cilindro)

    if not estado or estado.get("estado") != "EN CLIENTE":
        return False, "❌ Solo puedes devolver cilindros que están en cliente"

    return True, ""