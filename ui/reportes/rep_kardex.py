from PySide6.QtWidgets import *
from database import SessionLocal
from models import MovimientoDetalle, Ubicacion, Producto
from ui.components.table_view import TableView

class KardexUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kardex por Cilindro")

        layout = QVBoxLayout()

        self.codigo = QLineEdit()
        self.codigo.setPlaceholderText("Código de cilindro")

        btn = QPushButton("Buscar")
        btn.clicked.connect(self.buscar)

        self.tabla = TableView()

        layout.addWidget(self.codigo)
        layout.addWidget(btn)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

    def buscar(self):
        db = SessionLocal()
        
        try:
            codigo = self.codigo.text()

            data = db.query(MovimientoDetalle).filter_by(cilindro=codigo).all()

            # Crear diccionarios de mapeo
            areas = {a.codigo: a.nombre for a in db.query(Ubicacion).all()}
            materiales = {p.codigo: p.nombre for p in db.query(Producto).all()}

            headers = ["Fecha", "Tipo", "Área", "Material"]

            rows = [
                [d.fecha, d.tipo, areas.get(d.area, d.area), materiales.get(d.material, d.material)]
                for d in data
            ]

            self.tabla.cargar_datos(headers, rows)
        
        finally:
            db.close()