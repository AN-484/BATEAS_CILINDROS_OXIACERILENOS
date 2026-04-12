from database import get_connection

def buscar_cilindro(codigo):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM inventario
    WHERE codigo_cilindro=?
    """,(codigo,))

    dato = cursor.fetchone()

    conn.close()

    return dato