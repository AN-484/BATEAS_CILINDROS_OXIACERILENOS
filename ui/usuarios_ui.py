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
    listar_usuarios,
    crear_usuario,
    eliminar_usuario_api
)


class UsuariosUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Usuarios (Personal)")
        self.resize(700, 400)

        layout = QVBoxLayout()

        form = QHBoxLayout()

        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Código")

        self.dni = QLineEdit()
        self.dni.setPlaceholderText("DNI")

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre")

        self.cargo = QLineEdit()
        self.cargo.setPlaceholderText("Cargo")

        form.addWidget(self.codigo)
        form.addWidget(self.dni)
        form.addWidget(self.nombre)
        form.addWidget(self.cargo)

        layout.addLayout(form)

        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.agregar)

        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.eliminar)

        layout.addWidget(btn_add)
        layout.addWidget(btn_del)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Código", "DNI", "Nombre", "Cargo"])

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.cargar()

    def cargar(self):
        datos = listar_usuarios()

        if not datos:
            self.table.setRowCount(0)
            return

        datos = sorted(datos, key=lambda x: x.get("codigo", ""))

        self.table.setRowCount(len(datos))

        for i, d in enumerate(datos):
            self.table.setItem(i, 0, QTableWidgetItem(d.get("codigo", "")))
            self.table.setItem(i, 1, QTableWidgetItem(d.get("dni", "")))
            self.table.setItem(i, 2, QTableWidgetItem(d.get("nombre", "")))
            self.table.setItem(i, 3, QTableWidgetItem(d.get("cargo", "")))

    def agregar(self):
        codigo = self.codigo.text().strip()
        dni = self.dni.text().strip()
        nombre = self.nombre.text().strip()
        cargo = self.cargo.text().strip()

        if not codigo or not dni or not nombre or not cargo:
            QMessageBox.warning(self, "Error", "Complete código, DNI, nombre y cargo")
            return

        if len(dni) != 8 or not dni.isdigit():
            QMessageBox.warning(self, "Error", "El DNI debe tener 8 dígitos")
            return

        resp = crear_usuario({
            "codigo": codigo,
            "dni": dni,
            "nombre": nombre,
            "cargo": cargo
        })

        if resp is None:
            QMessageBox.warning(self, "Error", "No se pudo registrar el usuario")
            return

        self.codigo.clear()
        self.dni.clear()
        self.nombre.clear()
        self.cargo.clear()
        self.cargar()

    def eliminar(self):
        row = self.table.currentRow()
        if row < 0:
            return

        codigo = self.table.item(row, 0).text()

        resp = eliminar_usuario_api(codigo)

        if resp is None:
            QMessageBox.warning(self, "Error", "No se pudo eliminar el usuario")
            return

        self.cargar()