from PySide6.QtWidgets import *
from ui.components.table_view import TableView

from supabase_api import (
    listar_movimientos_detalle,
    listar_ubicaciones,
    listar_productos
)


class KardexUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kardex por Cilindro")

        layout = QVBoxLayout()

        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Código de cilindro")

        btn = QPushButton("Buscar")
        btn.clicked.connect(self.buscar)

        self.tabla = TableView()

        layout.addWidget(self.codigo)
        layout.addWidget(btn)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

    def buscar(self):
        try:
            codigo = self.codigo.text().strip()

            data = listar_movimientos_detalle()

            if codigo:
                data = [
                    d for d in data
                    if d.get("cilindro") == codigo
                ]

            areas = {
                a.get("codigo"): a.get("nombre")
                for a in listar_ubicaciones()
            }

            materiales = {
                p.get("codigo"): p.get("nombre")
                for p in listar_productos()
            }

            headers = ["Fecha", "Tipo", "Área", "Material"]

            rows = [
                [
                    d.get("fecha"),
                    d.get("tipo"),
                    areas.get(d.get("area"), d.get("area")),
                    materiales.get(d.get("material"), d.get("material"))
                ]
                for d in data
            ]

            self.tabla.cargar_datos(headers, rows)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el kardex: {str(e)}")