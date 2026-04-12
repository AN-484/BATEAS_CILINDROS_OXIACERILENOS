from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox
from database import SessionLocal
from models import Cilindro, Producto, Propietario

from PySide6.QtWidgets import QDateEdit
from PySide6.QtCore import QDate

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
        #self.propietario.setPlaceholderText("Propietario (LINDE, etc)")
        self.cargar_propietarios()

        self.producto = QComboBox()#*
        self.cargar_productos()#*

        self.fecha_hidro = QDateEdit()
        self.fecha_hidro.setCalendarPopup(True)
        self.fecha_hidro.setDate(QDate.currentDate())

        form.addWidget(self.codigo)
        form.addWidget(self.propietario)
        form.addWidget(self.producto)#*
        form.addWidget(self.fecha_hidro)

        layout.addLayout(form)

        btn_add = QPushButton("Agregar")
        btn_add.clicked.connect(self.agregar)

        btn_del = QPushButton("Eliminar")
        btn_del.clicked.connect(self.eliminar)

        layout.addWidget(btn_add)
        layout.addWidget(btn_del)

        self.table = QTableWidget()
        self.table.setColumnCount(4)#/
        self.table.setHorizontalHeaderLabels(["Código", "Propietario", "Producto", "Fecha Hidrostática"])#*/

        layout.addWidget(self.table)

        self.setLayout(layout)
        self.cargar()

    def cargar(self):
        db = SessionLocal()
        datos = db.query(Cilindro).all()
        datos_propietario= db.query(Propietario).all()
        datos_materia = db.query(Producto).all()
        db.close()
        fecha = ""

        self.table.setRowCount(len(datos))

        for i, d in enumerate(datos):
            if d.fecha_hidrostatica:
                fecha = d.fecha_hidrostatica.strftime("%Y-%m-%d")
            self.table.setItem(i, 0, QTableWidgetItem(d.codigo))
            for j, p in enumerate(datos_propietario):
                if d.propietario == p.codigo:
                    propietar = p.nombre
            self.table.setItem(i, 1, QTableWidgetItem(propietar))
            for k, m in enumerate(datos_materia):
                if d.producto == m.codigo:
                    propietar = m.nombre
            self.table.setItem(i, 2, QTableWidgetItem(propietar))#*
            self.table.setItem(i, 3, QTableWidgetItem(fecha))

    def agregar(self):
        db = SessionLocal()
        db.add(Cilindro(codigo=self.codigo.text(), propietario=self.propietario.currentData(), producto=self.producto.currentData(), fecha_hidrostatica=self.fecha_hidro.date().toPython()))#/
        db.commit()
        db.close()
        self.cargar()

    def eliminar(self):
        row = self.table.currentRow()
        if row < 0: return

        codigo = self.table.item(row, 0).text()
        db = SessionLocal()
        obj = db.query(Cilindro).filter_by(codigo=codigo).first()
        if obj:
            db.delete(obj)
            db.commit()
        db.close()
        self.cargar()

    def cargar_productos(self):
        db = SessionLocal()
        try:
            data = db.query(Producto).all()
            for t in data:
                self.producto.addItem(f"{t.codigo} - {t.nombre}", t.codigo)
        finally:
            db.close()

    def cargar_propietarios(self):
        db = SessionLocal()
        try:
            data = db.query(Propietario).all()
            for p in data:
                self.propietario.addItem(f"{p.codigo} - {p.nombre}", p.codigo)
        finally:
            db.close()