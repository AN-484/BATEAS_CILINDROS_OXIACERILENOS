'''import tkinter as tk
from tkinter import ttk
from modules.cilindros import registrar_cilindro
from database import get_connection


def ventana_cilindros():

    ventana = tk.Toplevel()
    ventana.title("Cilindros")
    ventana.geometry("600x400")

    frame = tk.Frame(ventana)
    frame.pack(pady=10)

    tk.Label(frame,text="Codigo Cilindro").grid(row=0,column=0)
    entry_codigo = tk.Entry(frame)
    entry_codigo.grid(row=0,column=1)

    tk.Label(frame,text="Propietario").grid(row=1,column=0)
    entry_prop = tk.Entry(frame)
    entry_prop.grid(row=1,column=1)

    tabla = ttk.Treeview(
        ventana,
        columns=("codigo","propietario"),
        show="headings"
    )

    tabla.heading("codigo",text="Codigo")
    tabla.heading("propietario",text="Propietario")

    tabla.pack(fill="both",expand=True)


    def guardar():

        registrar_cilindro(
            entry_codigo.get(),
            entry_prop.get()
        )

        cargar()


    def cargar():

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM cilindros")

        datos = cursor.fetchall()

        for fila in tabla.get_children():
            tabla.delete(fila)

        for d in datos:
            tabla.insert("",tk.END,values=(d[1],d[2]))

        conn.close()


    tk.Button(frame,text="Registrar",command=guardar).grid(row=2,column=1)

    cargar()'''

import tkinter as tk
from modules.cilindros import agregar_cilindro

def ventana_cilindros():

    v = tk.Toplevel()

    v.title("Cilindros")

    tk.Label(v,text="Codigo Cilindro").pack()

    codigo = tk.Entry(v)
    codigo.pack()

    tk.Label(v,text="Propietario").pack()

    propietario = tk.Entry(v)
    propietario.pack()

    def guardar():

        agregar_cilindro(
        codigo.get(),
        propietario.get())

    tk.Button(v,text="Guardar",
    command=guardar).pack(pady=10)