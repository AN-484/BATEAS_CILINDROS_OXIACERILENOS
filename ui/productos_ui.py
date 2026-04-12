from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit
from database import SessionLocal
from models import Producto

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
        db = SessionLocal()
        datos = db.query(Producto).all()
        db.close()

        self.table.setRowCount(len(datos))

        for i, d in enumerate(datos):
            self.table.setItem(i, 0, QTableWidgetItem(d.codigo))
            self.table.setItem(i, 1, QTableWidgetItem(d.nombre))
            self.table.setItem(i, 2, QTableWidgetItem(d.medida))

    def agregar(self):
        db = SessionLocal()

        nuevo = Producto(
            codigo=self.codigo.text(),
            nombre=self.nombre.text(),
            medida=self.medida.text()
        )

        db.add(nuevo)
        db.commit()
        db.close()

        self.cargar()

    def eliminar(self):
        row = self.table.currentRow()
        if row < 0:
            return

        codigo = self.table.item(row, 0).text()

        db = SessionLocal()
        obj = db.query(Producto).filter_by(codigo=codigo).first()
        if obj:
            db.delete(obj)
            db.commit()
        db.close()

        self.cargar()