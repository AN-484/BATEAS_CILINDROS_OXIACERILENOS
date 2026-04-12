from database import get_connection
from datetime import datetime

def registrar_entrada(guia,transportista,usuario):

    conn = get_connection()
    cursor = conn.cursor()

    fecha = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("""
    INSERT INTO entradas
    (fecha,guia,transportista,registrado_por)
    VALUES (?,?,?,?)
    """,(fecha,guia,transportista,usuario))

    conn.commit()
    conn.close()