from PySide6.QtWidgets import *
from datetime import datetime
from database import SessionLocal
from models import Transportista, Usuario, EntradaSalida, Cilindro, Producto, Propietario, EstadoCilindro
from crud import actualizar_estado
from ui.reportes.vale_pdf import generar_vale
from session import get_usuario

from ui.func_entrada_salida_ui_2 import *

from PySide6.QtWidgets import QDateEdit
from PySide6.QtCore import QDate

class FuncEntradaSalidaUI(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Ingreso / Recarga")

        layout = QFormLayout()

        #self.fecha = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        #self.fecha.setReadOnly(True)
        self.fecha = QDateEdit()
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setCalendarPopup(True)  # 🔥 botón calendario

        self.guia = QLineEdit()

        # 🔥 Cilindro New o desde BD
        self.cilindro = QLineEdit()
        self.cilindro.editingFinished.connect(self.verificar_cilindro)
        

        # 🔥 Propietario desde BD
        self.propietario = QComboBox()
        self.cargar_propietarios()

        # 🔥 Producto desde BD
        self.producto = QComboBox()
        self.cargar_productos()

        #fecha hisrostatica
        self.fecha_hidro = QDateEdit()
        self.fecha_hidro.setCalendarPopup(True)
        self.fecha_hidro.setDate(QDate.currentDate())

        # 🔥 Transportistas desde BD
        self.transportista = QComboBox()
        self.cargar_transportistas()

        # 🔥 Usuarios desde BD
        ##self.usuario = QComboBox()
        ##self.cargar_usuarios()
        self.usuario = QLineEdit()
        self.usuario.setReadOnly(True)

        usuario_actual = get_usuario()

        if usuario_actual:
            self.usuario.setText(
                #f"{usuario_actual.codigo} - {usuario_actual.nombre}"
                f"{usuario_actual.nombre}"
            )
        self.usuario.setStyleSheet("""
            QLineEdit {
                background-color: #E9ECEF;
                color: #495057;
                border: 1px solid #CED4DA;
                font-weight: bold;
            }
        """)

        self.movimiento = QComboBox()
        self.movimiento.addItems(["INGRESO", "RECARGA"])

        # ✅ CHECKBOX PARA GENERAR VALE PDF
        self.generar_vale = QCheckBox("Generar vale PDF")
        self.generar_vale.setChecked(True)  # Por defecto activado

        btn = QPushButton("Guardar")
        btn.clicked.connect(self.guardar)

        layout.addRow("Fecha", self.fecha)
        layout.addRow("Cod. Cilindro", self.cilindro)
        layout.addRow("Cod. Propietario", self.propietario)
        layout.addRow("Cod. Producto", self.producto)
        layout.addRow("Fecha Hidrostática", self.fecha_hidro)
        layout.addRow("Guía", self.guia)
        layout.addRow("Transportista", self.transportista)
        layout.addRow("Movimiento", self.movimiento)
        layout.addRow("Registrado por", self.usuario)
        layout.addRow(self.generar_vale)  # ✅ Checkbox antes del botón
        layout.addRow(btn)

        self.setLayout(layout)

    def cargar_transportistas(self):
        db = SessionLocal()
        try:
            data = db.query(Transportista).all()
            for t in data:
                self.transportista.addItem(f"{t.codigo} - {t.nombre}", t.codigo)
        finally:
            db.close()

    def cargar_usuarios(self):#####no es necesario ahora
        db = SessionLocal()
        try:
            data = db.query(Usuario).all()
            for u in data:
                self.usuario.addItem(f"{u.codigo} - {u.nombre}", u.codigo)
        finally:
            db.close()

    def cargar_productos(self):
        db = SessionLocal()
        try:
            data = db.query(Producto).all()
            for p in data:
                self.producto.addItem(f"{p.codigo} - {p.nombre}", p.codigo)
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


    def guardar(self):
        codigo_cilindro = self.cilindro.text().strip()

        if not codigo_cilindro:
            QMessageBox.warning(self, "Error", "Ingrese código de cilindro")
            return

        movimiento = self.movimiento.currentText()

        # 🔥 VALIDACIÓN DE CAMPOS VACÍOS
        if not self.guia.text().strip():
            QMessageBox.warning(self, "Error", "Ingrese número de guía")
            return
        
        if not self.propietario.currentData():
            QMessageBox.warning(self, "Error", "Seleccione propietario")
            return
        
        if not self.producto.currentData():
            QMessageBox.warning(self, "Error", "Seleccione producto")
            return
        
        if not self.transportista.currentData():
            QMessageBox.warning(self, "Error", "Seleccione transportista")
            return
        
        #if not self.usuario.currentData():
        #    QMessageBox.warning(self, "Error", "Seleccione usuario (registrado por)")
        #    return

        db = SessionLocal()
        try:
            # verificar si existe cilindro
            cilindro_existente = db.query(Cilindro).filter_by(codigo=codigo_cilindro).first()

            # 🔥 VALIDACIÓN DE ESTADO
            estado_actual = db.query(EstadoCilindro).filter_by(cilindro=codigo_cilindro).first()

            if movimiento == "INGRESO":
                if not verificar_entrada_de_cilindro(movimiento, estado_actual, self):
                    return
            elif movimiento == "RECARGA":
                if not verificar_salida_de_cilindro(movimiento, estado_actual, self):
                    return

            if not cilindro_existente:
                # crear cilindro si no existe
                nuevo_cilindro = Cilindro(
                    codigo=codigo_cilindro,
                    propietario=self.propietario.currentData(), 
                    producto=self.producto.currentData(),
                    fecha_hidrostatica=self.fecha_hidro.date().toPython()
                )
                db.add(nuevo_cilindro)

            # registrar movimiento
            usuario_actual = get_usuario()
            nuevo = EntradaSalida(
                id=str(datetime.now().timestamp()),
                #fecha=datetime.now(),
                fecha=self.fecha.date().toPython(),
                nro_guia=self.guia.text(),
                cilindro=codigo_cilindro,
                producto=self.producto.currentData(),   
                cod_transportista=self.transportista.currentData(),
                transportista=self.transportista.currentData(),
                tipo=movimiento,
                registrado_por = usuario_actual.codigo
            )

            db.add(nuevo)

            # estado correcto
            if movimiento == "INGRESO":
                estado = "STOCK"
                ubicacion = "ALMACEN"
            else:
                estado = "EN PROVEEDOR"
                ubicacion = "PROVEEDOR"

            actualizar_estado(
                db,
                codigo_cilindro,
                estado,
                ubicacion,
                self.producto.currentData(),
                self.fecha.date().toPython(),
                self.propietario.currentData()
            )

            db.commit()

            # generar vale (solo si está marcado el checkbox)
            if self.generar_vale.isChecked():
                usuario_actual = get_usuario()
                data_vale = {
                    "Tipo": movimiento,
                    "Guía": self.guia.text(),
                    "Transportista": self.transportista.currentText(),
                    "Registrado por": usuario_actual.nombre
                }

                generar_vale(data_vale, f"vale_{self.guia.text()}.pdf", generar_pdf=True)
            else:
                generar_vale({}, "", generar_pdf=False)  # No generar PDF

            QMessageBox.information(self, "OK", "Registro guardado")
            
            # Limpiar campos
            self.limpiar_campos()
        finally:
            db.close()
    
    def limpiar_campos(self):
        self.cilindro.clear()
        self.guia.clear()
        self.propietario.setCurrentIndex(0)
        self.producto.setCurrentIndex(0)
        self.transportista.setCurrentIndex(0)
        usuario_actual = get_usuario()
        if usuario_actual:
            self.usuario.setText(
                f"{usuario_actual.codigo} - {usuario_actual.nombre}"
            )
        self.movimiento.setCurrentIndex(0)
        self.fecha.setDate(QDate.currentDate())
        self.fecha_hidro.setDate(QDate.currentDate())
        
        # Habilitar campos
        self.propietario.setEnabled(True)
        self.producto.setEnabled(True)
        self.fecha_hidro.setEnabled(True)
    
    def verificar_cilindro(self):
        codigo = self.cilindro.text().strip()

        if not codigo:
            return

        db = SessionLocal()
        try:
            c = db.query(Cilindro).filter_by(codigo=codigo).first()

            if c:
                propie = db.query(Propietario).filter_by(codigo=c.propietario).first()
                # autocompletar
                if propie:
                    index_prop = self.propietario.findData(propie.codigo)
                    if index_prop >= 0:
                        self.propietario.setCurrentIndex(index_prop)

                index_prod = self.producto.findData(c.producto)
                if index_prod >= 0:
                    self.producto.setCurrentIndex(index_prod)

                # bloquear
                self.propietario.setEnabled(False)
                self.producto.setEnabled(False)

                # bloquear fecha si existe
                if c.fecha_hidrostatica:
                    self.fecha_hidro.setDate(
                        QDate(
                            c.fecha_hidrostatica.year,
                            c.fecha_hidrostatica.month,
                            c.fecha_hidrostatica.day
                        )
                    )
                self.fecha_hidro.setEnabled(False)

            else:
                # habilitar si es nuevo
                self.propietario.setEnabled(True)
                self.producto.setEnabled(True)
                self.fecha_hidro.setEnabled(True)
        finally:
            db.close()