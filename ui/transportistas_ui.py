from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit
from database import SessionLocal
from models import Transportista

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
        db = SessionLocal()
        datos = db.query(Transportista).all()
        db.close()

        self.table.setRowCount(len(datos))

        for i, d in enumerate(datos):
            self.table.setItem(i, 0, QTableWidgetItem(d.codigo))
            self.table.setItem(i, 1, QTableWidgetItem(d.nombre))
            self.table.setItem(i, 2, QTableWidgetItem(d.ruc))

    def agregar(self):
        db = SessionLocal()

        nuevo = Transportista(
            codigo=self.codigo.text(),
            nombre=self.nombre.text(),
            ruc=self.ruc.text()
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
        obj = db.query(Transportista).filter_by(codigo=codigo).first()
        if obj:
            db.delete(obj)
            db.commit()
        db.close()

        self.cargar()