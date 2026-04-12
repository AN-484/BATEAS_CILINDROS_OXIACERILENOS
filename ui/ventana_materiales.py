'''
import tkinter as tk
from tkinter import ttk
from modules.materiales import agregar_material, listar_materiales


def ventana_materiales():

    ventana = tk.Toplevel()
    ventana.title("Materiales")
    ventana.geometry("600x400")

    frame_form = tk.Frame(ventana)
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Codigo").grid(row=0,column=0)
    entry_codigo = tk.Entry(frame_form)
    entry_codigo.grid(row=0,column=1)

    tk.Label(frame_form, text="Nombre").grid(row=1,column=0)
    entry_nombre = tk.Entry(frame_form)
    entry_nombre.grid(row=1,column=1)

    tk.Label(frame_form, text="Medida").grid(row=2,column=0)
    entry_medida = tk.Entry(frame_form)
    entry_medida.grid(row=2,column=1)

    tabla = ttk.Treeview(ventana,columns=("codigo","nombre","medida"),show="headings")

    tabla.heading("codigo",text="Codigo")
    tabla.heading("nombre",text="Nombre")
    tabla.heading("medida",text="Medida")

    tabla.pack(fill="both",expand=True,pady=10)


    def cargar_tabla():

        for fila in tabla.get_children():
            tabla.delete(fila)

        datos = listar_materiales()

        for d in datos:
            tabla.insert("",tk.END,values=(d[1],d[2],d[3]))


    def guardar():

        agregar_material(
            entry_codigo.get(),
            entry_nombre.get(),
            entry_medida.get()
        )

        cargar_tabla()

    tk.Button(frame_form,text="Guardar",command=guardar).grid(row=3,column=1)

    cargar_tabla()'''


import tkinter as tk
from modules.materiales import agregar_material

def ventana_materiales():

    v = tk.Toplevel()

    v.title("Materiales")

    tk.Label(v,text="Codigo").pack()
    codigo = tk.Entry(v)
    codigo.pack()

    tk.Label(v,text="Nombre").pack()
    nombre = tk.Entry(v)
    nombre.pack()

    tk.Label(v,text="Medida").pack()
    medida = tk.Entry(v)
    medida.pack()

    def guardar():

        agregar_material(
        codigo.get(),
        nombre.get(),
        medida.get())

    tk.Button(v,text="Guardar",
    command=guardar).pack(pady=10)