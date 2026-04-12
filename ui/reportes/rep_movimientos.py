from PySide6.QtWidgets import *
from database import SessionLocal
from models import MovimientoDetalle, Producto, Ubicacion, Usuario
from ui.components.table_view import TableView
from ui.components.export_excel import exportar_excel

class ReporteMovimientos(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Búsqueda Avanzada - Movimientos")

        layout = QVBoxLayout()

        # 🔎 FILTROS - Primera fila
        filtros1 = QHBoxLayout()

        self.f_cilindro = QLineEdit()
        self.f_cilindro.setPlaceholderText("Cilindro")

        self.f_area = QComboBox()
        self.f_area.addItem("TODOS")
        self.cargar_areas()

        self.f_tipo = QComboBox()
        self.f_tipo.addItem("TODOS")
        self.f_tipo.addItems(["DESPACHO", "RECEPCION"])

        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar)

        filtros1.addWidget(QLabel("Cilindro:"))
        filtros1.addWidget(self.f_cilindro)
        filtros1.addWidget(QLabel("Área:"))
        filtros1.addWidget(self.f_area)
        filtros1.addWidget(QLabel("Tipo:"))
        filtros1.addWidget(self.f_tipo)
        filtros1.addWidget(btn_buscar)

        # 🔎 FILTROS - Segunda fila
        filtros2 = QHBoxLayout()

        self.f_material = QComboBox()
        self.f_material.addItem("TODOS")
        self.cargar_materiales()

        filtros2.addWidget(QLabel("Material:"))
        filtros2.addWidget(self.f_material)
        filtros2.addStretch()

        # 📊 TABLA
        self.tabla = TableView()

        btn_excel = QPushButton("Exportar Excel")
        btn_excel.clicked.connect(self.exportar)

        layout.addLayout(filtros1)
        layout.addLayout(filtros2)
        layout.addWidget(btn_excel)
        layout.addWidget(self.tabla)

        self.setLayout(layout)

        self.headers = ["Fecha", "Cilindro", "Material", "Área", "Tipo", "Encargado", "Responsable", "Registrado por"]
        self.data = []

    def cargar_materiales(self):
        db = SessionLocal()
        try:
            for p in db.query(Producto).all():
                self.f_material.addItem(p.nombre, p.codigo)
        finally:
            db.close()

    def cargar_areas(self):
        db = SessionLocal()
        try:
            for u in db.query(Ubicacion).all():
                self.f_area.addItem(u.nombre, u.codigo)
        finally:
            db.close()

    def buscar(self):
        db = SessionLocal()
        
        try:
            query = db.query(MovimientoDetalle)

            if self.f_cilindro.text():
                query = query.filter(MovimientoDetalle.cilindro.contains(self.f_cilindro.text()))

            if self.f_material.currentText() != "TODOS":
                query = query.filter(MovimientoDetalle.material == self.f_material.currentData())

            if self.f_area.currentText() != "TODOS":
                query = query.filter(MovimientoDetalle.area == self.f_area.currentData())

            if self.f_tipo.currentText() != "TODOS":
                query = query.filter(MovimientoDetalle.tipo == self.f_tipo.currentText())

            resultados = query.all()
            
            # Cargar productos, ubicaciones y usuarios para búsqueda rápida
            productos = {p.codigo: p.nombre for p in db.query(Producto).all()}
            ubicaciones = {u.codigo: u.nombre for u in db.query(Ubicacion).all()}
            usuarios = {u.codigo: u.nombre for u in db.query(Usuario).all()}


            self.data = [
                [
                    r.fecha,
                    r.cilindro,
                    productos.get(r.material, r.material),  # Mostrar nombre
                    ubicaciones.get(r.area, r.area),  # Mostrar nombre
                    r.tipo,
                    usuarios.get(r.encargado_almacen, r.encargado_almacen),  # Mostrar nombre
                    r.responsable_area,
                    usuarios.get(r.registrado_por, r.registrado_por)  # Mostrar nombre
                ]
                for r in resultados
            ]

            self.tabla.cargar_datos(self.headers, self.data)
        
        finally:
            db.close()

    def exportar(self):
        exportar_excel(self.headers, self.data)
        QMessageBox.information(self, "OK", "Exportado")