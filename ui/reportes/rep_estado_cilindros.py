from PySide6.QtWidgets import *
from database import SessionLocal
from models import EstadoCilindro, Producto, Propietario, Cilindro  
from ui.components.table_view import TableView
from ui.components.export_excel import exportar_excel
from datetime import datetime, timedelta

class ReporteEstadoCilindros(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Estado de Cilindros")

        layout = QVBoxLayout()

        btn_excel = QPushButton("Exportar Excel")
        btn_excel.clicked.connect(self.exportar)

        self.tabla = TableView()

        layout.addWidget(btn_excel)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

        self.headers = ["Cilindro", "Propietario", "Material", "F. Hidrostática",   "Estado", "Fecha", "Ubicación"]
        self.data = []

        self.cargar()

    def cargar(self):
        db = SessionLocal()
        
        try:
            resultados = db.query(EstadoCilindro).all()
            
            # Cargar productos y propietarios para búsqueda rápida
            productos = {p.codigo: p.nombre for p in db.query(Producto).all()}
            propietarios = {p.codigo: p.nombre for p in db.query(Propietario).all()}
            cilindros = {c.codigo: c.fecha_hidrostatica for c in db.query(Cilindro).all()}

            self.data = [
                [
                    r.cilindro,
                    propietarios.get(r.propietario, r.propietario) if r.propietario else "N/A",  # Mostrar nombre del propietario
                    productos.get(r.material, r.material),  # Mostrar nombre del material
                    cilindros.get(r.cilindro),
                    r.estado,
                    r.fecha_mov,
                    r.ubicacion
                ]
                for r in resultados
            ]

            self.tabla.cargar_datos(self.headers, self.data)

            # 🚨 ALERTA AUTOMÁTICA
            alertas = [
                d for d in resultados
                if d.estado == "EN CLIENTE" and d.fecha_mov and (datetime.now().date() - d.fecha_mov).days > 30
            ]

            if alertas:
                QMessageBox.warning(self, "Alerta", f"{len(alertas)} cilindros llevan más de 30 días en cliente")
        
        finally:
            db.close()

    # ✅ ESTE ES EL MÉTODO QUE FALTABA
    def exportar(self):
        exportar_excel(self.headers, self.data, "estado_cilindros.xlsx")
        QMessageBox.information(self, "OK", "Exportado a Excel")