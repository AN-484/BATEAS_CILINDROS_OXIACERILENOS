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
    listar_transportistas,
    crear_transportista,
    eliminar_transportista_api
)


class TransportistasUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transportistas")
        self.resize(600, 400)

        layout = QVBoxLayout()

        form = QHBoxLayout()

        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Código")

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre")

        self.ruc = QLineEdit()
        self.ruc.setPlaceholderText("RUC")

        form.addWidget(self.codigo)
        form.addWidget(self.nombre)
        form.addWidget(self.ruc)

        layout.addLayout(form)

        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.agregar)

        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.eliminar)

        layout.addWidget(btn_add)
        layout.addWidget(btn_del)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Código", "Nombre", "RUC"])

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.cargar()

    def cargar(self):
        datos = listar_transportistas()

        if not datos:
            self.table.setRowCount(0)
            return

        datos = sorted(datos, key=lambda x: x.get("codigo", ""))

        self.table.setRowCount(len(datos))

        for i, d in enumerate(datos):
            self.table.setItem(i, 0, QTableWidgetItem(d.get("codigo", "")))
            self.table.setItem(i, 1, QTableWidgetItem(d.get("nombre", "")))
            self.table.setItem(i, 2, QTableWidgetItem(d.get("ruc", "")))

    def agregar(self):
        codigo = self.codigo.text().strip()
        nombre = self.nombre.text().strip()
        ruc = self.ruc.text().strip()

        if not codigo or not nombre or not ruc:
            QMessageBox.warning(self, "Error", "Complete código, nombre y RUC")
            return

        resp = crear_transportista({
            "codigo": codigo,
            "nombre": nombre,
            "ruc": ruc
        })

        if resp is None:
            QMessageBox.warning(self, "Error", "No se pudo registrar el transportista")
            return

        self.codigo.clear()
        self.nombre.clear()
        self.ruc.clear()
        self.cargar()

    def eliminar(self):
        row = self.table.currentRow()
        if row < 0:
            return

        codigo = self.table.item(row, 0).text()

        resp = eliminar_transportista_api(codigo)

        if resp is None:
            QMessageBox.warning(self, "Error", "No se pudo eliminar el transportista")
            return

        self.cargar()