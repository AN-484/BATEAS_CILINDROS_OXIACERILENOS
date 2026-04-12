import tkinter as tk
from modules.salidas import registrar_salida


def ventana_salidas():

    ventana = tk.Toplevel()
    ventana.title("Registro de Salidas")
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

        registrar_salida(
            entry_guia.get(),
            entry_transportista.get(),
            entry_usuario.get()
        ) 


    tk.Button(frame,text="Registrar Salida",command=guardar).grid(row=3,column=1,pady=10)