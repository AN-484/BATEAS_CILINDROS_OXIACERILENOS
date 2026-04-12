from PySide6.QtWidgets import *
from database import SessionLocal
from models import EstadoCilindro

class SelectorCilindroUI(QDialog):

    def __init__(self, material, tipo):
        super().__init__()

        self.setWindowTitle("Seleccionar cilindro")

        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(3)

        db = SessionLocal()
        
        try:
            if tipo == "DESPACHO":

                self.table.setHorizontalHeaderLabels(
                    ["Seleccionar", "Cilindro", "Estado"]
                )

                datos = db.query(EstadoCilindro).filter_by(
                    material=material,
                    estado="STOCK"
                ).all()

            else:

                self.table.setHorizontalHeaderLabels(
                    ["Seleccionar", "Cilindro", "Área"]
                )

                datos = db.query(EstadoCilindro).filter_by(
                    material=material,
                    estado="EN CLIENTE"
                ).all()

            self.table.setRowCount(len(datos))

            for i, d in enumerate(datos):

                radio = QRadioButton()

                self.table.setCellWidget(i, 0, radio)
                self.table.setItem(i, 1, QTableWidgetItem(d.cilindro))

                if tipo == "DESPACHO":
                    self.table.setItem(i, 2, QTableWidgetItem(d.estado))
                else:
                    self.table.setItem(i, 2, QTableWidgetItem(d.ubicacion))
        
        finally:
            db.close()

        layout.addWidget(self.table)

        btn = QPushButton("Confirmar")
        btn.clicked.connect(self.confirmar)

        layout.addWidget(btn)

        self.setLayout(layout)

        self.cilindro_seleccionado = None

    def confirmar(self):

        for row in range(self.table.rowCount()):

            radio = self.table.cellWidget(row, 0)

            if radio.isChecked():

                self.cilindro_seleccionado = self.table.item(row, 1).text()

                self.accept()

                return

        QMessageBox.warning(self, "Error", "Seleccione un cilindro")