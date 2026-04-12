from sqlalchemy import Column, String, Date
from database import Base
from datetime import date


# 🔐 LOGIN
class Acceso(Base):
    __tablename__ = "accesos"
    usuario = Column(String, primary_key=True)
    password = Column(String)

# 👷 PERSONAL
class Usuario(Base):
    __tablename__ = "usuarios"
    codigo = Column(String, primary_key=True)
    nombre = Column(String)
    cargo = Column(String)

# 📦 MAESTROS
class Producto(Base):
    __tablename__ = "productos"
    codigo = Column(String, primary_key=True)
    nombre = Column(String)
    medida = Column(String)

class Transportista(Base):
    __tablename__ = "transportistas"
    codigo = Column(String, primary_key=True)
    nombre = Column(String)
    ruc = Column(String)

class Ubicacion(Base):
    __tablename__ = "ubicaciones"
    codigo = Column(String, primary_key=True)
    nombre = Column(String)

class Almacen(Base):
    __tablename__ = "almacenes"
    codigo = Column(String, primary_key=True)
    nombre = Column(String)

class Cilindro(Base):
    __tablename__ = "cilindros"
    codigo = Column(String, primary_key=True)
    propietario = Column(String)
    producto = Column(String)
    fecha_hidrostatica = Column(Date)

class Propietario(Base):
    __tablename__ = "propietarios"
    codigo = Column(String, primary_key=True)
    nombre = Column(String)

class Guias(Base):
    __tablename__ = "guias"
    serie = Column(String, primary_key=True)


class EntradaSalida(Base):
    __tablename__ = "entradas_salidas"

    id = Column(String, primary_key=True)
    fecha = Column(Date, default=date.today)
    nro_guia = Column(String)
    cilindro = Column(String)
    producto = Column(String)
    cod_transportista = Column(String)
    transportista = Column(String)

    tipo = Column(String)  # ENTRADA / SALIDA

    registrado_por = Column(String)

class MovimientoDetalle(Base):
    __tablename__ = "movimientos_detalle"

    id = Column(String, primary_key=True)
    fecha = Column(Date, default=date.today)

    cilindro = Column(String)
    material = Column(String)

    area = Column(String)

    tipo = Column(String)  # DESPACHO / RECEPCION

    encargado_almacen = Column(String)
    responsable_area = Column(String)

    registrado_por = Column(String)

class EstadoCilindro(Base):
    __tablename__ = "estado_cilindros"

    cilindro = Column(String, primary_key=True)

    propietario = Column(String)

    material = Column(String)
    nombre_material = Column(String)
    medida = Column(String)

    capacidad = Column(String, default="1")

    estado = Column(String)  # DISPONIBLE / VACIO / EN CLIENTE / EN PROVEEDOR

    fecha_mov = Column(Date)

    ubicacion = Column(String)

    obs = Column(String)

class HistorialMovimientos(Base):
    __tablename__ = "historial_movimientos"

    id = Column(String, primary_key=True)
    fecha = Column(Date)

    cilindro = Column(String)
    material = Column(String)

    area = Column(String)

    estado = Column(String)

    encargado_almacen = Column(String)
    responsable_area = Column(String)
    registrado_por = Column(String)

class HistorialEntradaSalida(Base):
    __tablename__ = "historial_entradas_salidas"

    id = Column(String, primary_key=True)
    fecha = Column(Date)

    nro_guia = Column(String)

    cod_transportista = Column(String)
    transportista = Column(String)

    tipo = Column(String)

    registrado_por = Column(String)