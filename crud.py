from database import SessionLocal
from models import EstadoCilindro
from datetime import datetime

def obtener_estado_actual(db, cilindro):
    return db.query(EstadoCilindro).filter_by(cilindro=cilindro).first()


def actualizar_estado(db, cilindro, nuevo_estado, ubicacion, material=None, fecha_mov=None, propietario=None):
    if fecha_mov is None:
        fecha_mov = datetime.now()
    
    estado = obtener_estado_actual(db, cilindro)

    if estado:
        estado.estado = nuevo_estado
        estado.fecha_mov = fecha_mov
        estado.ubicacion = ubicacion
        if material:
            estado.material = material
        if propietario:
            estado.propietario = propietario
    else:
        estado = EstadoCilindro(
            cilindro=cilindro,
            estado=nuevo_estado,
            fecha_mov=fecha_mov,
            ubicacion=ubicacion,
            material=material or "",
            propietario=propietario or ""
        )
        db.add(estado)

    return estado


def validar_despacho(db, cilindro):
    estado = obtener_estado_actual(db, cilindro)

    if estado and estado.estado == "EN CLIENTE":
        return False, "❌ Cilindro ya está en cliente"

    return True, ""


def validar_recepcion(db, cilindro):
    estado = obtener_estado_actual(db, cilindro)

    if not estado or estado.estado != "EN CLIENTE":
        return False, "❌ Solo puedes devolver cilindros que están en cliente"

    return True, ""