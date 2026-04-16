from PySide6.QtWidgets import *
from ui.components.table_view import TableView
from ui.components.export_excel import exportar_excel

from supabase_api import (
    listar_entradas_salidas,
    listar_transportistas,
    listar_usuarios,
    listar_cilindros
)


class ReporteEntradasSalidas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reporte Ingresos / Recargas")

        layout = QVBoxLayout()

        # 🔍 filtros
        self.filtro = QLineEdit()
        self.filtro.setPlaceholderText("Buscar por n° de guía...")

        self.filtro_nro_documento = QLineEdit()
        self.filtro_nro_documento.setPlaceholderText("Buscar por n° de documento...")
        self.filtro_nro_documento.setMaxLength(10)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.cargar_datos)

        btn_excel = QPushButton("Exportar Excel")
        btn_excel.clicked.connect(self.exportar)

        self.tabla = TableView()

        layout.addWidget(self.filtro)
        layout.addWidget(self.filtro_nro_documento)
        layout.addWidget(btn_buscar)
        layout.addWidget(btn_excel)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

        self.headers = [
            "Fecha",
            "Guía",
            "N° Documento",
            "Cilindro",
            "F. Hidrostática",
            "Transportista",
            "Tipo",
            "Usuario"
        ]

        self.data = []

        self.cargar_datos()

    def cargar_datos(self):

        try:
            texto = self.filtro.text().strip()
            texto_doc = self.filtro_nro_documento.text().strip()

            resultados = listar_entradas_salidas()

            # 🔍 FILTROS
            if texto:
                resultados = [
                    r for r in resultados
                    if texto.lower() in str(r.get("nro_guia", "")).lower()
                ]

            elif texto_doc:
                resultados = [
                    r for r in resultados
                    if texto_doc.lower() in str(r.get("nro_documento", "")).lower()
                ]

            # 🔥 DICCIONARIOS (join manual)
            transportistas = {
                t.get("codigo"): t.get("nombre")
                for t in listar_transportistas()
            }

            usuarios = {
                u.get("codigo"): u.get("nombre")
                for u in listar_usuarios()
            }

            cilindros = {
                c.get("codigo"): c.get("fecha_hidrostatica")
                for c in listar_cilindros()
            }

            # 🔥 ARMAR DATA
            self.data = [
                [
                    r.get("fecha"),
                    r.get("nro_guia"),
                    r.get("nro_documento"),
                    r.get("cilindro"),
                    cilindros.get(r.get("cilindro")),
                    transportistas.get(r.get("transportista"), r.get("transportista")),
                    r.get("tipo"),
                    usuarios.get(r.get("registrado_por"), r.get("registrado_por"))
                ]
                for r in resultados
            ]

            self.tabla.cargar_datos(self.headers, self.data)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar datos: {str(e)}")

    def exportar(self):
        exportar_excel(self.headers, self.data)
        QMessageBox.information(self, "OK", "Exportado a Excel")