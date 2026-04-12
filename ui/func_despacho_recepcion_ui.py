from PySide6.QtWidgets import *
from datetime import datetime
from database import SessionLocal
from models import *
from crud import validar_despacho, validar_recepcion, actualizar_estado
from ui.reportes.vale_pdf import generar_vale

from PySide6.QtWidgets import QDateEdit
from PySide6.QtCore import QDate

from ui.selector_cilindro_ui import SelectorCilindroUI

class FuncDespachoRecepcionUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Despacho / Recepción")

        layout = QFormLayout()

        #self.fecha = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        #self.fecha.setReadOnly(True)
        self.fecha = QDateEdit()
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setCalendarPopup(True)  # 🔥 botón calendario

        self.cilindro = QLineEdit()
        self.cilindro.setReadOnly(True)

        ###self.material = QLineEdit()
        ##self.material.setReadOnly(True)

        self.material = QComboBox()
        self.material.currentIndexChanged.connect(self.verificar_stock)
        self.indicador = QLabel("●")
        self.indicador.setStyleSheet("""
        font-size: 20px;
        color: gray;
        """)
        #self.cilindro.currentIndexChanged.connect(self.autocompletar_material)

        self.area = QComboBox()
        self.encargado = QComboBox()
        self.registrado = QComboBox()

        self.responsable = QLineEdit()

        #################################
        '''self.movimiento = QComboBox()
        self.movimiento.addItems(["DESPACHO", "DEVOLUCION"])'''

        self.tipo = "DESPACHO"  # default

        self.btn_despacho = QPushButton("🚚 DESPACHO")
        self.btn_recepcion = QPushButton("📥 DEVOLUCION")

        self.btn_despacho.setStyleSheet("background-color: lightgreen;")
        self.btn_recepcion.setStyleSheet("")

        self.btn_despacho.clicked.connect(self.set_despacho)
        self.btn_recepcion.clicked.connect(self.set_recepcion)
        self.info = QLabel("")


        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.btn_despacho)
        btn_layout.addWidget(self.btn_recepcion)

        layout.addRow("Tipo", btn_layout)
        #############################

        self.btn_seleccionar = QPushButton("Seleccionar cilindro")
        self.btn_seleccionar.setEnabled(False)
        self.btn_seleccionar.clicked.connect(self.abrir_selector)

        self.cargar_datos()

        btn = QPushButton("Guardar")
        btn.clicked.connect(self.guardar)

        layout.addRow("Fecha", self.fecha)
        layout.addRow("Material", self.material)
        layout.addRow("Disponibilidad", self.indicador)
        layout.addRow("", self.btn_seleccionar)
        layout.addRow("Cilindro", self.cilindro)
        layout.addRow("    '----> Info", self.info)
        layout.addRow("Área", self.area)
        #layout.addRow("Movimiento", self.movimiento)
        #layout.addRow("Material", self.material)
        layout.addRow("Encargado", self.encargado)
        layout.addRow("Responsable Área", self.responsable)
        layout.addRow("Registrado por", self.registrado)
        
        # ✅ CHECKBOX PARA GENERAR VALE PDF
        self.generar_vale = QCheckBox("Generar vale PDF")
        self.generar_vale.setChecked(True)  # Por defecto activado
        layout.addRow(self.generar_vale)
       
        layout.addRow(btn)

        self.setLayout(layout)

    def cargar_datos(self):

    # YA NO SE CARGAN CILINDROS AQUÍ
    # Se seleccionan desde el selector

        db = SessionLocal()
        
        try:
            for u in db.query(Ubicacion).all():
                self.area.addItem(u.nombre, u.codigo)

            for u in db.query(Usuario).all():
                self.encargado.addItem(u.nombre, u.codigo)
                self.registrado.addItem(u.nombre, u.codigo)

            for p in db.query(Producto).all():
                self.material.addItem(p.nombre, p.codigo)
        
        finally:
            db.close()

    def guardar(self):
        tipo = self.tipo
        cilindro = self.cilindro.text().strip()
        
        # 🔥 VALIDACIÓN DE CAMPOS VACÍOS
        if not cilindro:
            QMessageBox.warning(self, "Error", "Seleccione un cilindro")
            return
        
        if not self.material.currentData():
            QMessageBox.warning(self, "Error", "Seleccione un material")
            return
        
        if not self.area.currentData():
            QMessageBox.warning(self, "Error", "Seleccione un área")
            return
        
        if not self.encargado.currentData():
            QMessageBox.warning(self, "Error", "Seleccione un encargado")
            return
        
        if not self.responsable.text().strip():
            QMessageBox.warning(self, "Error", "Ingrese responsable del área")
            return
        
        if not self.registrado.currentData():
            QMessageBox.warning(self, "Error", "Seleccione quién registra")
            return

        db = SessionLocal()
        
        try:
            # 🔥 VALIDACIÓN DE ESTADO EN BD
            if tipo == "DESPACHO":
                ok, msg = validar_despacho(db, cilindro)
            else:
                ok, msg = validar_recepcion(db, cilindro)

            if not ok:
                QMessageBox.warning(self, "Error", msg)
                return

            # Obtener propietario del cilindro
            from models import Cilindro
            cilindro_obj = db.query(Cilindro).filter_by(codigo=cilindro).first()
            propietario = cilindro_obj.propietario if cilindro_obj else None

            nuevo = MovimientoDetalle(
                id=str(datetime.now().timestamp()),
                fecha=self.fecha.date().toPython(),
                cilindro=cilindro,
                material=self.material.currentData(),
                area=self.area.currentData(),
                tipo = self.tipo,
                encargado_almacen=self.encargado.currentData(),
                responsable_area=self.responsable.text(),
                registrado_por=self.registrado.currentData()
            )

            db.add(nuevo)

            # 🔥 ESTADO AUTOMÁTICO
            if tipo == "DESPACHO":
                estado = "EN CLIENTE"
                ubicacion = self.area.currentText()
            else:
                estado = "VACIO"
                ubicacion = "ALMACEN"

            actualizar_estado(
                db,
                cilindro,
                estado,
                ubicacion,
                self.material.currentData(),
                self.fecha.date().toPython(),
                propietario
            )

            db.commit()

            # ✅ GENERAR VALE PDF (solo si está marcado el checkbox)
            if self.generar_vale.isChecked():
                data_vale = {
                    "Tipo": tipo,
                    "Cilindro": cilindro,
                    "Material": self.material.currentText(),
                    "Área": self.area.currentText(),
                    "Encargado": self.encargado.currentText(),
                    "Responsable": self.responsable.text(),
                }

                generar_vale(data_vale, f"vale_{cilindro}.pdf", generar_pdf=True)
            else:
                generar_vale({}, "", generar_pdf=False)  # No generar PDF

            QMessageBox.information(self, "OK", "Movimiento registrado correctamente")
            
            # Limpiar campos
            self.limpiar_campos()
        
        finally:
            db.close()
    
    def limpiar_campos(self):
        self.cilindro.clear()
        self.responsable.clear()
        self.material.setCurrentIndex(0)
        self.area.setCurrentIndex(0)
        self.area.setEnabled(True)  # Habilitar área nuevamente
        self.encargado.setCurrentIndex(0)
        self.registrado.setCurrentIndex(0)
        self.fecha.setDate(QDate.currentDate())
        self.indicador.setText("●")
        self.indicador.setStyleSheet("font-size: 20px; color: gray;")
        self.btn_seleccionar.setEnabled(False)
        self.info.setText("")
    
    def autocompletar_material(self):

        codigo = self.cilindro.text().strip()

        if not codigo:
            return

        db = SessionLocal()
        
        try:
            cil = db.query(Cilindro).filter_by(codigo=codigo).first()

            if cil:
                index = self.material.findText(cil.producto)

                if index >= 0:
                    self.material.setCurrentIndex(index)

            estado = db.query(EstadoCilindro).filter_by(
                cilindro=codigo
            ).first()

            if estado:
                self.info.setText(
                    f"Estado: {estado.estado} | Ubicación: {estado.ubicacion}"
                )
                
                # Si es DEVUELVE, autocompletar área y desactivarla
                if self.tipo == "DEVOLUCION" and estado.estado == "EN CLIENTE":
                    # Buscar la ubicación en el ComboBox de área
                    index_area = self.area.findText(estado.ubicacion)
                    if index_area >= 0:
                        self.area.setCurrentIndex(index_area)
                    self.area.setEnabled(False)
                else:
                    # Para DESPACHO, dejar área editable
                    self.area.setEnabled(True)
        
        finally:
            db.close()

    def set_despacho(self):
        self.tipo = "DESPACHO"
        self.btn_despacho.setStyleSheet("background-color: lightgreen;")
        self.btn_recepcion.setStyleSheet("")
        # Limpiar cilindro e info al cambiar tipo
        self.cilindro.clear()
        self.info.setText("")
        self.responsable.clear()
        self.area.setEnabled(True)  # Habilitar para DESPACHO
        self.verificar_stock()

    def set_recepcion(self):
        self.tipo = "DEVOLUCION"
        self.btn_recepcion.setStyleSheet("background-color: lightblue;")
        self.btn_despacho.setStyleSheet("")
        # Limpiar cilindro e info al cambiar tipo
        self.cilindro.clear()
        self.info.setText("")
        self.responsable.clear()
        self.area.setEnabled(True)  # Será deshabilitado si hay cilindro
        self.verificar_stock()
    
    def verificar_stock(self):

        material = self.material.currentData()

        if self.tipo == "DESPACHO":

            db = SessionLocal()
            try:
                disponibles = db.query(EstadoCilindro).filter_by(
                    material=material,
                    estado="STOCK"
                ).count()

                if disponibles > 0:

                    self.indicador.setText("🟢 Disponible")
                    self.indicador.setStyleSheet("color: green; font-weight: bold;")

                    self.btn_seleccionar.setEnabled(True)

                else:

                    self.indicador.setText("🔴 No disponible")
                    self.indicador.setStyleSheet("color: red; font-weight: bold;")

                    self.btn_seleccionar.setEnabled(False)
            finally:
                db.close()

        else:

            # DEVOLUCION - Verificar cilindros en cliente
            db = SessionLocal()
            try:
                disponibles = db.query(EstadoCilindro).filter_by(
                    material=material,
                    estado="EN CLIENTE"
                ).count()

                if disponibles > 0:

                    self.indicador.setText("🟢 Disponible")
                    self.indicador.setStyleSheet("color: green; font-weight: bold;")

                    self.btn_seleccionar.setEnabled(True)

                else:

                    self.indicador.setText("🔴 No disponible")
                    self.indicador.setStyleSheet("color: red; font-weight: bold;")

                    self.btn_seleccionar.setEnabled(False)
            finally:
                db.close()
    
    def abrir_selector(self):

        material = self.material.currentData()

        dialog = SelectorCilindroUI(
            material,
            self.tipo
        )

        if dialog.exec():

            cilindro = dialog.cilindro_seleccionado

            if cilindro:

                self.cilindro.setText(cilindro)

                self.autocompletar_material()