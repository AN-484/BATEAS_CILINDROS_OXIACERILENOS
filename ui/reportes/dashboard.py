from PySide6.QtWidgets import *
from database import SessionLocal
from models import EstadoCilindro

class DashboardUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard Logístico")

        layout = QVBoxLayout()

        self.lbl_total = QLabel()
        self.lbl_disponible = QLabel()
        self.lbl_cliente = QLabel()
        self.lbl_proveedor = QLabel()
        self.lbl_vacio = QLabel()
        self.lbl_LINDE = QLabel()
        self.lbl_BATEAS = QLabel()

        btn_refresh = QPushButton("Actualizar")
        btn_refresh.clicked.connect(self.cargar)

        layout.addWidget(self.lbl_total)
        layout.addWidget(self.lbl_disponible)
        layout.addWidget(self.lbl_cliente)
        layout.addWidget(self.lbl_proveedor)
        layout.addWidget(self.lbl_vacio)
        layout.addWidget(self.lbl_LINDE)
        layout.addWidget(self.lbl_BATEAS)
        layout.addWidget(btn_refresh)

        self.setLayout(layout)

        self.cargar()

    def cargar(self):
        db = SessionLocal()
        
        try:
            data = db.query(EstadoCilindro).all()

            total = len(data)
            disponible = sum(1 for d in data if d.estado == "STOCK")
            cliente = sum(1 for d in data if d.estado == "EN CLIENTE")
            proveedor = sum(1 for d in data if d.estado == "EN PROVEEDOR")
            vacio = sum(1 for d in data if d.estado == "VACIO")
            linde = sum(1 for d in data if d.propietario == "PP02" and d.estado != "EN PROVEEDOR")
            bateas = sum(1 for d in data if d.propietario == "PP01" and d.estado != "EN PROVEEDOR")

            self.lbl_total.setText(f"Total cilindros: {total}")
            self.lbl_disponible.setText(f"Disponibles: {disponible}")
            self.lbl_cliente.setText(f"En cliente: {cliente}")
            self.lbl_proveedor.setText(f"En proveedor: {proveedor}")
            self.lbl_vacio.setText(f"Vacíos: {vacio}")
            self.lbl_LINDE.setText(f"Cilindros Actuales de LINDE: {linde}")
            self.lbl_BATEAS.setText(f"Cilindros Actuales de BATEAS: {bateas}")
        
        finally:
            db.close()