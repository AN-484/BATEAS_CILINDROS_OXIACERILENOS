from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QComboBox,
    QDateEdit,
    QMessageBox
)
from PySide6.QtCore import QDate

from supabase_api import (
    listar_cilindros,
    listar_productos,
    listar_propietarios,
    crear_cilindro,
    eliminar_cilindro_api
)


class CilindrosUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cilindros")
        self.resize(600, 400)

        layout = QVBoxLayout()

        form = QHBoxLayout()

        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Código Cilindro")

        self.propietario = QComboBox()
        self.cargar_propietarios()

        self.producto = QComboBox()
        self.cargar_productos()

        self.fecha_hidro = QDateEdit()
        self.fecha_hidro.setCalendarPopup(True)
        self.fecha_hidro.setDate(QDate.currentDate())

        form.addWidget(self.codigo)
        form.addWidget(self.propietario)
        form.addWidget(self.producto)
        form.addWidget(self.fecha_hidro)

        layout.addLayout(form)

        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.agregar)

        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.eliminar)

        layout.addWidget(btn_add)
        layout.addWidget(btn_del)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Código",
            "Propietario",
            "Producto",
            "Fecha Hidrostática",
            "Modo"
        ])

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.cargar()

    def cargar(self):
        datos = listar_cilindros()
        datos_propietario = listar_propietarios()
        datos_materia = listar_productos()

        if not datos:
            self.table.setRowCount(0)
            return

        propietarios_map = {
            p.get("codigo", ""): p.get("nombre", "")
            for p in datos_propietario
        }

        productos_map = {
            p.get("codigo", ""): p.get("nombre", "")
            for p in datos_materia
        }

        datos = sorted(datos, key=lambda x: x.get("codigo", ""))

        self.table.setRowCount(len(datos))

        for i, d in enumerate(datos):
            fecha = ""
            fecha_hidro = d.get("fecha_hidrostatica")
            if fecha_hidro:
                fecha = str(fecha_hidro)

            propietario_nombre = propietarios_map.get(d.get("propietario", ""), "")
            producto_nombre = productos_map.get(d.get("producto", ""), "")

            self.table.setItem(i, 0, QTableWidgetItem(d.get("codigo", "")))
            self.table.setItem(i, 1, QTableWidgetItem(propietario_nombre))
            self.table.setItem(i, 2, QTableWidgetItem(producto_nombre))
            self.table.setItem(i, 3, QTableWidgetItem(fecha))
            self.table.setItem(i, 4, QTableWidgetItem(d.get("nuevo", "")))

    def agregar(self):
        codigo = self.codigo.text().strip()
        propietario = self.propietario.currentData()
        producto = self.producto.currentData()
        fecha_hidro = self.fecha_hidro.date().toPython()

        if not codigo:
            QMessageBox.warning(self, "Error", "Ingrese código de cilindro")
            return

        if not propietario:
            QMessageBox.warning(self, "Error", "Seleccione propietario")
            return

        if not producto:
            QMessageBox.warning(self, "Error", "Seleccione producto")
            return

        resp = crear_cilindro({
            "codigo": codigo,
            "propietario": propietario,
            "producto": producto,
            "fecha_hidrostatica": fecha_hidro.strftime("%Y-%m-%d"),
            "nuevo": "SI"
        })

        if resp is None:
            QMessageBox.warning(self, "Error", "No se pudo registrar el cilindro")
            return

        self.codigo.clear()
        self.propietario.setCurrentIndex(0)
        self.producto.setCurrentIndex(0)
        self.fecha_hidro.setDate(QDate.currentDate())
        self.cargar()

    def eliminar(self):
        row = self.table.currentRow()
        if row < 0:
            return

        codigo = self.table.item(row, 0).text()

        resp = eliminar_cilindro_api(codigo)

        if resp is None:
            QMessageBox.warning(self, "Error", "No se pudo eliminar el cilindro")
            return

        self.cargar()

    def cargar_productos(self):
        self.producto.clear()
        data = listar_productos()

        for t in sorted(data, key=lambda x: x.get("codigo", "")):
            self.producto.addItem(
                f"{t.get('codigo', '')} - {t.get('nombre', '')}",
                t.get("codigo", "")
            )

    def cargar_propietarios(self):
        self.propietario.clear()
        data = listar_propietarios()

        for p in sorted(data, key=lambda x: x.get("codigo", "")):
            self.propietario.addItem(
                f"{p.get('codigo', '')} - {p.get('nombre', '')}",
                p.get("codigo", "")
            )