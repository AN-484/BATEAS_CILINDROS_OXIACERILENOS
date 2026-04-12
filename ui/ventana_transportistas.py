import tkinter as tk
from tkinter import ttk
from database import get_connection


def ventana_transportistas():

    ventana = tk.Toplevel()
    ventana.title("Transportistas")
    ventana.geometry("600x400")

    frame = tk.Frame(ventana)
    frame.pack(pady=10)

    tk.Label(frame,text="Codigo").grid(row=0,column=0)
    entry_codigo = tk.Entry(frame)
    entry_codigo.grid(row=0,column=1)

    tk.Label(frame,text="Nombre").grid(row=1,column=0)
    entry_nombre = tk.Entry(frame)
    entry_nombre.grid(row=1,column=1)

    tk.Label(frame,text="RUC").grid(row=2,column=0)
    entry_ruc = tk.Entry(frame)
    entry_ruc.grid(row=2,column=1)

    tabla = ttk.Treeview(
        ventana,
        columns=("codigo","nombre","ruc"),
        show="headings"
    )

    tabla.heading("codigo",text="Codigo")
    tabla.heading("nombre",text="Nombre")
    tabla.heading("ruc",text="RUC")

    tabla.pack(fill="both",expand=True)


    def guardar():

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO transportistas
        (codigo,nombre,ruc)
        VALUES (?,?,?)
        """,(entry_codigo.get(),
             entry_nombre.get(),
             entry_ruc.get()))

        conn.commit()
        conn.close()

        cargar()


    def cargar():

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM transportistas")

        datos = cursor.fetchall()

        for fila in tabla.get_children():
            tabla.delete(fila)

        for d in datos:
            tabla.insert("",tk.END,values=(d[1],d[2],d[3]))

        conn.close()


    tk.Button(frame,text="Guardar",command=guardar).grid(row=3,column=1)

    cargar()