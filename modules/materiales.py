'''from database import get_connection

def agregar_material(codigo,nombre,medida):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO materiales
    (codigo_material,nombre_material,medida)
    VALUES (?,?,?)
    """,(codigo,nombre,medida))

    conn.commit()
    conn.close()

def listar_materiales():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM materiales")

    datos = cursor.fetchall()

    conn.close()

    return datos'''

from database import get_connection

def agregar_material(codigo,nombre,medida):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO materiales VALUES (NULL,?,?,?)",
    (codigo,nombre,medida))

    conn.commit()
    conn.close()

def listar_materiales():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM materiales")

    datos = cursor.fetchall()

    conn.close()

    return datos