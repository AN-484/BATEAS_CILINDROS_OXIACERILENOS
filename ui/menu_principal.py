'''import tkinter as tk
from tkinter import ttk
from ui.ventana_materiales import ventana_materiales
from ui.ventana_transportistas import ventana_transportistas
from ui.ventana_cilindros import ventana_cilindros
from ui.ventana_entradas import ventana_entradas
from ui.ventana_salidas import ventana_salidas
from ui.ventana_inventario import ventana_inventario


def iniciar_menu():

    root = tk.Tk()
    root.title("Sistema Logístico de Cilindros")
    root.geometry("700x500")

    titulo = tk.Label(root,text="SISTEMA LOGÍSTICO DE GASES",
                      font=("Arial",18))
    titulo.pack(pady=20)

    frame = tk.Frame(root)
    frame.pack()

    botones = [

        ("Materiales",ventana_materiales),
        ("Transportistas",ventana_transportistas),
        ("Cilindros",ventana_cilindros),
        ("Entradas",ventana_entradas),
        ("Salidas",ventana_salidas),
        ("Inventario",ventana_inventario)
    ]

    for texto,funcion in botones:

        btn = tk.Button(frame,
                        text=texto,
                        width=25,
                        height=2,
                        command=funcion)

        btn.pack(pady=5)

    root.mainloop()'''

import tkinter as tk

from ui.ventana_materiales import ventana_materiales
from ui.ventana_cilindros import ventana_cilindros
from ui.ventana_despachos import ventana_despachos
from ui.ventana_recepciones import ventana_recepciones
from ui.ventana_inventario import ventana_inventario

def iniciar_menu():

    root = tk.Tk()
    root.title("Sistema Logistico de Cilindros")
    root.geometry("500x400")

    tk.Label(root,text="SISTEMA LOGISTICO",
    font=("Arial",18)).pack(pady=20)

    botones = [

    ("Materiales",ventana_materiales),
    ("Cilindros",ventana_cilindros),
    ("Despachos",ventana_despachos),
    ("Recepciones",ventana_recepciones),
    ("Inventario",ventana_inventario)

    ]

    for t,f in botones:

        tk.Button(root,text=t,width=30,
        command=f).pack(pady=5)

    root.mainloop()