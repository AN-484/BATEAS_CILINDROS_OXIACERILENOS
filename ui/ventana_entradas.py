import tkinter as tk
from tkinter import ttk
from modules.entradas import registrar_entrada


def ventana_entradas():

    ventana = tk.Toplevel()
    ventana.title("Registro de Entradas")
    ventana.geometry("500x300")

    frame = tk.Frame(ventana)
    frame.pack(pady=20)

    tk.Label(frame,text="Numero de Guia").grid(row=0,column=0)
    entry_guia = tk.Entry(frame)
    entry_guia.grid(row=0,column=1)

    tk.Label(frame,text="Transportista").grid(row=1,column=0)
    entry_transportista = tk.Entry(frame)
    entry_transportista.grid(row=1,column=1)

    tk.Label(frame,text="Registrado por").grid(row=2,column=0)
    entry_usuario = tk.Entry(frame)
    entry_usuario.grid(row=2,column=1)


    def guardar():

        registrar_entrada(
            entry_guia.get(),
            entry_transportista.get(),
            entry_usuario.get()
        )

        entry_guia.delete(0,tk.END)
        entry_transportista.delete(0,tk.END)
        entry_usuario.delete(0,tk.END)


    boton = tk.Button(frame,text="Registrar Entrada",command=guardar)
    boton.grid(row=3,column=1,pady=10)