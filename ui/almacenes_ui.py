from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit
from database import SessionLocal
from models import Almacen

class AlmacenesUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Almacenes")
        self.resize(600, 400)

        layout = QVBoxLayout()

        form = QHBoxLayout()
        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Código")

        self.nombre = QLineEdit()
        self.nombre.setPlaceholderText("Nombre")

        form.addWidget(self.codigo)
        form.addWidget(self.nombre)

        layout.addLayout(form)

        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.agregar)

        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.eliminar)

        layout.addWidget(btn_add)
        layout.addWidget(btn_del)

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Código", "Nombre"])

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.cargar()

    def cargar(self):
        db = SessionLocal()
        datos = db.query(Almacen).all()
        db.close()

        self.table.setRowCount(len(datos))

        for i, d in enumerate(datos):
            self.table.setItem(i, 0, QTableWidgetItem(d.codigo))
            self.table.setItem(i, 1, QTableWidgetItem(d.nombre))

    def agregar(self):
        db = SessionLocal()
        db.add(Almacen(codigo=self.codigo.text(), nombre=self.nombre.text()))
        db.commit()
        db.close()
        self.cargar()

    def eliminar(self):
        row = self.table.currentRow()
        if row < 0: return

        codigo = self.table.item(row, 0).text()
        db = SessionLocal()
        obj = db.query(Almacen).filter_by(codigo=codigo).first()
        if obj:
            db.delete(obj)
            db.commit()
        db.close()
        self.cargar()