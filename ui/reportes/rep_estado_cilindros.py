from PySide6.QtWidgets import *
from ui.components.table_view import TableView
from ui.components.export_excel import exportar_excel
from datetime import datetime

from supabase_api import (
    obtener_registros,
    listar_productos,
    listar_propietarios,
    listar_cilindros
)


class ReporteEstadoCilindros(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Estado de Cilindros")

        layout = QVBoxLayout()

        btn_excel = QPushButton("Exportar Excel")
        btn_excel.clicked.connect(self.exportar)

        self.tabla = TableView()

        layout.addWidget(btn_excel)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

        self.headers = [
            "Cilindro",
            "Propietario",
            "Material",
            "F. Hidrostática",
            "Estado",
            "Fecha",
            "Ubicación"
        ]
        self.data = []

        self.cargar()

    def cargar(self):
        try:
            resultados = obtener_registros("estado_cilindros")

            productos = {
                p.get("codigo"): p.get("nombre")
                for p in listar_productos()
            }

            propietarios = {
                p.get("codigo"): p.get("nombre")
                for p in listar_propietarios()
            }

            cilindros = {
                c.get("codigo"): c.get("fecha_hidrostatica")
                for c in listar_cilindros()
            }

            self.data = [
                [
                    r.get("cilindro"),
                    propietarios.get(r.get("propietario"), r.get("propietario")) if r.get("propietario") else "N/A",
                    productos.get(r.get("material"), r.get("material")),
                    cilindros.get(r.get("cilindro")),
                    r.get("estado"),
                    r.get("fecha_mov"),
                    r.get("ubicacion")
                ]
                for r in resultados
            ]

            self.tabla.cargar_datos(self.headers, self.data)

            alertas = []

            for d in resultados:
                if d.get("estado") != "EN CLIENTE":
                    continue

                fecha_mov = d.get("fecha_mov")
                if not fecha_mov:
                    continue

                try:
                    fecha_obj = datetime.strptime(str(fecha_mov), "%Y-%m-%d").date()
                    if (datetime.now().date() - fecha_obj).days > 30:
                        alertas.append(d)
                except Exception:
                    pass

            if alertas:
                QMessageBox.warning(
                    self,
                    "Alerta",
                    f"{len(alertas)} cilindros llevan más de 30 días en cliente"
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el reporte: {str(e)}")

    def exportar(self):
        exportar_excel(self.headers, self.data, "estado_cilindros.xlsx")
        QMessageBox.information(self, "OK", "Exportado a Excel")