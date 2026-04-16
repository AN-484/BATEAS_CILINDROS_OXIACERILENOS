from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QLineEdit,
    QMessageBox
)

from supabase_api import (
    listar_productos,
    crear_producto,
    eliminar_producto_api
)


class ProductosUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Productos")
        self.resize(600, 400)

        layout = QVBoxLayout()

        form = QHBoxLayout()

        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Código")

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre")

        self.medida = QLineEdit()
        self.medida.setPlaceholderText("Medida")

        form.addWidget(self.codigo)
        form.addWidget(self.nombre)
        form.addWidget(self.medida)

        layout.addLayout(form)

        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.agregar)

        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.eliminar)

        layout.addWidget(btn_add)
        layout.addWidget(btn_del)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Código", "Nombre", "Medida"])

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.cargar()

    def cargar(self):
        datos = listar_productos()

        if not datos:
            self.table.setRowCount(0)
            return

        datos = sorted(datos, key=lambda x: x.get("codigo", ""))

        self.table.setRowCount(len(datos))

        for i, d in enumerate(datos):
            self.table.setItem(i, 0, QTableWidgetItem(d.get("codigo", "")))
            self.table.setItem(i, 1, QTableWidgetItem(d.get("nombre", "")))
            self.table.setItem(i, 2, QTableWidgetItem(d.get("medida", "")))

    def agregar(self):
        codigo = self.codigo.text().strip()
        nombre = self.nombre.text().strip()
        medida = self.medida.text().strip()

        if not codigo or not nombre or not medida:
            QMessageBox.warning(self, "Error", "Complete código, nombre y medida")
            return

        resp = crear_producto({
            "codigo": codigo,
            "nombre": nombre,
            "medida": medida
        })

        if resp is None:
            QMessageBox.warning(self, "Error", "No se pudo registrar el producto")
            return

        self.codigo.clear()
        self.nombre.clear()
        self.medida.clear()
        self.cargar()

    def eliminar(self):
        row = self.table.currentRow()
        if row < 0:
            return

        codigo = self.table.item(row, 0).text()

        resp = eliminar_producto_api(codigo)

        if resp is None:
            QMessageBox.warning(self, "Error", "No se pudo eliminar el producto")
            return

        self.cargar()