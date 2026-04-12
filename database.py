'''import sqlite3

DB_NAME = "logistica_gases.db"

def get_connection():
    return sqlite3.connect(DB_NAME)

def crear_tablas():

    conn = get_connection()
    cursor = conn.cursor()

    # MATERIALES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materiales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_material TEXT UNIQUE,
        nombre_material TEXT,
        medida TEXT
    )
    """)

    # TRANSPORTISTAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transportistas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nombre TEXT,
        ruc TEXT
    )
    """)

    # USUARIOS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nombre TEXT,
        cargo TEXT
    )
    """)

    # UBICACIONES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ubicaciones(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nombre TEXT
    )
    """)

    # ALMACENES
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS almacenes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo TEXT,
        nombre TEXT
    )
    """)

    # CILINDROS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cilindros(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_cilindro TEXT UNIQUE,
        propietario TEXT
    )
    """)

    # INVENTARIO ACTUAL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventario(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_cilindro TEXT,
        codigo_material TEXT,
        estado TEXT,
        ubicacion TEXT,
        fecha_movimiento TEXT,
        observacion TEXT
    )
    """)

    # ENTRADAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS entradas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        guia TEXT,
        transportista TEXT,
        registrado_por TEXT
    )
    """)

    # SALIDAS
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS salidas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT,
        guia TEXT,
        transportista TEXT,
        registrado_por TEXT
    )
    """)

    # MOVIMIENTOS HISTORIAL
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        codigo_cilindro TEXT,
        material TEXT,
        area TEXT,
        estado TEXT,
        encargado TEXT,
        responsable TEXT,
        registrado_por TEXT,
        fecha TEXT
    )
    """)

    conn.commit()
    conn.close()'''


import sqlite3

DB = "logistica_gases.db"

def get_connection():

    return sqlite3.connect(DB)

def crear_tablas():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materiales(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    nombre TEXT,
    medida TEXT)
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cilindros(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    propietario TEXT)
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ubicaciones(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    nombre TEXT)
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS almacenes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    nombre TEXT)
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS usuarios(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT,
    nombre TEXT,
    cargo TEXT)
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS estado_cilindros(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_cilindro TEXT,
    material TEXT,
    estado TEXT,
    ubicacion TEXT,
    fecha TEXT)
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS despachos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cilindro TEXT,
    material TEXT,
    area TEXT,
    estado TEXT,
    encargado TEXT,
    responsable TEXT,
    usuario TEXT,
    fecha TEXT)
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS movimientos(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cilindro TEXT,
    material TEXT,
    area TEXT,
    estado TEXT,
    encargado TEXT,
    responsable TEXT,
    usuario TEXT,
    fecha TEXT)
    """)

    conn.commit()
    conn.close()