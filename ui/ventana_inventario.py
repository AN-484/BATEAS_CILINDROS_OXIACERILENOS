'''import tkinter as tk
from tkinter import ttk
from modules.inventario import ver_inventario


def ventana_inventario():

    ventana = tk.Toplevel()
    ventana.title("Inventario")
    ventana.geometry("900x500")

    tabla = ttk.Treeview(
        ventana,
        columns=("cilindro","material","estado","ubicacion","fecha"),
        show="headings"
    )

    tabla.heading("cilindro",text="Cilindro")
    tabla.heading("material",text="Material")
    tabla.heading("estado",text="Estado")
    tabla.heading("ubicacion",text="Ubicacion")
    tabla.heading("fecha",text="Fecha")

    tabla.pack(fill="both",expand=True)


    datos = ver_inventario()

    for d in datos:

        tabla.insert("",tk.END,
        values=(d[1],d[2],d[3],d[4],d[5]))'''

import tkinter as tk
from tkinter import ttk
from database import get_connection

def ventana_inventario():

    v = tk.Toplevel()

    v.title("Inventario")

    tabla = ttk.Treeview(v,
    columns=("cilindro","material","estado","ubicacion","fecha"),
    show="headings")

    tabla.heading("cilindro",text="Cilindro")
    tabla.heading("material",text="Material")
    tabla.heading("estado",text="Estado")
    tabla.heading("ubicacion",text="Ubicacion")
    tabla.heading("fecha",text="Fecha")

    tabla.pack(fill="both",expand=True)

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM estado_cilindros")

    datos = cursor.fetchall()

    for d in datos:

        tabla.insert("",tk.END,
        values=(d[1],d[2],d[3],d[4],d[5]))

    conn.close()