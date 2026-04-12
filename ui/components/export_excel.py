import pandas as pd

def exportar_excel(headers, data, filename="reporte.xlsx"):
    df = pd.DataFrame(data, columns=headers)
    df.to_excel(filename, index=False)