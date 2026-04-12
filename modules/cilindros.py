'''from database import get_connection

def registrar_cilindro(codigo,propietario):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO cilindros
    (codigo_cilindro,propietario)
    VALUES (?,?)
    """,(codigo,propietario))

    conn.commit()
    conn.close()'''

from database import get_connection

def agregar_cilindro(codigo,propietario):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
    "INSERT INTO cilindros VALUES(NULL,?,?)",
    (codigo,propietario))

    conn.commit()
    conn.close()

def listar_cilindros():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM cilindros")

    datos = cursor.fetchall()

    conn.close()

    return datos