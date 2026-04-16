from PySide6.QtWidgets import *
from ui.components.table_view import TableView
from ui.components.export_excel import exportar_excel

from supabase_api import (
    listar_movimientos_detalle,
    listar_productos,
    listar_ubicaciones,
    listar_usuarios
)


class ReporteMovimientos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Búsqueda Avanzada - Despachos / Devoluciones")

        layout = QVBoxLayout()

        filtros1 = QHBoxLayout()

        self.f_cilindro = QLineEdit()
        self.f_cilindro.setPlaceholderText("Cilindro")

        self.f_area = QComboBox()
        self.f_area.addItem("TODOS")
        self.cargar_areas()

        self.f_tipo = QComboBox()
        self.f_tipo.addItem("TODOS")
        self.f_tipo.addItems(["DESPACHO", "DEVOLUCION"])

        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar)

        filtros1.addWidget(QLabel("Cilindro:"))
        filtros1.addWidget(self.f_cilindro)
        filtros1.addWidget(QLabel("Área:"))
        filtros1.addWidget(self.f_area)
        filtros1.addWidget(QLabel("Tipo:"))
        filtros1.addWidget(self.f_tipo)
        filtros1.addWidget(btn_buscar)

        filtros2 = QHBoxLayout()

        self.f_material = QComboBox()
        self.f_material.addItem("TODOS")
        self.cargar_materiales()

        filtros2.addWidget(QLabel("Material:"))
        filtros2.addWidget(self.f_material)
        filtros2.addStretch()

        self.tabla = TableView()

        btn_excel = QPushButton("Exportar Excel")
        btn_excel.clicked.connect(self.exportar)

        layout.addLayout(filtros1)
        layout.addLayout(filtros2)
        layout.addWidget(btn_excel)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

        self.headers = [
            "Fecha",
            "Cilindro",
            "Material",
            "Área",
            "Tipo",
            "Autorizado por",
            "Usuario Atendido",
            "Registrado por"
        ]
        self.data = []

    def cargar_materiales(self):
        for p in sorted(listar_productos(), key=lambda x: x.get("nombre", "")):
            self.f_material.addItem(
                p.get("nombre", ""),
                p.get("codigo", "")
            )

    def cargar_areas(self):
        for u in sorted(listar_ubicaciones(), key=lambda x: x.get("nombre", "")):
            self.f_area.addItem(
                u.get("nombre", ""),
                u.get("codigo", "")
            )

    def buscar(self):
        try:
            resultados = listar_movimientos_detalle()

            if self.f_cilindro.text():
                texto = self.f_cilindro.text().strip().lower()
                resultados = [
                    r for r in resultados
                    if texto in str(r.get("cilindro", "")).lower()
                ]

            if self.f_material.currentText() != "TODOS":
                resultados = [
                    r for r in resultados
                    if r.get("material") == self.f_material.currentData()
                ]

            if self.f_area.currentText() != "TODOS":
                resultados = [
                    r for r in resultados
                    if r.get("area") == self.f_area.currentData()
                ]

            if self.f_tipo.currentText() != "TODOS":
                resultados = [
                    r for r in resultados
                    if r.get("tipo") == self.f_tipo.currentText()
                ]

            productos = {
                p.get("codigo"): p.get("nombre")
                for p in listar_productos()
            }

            ubicaciones = {
                u.get("codigo"): u.get("nombre")
                for u in listar_ubicaciones()
            }

            usuarios = {
                u.get("codigo"): u.get("nombre")
                for u in listar_usuarios()
            }

            self.data = [
                [
                    r.get("fecha"),
                    r.get("cilindro"),
                    productos.get(r.get("material"), r.get("material")),
                    ubicaciones.get(r.get("area"), r.get("area")),
                    r.get("tipo"),
                    usuarios.get(r.get("encargado_almacen"), r.get("encargado_almacen")),
                    r.get("responsable_area"),
                    usuarios.get(r.get("registrado_por"), r.get("registrado_por"))
                ]
                for r in resultados
            ]

            self.tabla.cargar_datos(self.headers, self.data)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo cargar el reporte: {str(e)}")

    def exportar(self):
        exportar_excel(self.headers, self.data)
        QMessageBox.information(self, "OK", "Exportado")