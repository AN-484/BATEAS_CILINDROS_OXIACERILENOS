import pandas as pd
import sqlite3

def exportar_inventario():

    conn = sqlite3.connect("logistica_gases.db")

    df = pd.read_sql_query(
        "SELECT * FROM inventario",
        conn
    )

    df.to_excel("inventario.xlsx",index=False)

    print("Inventario exportado")