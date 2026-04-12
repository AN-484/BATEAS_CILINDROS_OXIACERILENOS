from database import get_connection
from datetime import datetime

def registrar_despacho(cilindro,material,area,encargado,responsable,usuario):

    conn = get_connection()
    cursor = conn.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute("""
    INSERT INTO despachos VALUES(NULL,?,?,?,?,?,?,?,?)
    """,(cilindro,material,area,"DESPACHADO",
    encargado,responsable,usuario,fecha))

    cursor.execute("""
    INSERT INTO movimientos VALUES(NULL,?,?,?,?,?,?,?,?)
    """,(cilindro,material,area,"DESPACHADO",
    encargado,responsable,usuario,fecha))

    cursor.execute("""
    INSERT INTO estado_cilindros VALUES(NULL,?,?,?,?,?)
    """,(cilindro,material,"EN CLIENTE",area,fecha))

    conn.commit()
    conn.close()