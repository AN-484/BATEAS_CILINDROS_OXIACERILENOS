from database import get_connection
from datetime import datetime

def registrar_recepcion(cilindro,material,area,encargado,responsable,usuario):

    conn = get_connection()
    cursor = conn.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    cursor.execute("""
    INSERT INTO movimientos VALUES(NULL,?,?,?,?,?,?,?,?)
    """,(cilindro,material,area,"RECEPCION",
    encargado,responsable,usuario,fecha))

    cursor.execute("""
    INSERT INTO estado_cilindros VALUES(NULL,?,?,?,?,?)
    """,(cilindro,material,"DISPONIBLE",area,fecha))

    conn.commit()
    conn.close()