from PySide6.QtWidgets import *
from database import SessionLocal
from models import EntradaSalida, Transportista, Usuario, Cilindro
from ui.components.table_view import TableView
from ui.components.export_excel import exportar_excel

class ReporteEntradasSalidas(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reporte Entradas / Salidas")

        layout = QVBoxLayout()

        # 🔍 filtro
        self.filtro = QLineEdit()
        self.filtro.setPlaceholderText("Buscar guía...")

        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.cargar_datos)

        btn_excel = QPushButton("Exportar Excel")
        btn_excel.clicked.connect(self.exportar)

        self.tabla = TableView()

        layout.addWidget(self.filtro)
        layout.addWidget(btn_buscar)
        layout.addWidget(btn_excel)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

        self.headers = ["Fecha", "Guía", "Cilindro", "F. Hidrostática", "Transportista", "Tipo", "Usuario"]
        self.data = []

        self.cargar_datos()

    def cargar_datos(self):
        db = SessionLocal()
        
        try:
            texto = self.filtro.text()

            query = db.query(EntradaSalida)

            if texto:
                query = query.filter(EntradaSalida.nro_guia.contains(texto))

            resultados = query.all()
            
            # Cargar transportistas y usuarios para búsqueda rápida
            transportistas = {t.codigo: t.nombre for t in db.query(Transportista).all()}
            usuarios = {u.codigo: u.nombre for u in db.query(Usuario).all()}
            cilindros = {c.codigo: c.fecha_hidrostatica for c in db.query(Cilindro).all()}

            self.data = [
                [
                    r.fecha,
                    r.nro_guia,
                    r.cilindro,
                    cilindros.get(r.cilindro),
                    transportistas.get(r.transportista, r.transportista),  # Mostrar nombre
                    r.tipo,
                    usuarios.get(r.registrado_por, r.registrado_por)  # Mostrar nombre
                ]
                for r in resultados
            ]

            self.tabla.cargar_datos(self.headers, self.data)
        
        finally:
            db.close()

    def exportar(self):
        exportar_excel(self.headers, self.data)
        QMessageBox.information(self, "OK", "Exportado a Excel")