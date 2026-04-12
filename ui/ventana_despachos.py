import tkinter as tk
from modules.despachos import registrar_despacho

def ventana_despachos():

    v = tk.Toplevel()

    v.title("Despacho")

    entradas = []

    labels = ["Cilindro","Material",
    "Area","Encargado","Responsable","Usuario"]

    for l in labels:

        tk.Label(v,text=l).pack()

        e = tk.Entry(v)

        e.pack()

        entradas.append(e)

    def guardar():

        registrar_despacho(

        entradas[0].get(),
        entradas[1].get(),
        entradas[2].get(),
        entradas[3].get(),
        entradas[4].get(),
        entradas[5].get()

        )

    tk.Button(v,text="Registrar",
    command=guardar).pack(pady=10)