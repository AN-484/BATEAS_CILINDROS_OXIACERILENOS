from database import get_connection

def actualizar_estado(cilindro,material,estado,ubicacion):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO inventario
    (codigo_cilindro,codigo_material,estado,ubicacion,fecha_movimiento)
    VALUES (?,?,?,?,datetime('now'))
    """,(cilindro,material,estado,ubicacion))

    conn.commit()
    conn.close()

def ver_inventario():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM inventario
    """)

    datos = cursor.fetchall()

    conn.close()

    return datos