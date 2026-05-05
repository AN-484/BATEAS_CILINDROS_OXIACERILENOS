from PySide6.QtWidgets import *
from PySide6.QtGui import QColor
from ui.components.table_view import TableView
from ui.components.export_excel import exportar_excel
from datetime import datetime, timedelta

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

        # ================= FILTROS =================
        filtros = QHBoxLayout()

        self.f_producto = QComboBox()
        self.f_producto.addItem("TODOS", "")

        self.f_propietario = QComboBox()
        self.f_propietario.addItem("TODOS", "")

        self.f_estado = QComboBox()
        self.f_estado.addItem("TODOS", "")
        self.f_estado.addItems([
            "STOCK",
            "VACIO",
            "EN CLIENTE",
            "EN PROVEEDOR"
        ])

        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.cargar)

        filtros.addWidget(QLabel("Producto:"))
        filtros.addWidget(self.f_producto)

        filtros.addWidget(QLabel("Propietario:"))
        filtros.addWidget(self.f_propietario)

        filtros.addWidget(QLabel("Estado:"))
        filtros.addWidget(self.f_estado)

        filtros.addWidget(btn_buscar)

        layout.addLayout(filtros)

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
            "Alerta Hidro",
            "Estado",
            "Fecha",
            "Ubicación"
        ]

        self.data = []

        self.cargar_filtros()
        self.cargar()

    def cargar_filtros(self):
        productos = listar_productos()
        propietarios = listar_propietarios()

        for p in sorted(productos, key=lambda x: x.get("nombre", "")):
            self.f_producto.addItem(
                p.get("nombre", ""),
                p.get("codigo", "")
            )

        for p in sorted(propietarios, key=lambda x: x.get("nombre", "")):
            self.f_propietario.addItem(
                p.get("nombre", ""),
                p.get("codigo", "")
            )

    def calcular_alerta_hidro(self, fecha_hidro):
        if not fecha_hidro:
            return "⚪ Sin fecha", None

        try:
            fecha_hidro = datetime.strptime(str(fecha_hidro), "%Y-%m-%d").date()
            fecha_vencimiento = fecha_hidro.replace(year=fecha_hidro.year + 5)
            hoy = datetime.now().date()

            dias_restantes = (fecha_vencimiento - hoy).days

            if dias_restantes < 0:
                return "🔴 Vencido", QColor(255, 180, 180)

            if dias_restantes <= 90:
                return "🟡 Por vencer", QColor(255, 235, 150)

            return "🟢 Vigente", QColor(190, 255, 190)

        except Exception:
            return "⚪ Fecha inválida", None

    def cargar(self):
        try:
            resultados = obtener_registros("estado_cilindros")

            productos_lista = listar_productos()
            propietarios_lista = listar_propietarios()
            cilindros_lista = listar_cilindros()

            productos = {
                p.get("codigo"): p.get("nombre")
                for p in productos_lista
            }

            propietarios = {
                p.get("codigo"): p.get("nombre")
                for p in propietarios_lista
            }

            cilindros = {
                c.get("codigo"): c.get("fecha_hidrostatica")
                for c in cilindros_lista
            }

            # ================= FILTRAR =================
            producto_filtro = self.f_producto.currentData()
            propietario_filtro = self.f_propietario.currentData()
            estado_filtro = self.f_estado.currentText()

            if producto_filtro:
                resultados = [
                    r for r in resultados
                    if r.get("material") == producto_filtro
                ]

            if propietario_filtro:
                resultados = [
                    r for r in resultados
                    if r.get("propietario") == propietario_filtro
                ]

            if estado_filtro != "TODOS":
                resultados = [
                    r for r in resultados
                    if r.get("estado") == estado_filtro
                ]

            self.data = []

            colores_alerta = []

            for r in resultados:
                fecha_hidro = cilindros.get(r.get("cilindro"))
                alerta_texto, color = self.calcular_alerta_hidro(fecha_hidro)

                self.data.append([
                    r.get("cilindro"),
                    propietarios.get(r.get("propietario"), r.get("propietario")) if r.get("propietario") else "N/A",
                    productos.get(r.get("material"), r.get("material")),
                    fecha_hidro,
                    alerta_texto,
                    r.get("estado"),
                    r.get("fecha_mov"),
                    r.get("ubicacion")
                ])

                colores_alerta.append(color)

            self.tabla.cargar_datos(self.headers, self.data)

            # ================= ANCHOS =================
            self.tabla.setColumnWidth(0, 120)
            self.tabla.setColumnWidth(1, 180)
            self.tabla.setColumnWidth(2, 320)  # material más amplio
            self.tabla.setColumnWidth(3, 130)
            self.tabla.setColumnWidth(4, 130)
            self.tabla.setColumnWidth(5, 120)
            self.tabla.setColumnWidth(6, 120)
            self.tabla.setColumnWidth(7, 180)

            # ================= COLOREAR ALERTA =================
            for row, color in enumerate(colores_alerta):
                item = self.tabla.item(row, 4)

                if item and color:
                    item.setBackground(color)

            # ================= ALERTA CLIENTE +30 DÍAS =================
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
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo cargar el reporte: {str(e)}"
            )

    def exportar(self):
        exportar_excel(
            self.headers,
            self.data,
            "estado_cilindros.xlsx"
        )
        QMessageBox.information(
            self,
            "OK",
            "Exportado a Excel"
        )