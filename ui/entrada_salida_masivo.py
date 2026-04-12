from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QDate
from datetime import datetime
from database import SessionLocal
from models import Transportista, Usuario, EntradaSalida, Cilindro, Producto, Propietario, EstadoCilindro
from crud import actualizar_estado
from ui.reportes.vale_pdf import generar_vale
from ui.func_entrada_salida_ui_2 import verificar_entrada_de_cilindro, verificar_salida_de_cilindro

class EntradaSalidaMasivoUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Entrada / Salida Masiva")
        self.resize(1000, 600)
        
        layout = QVBoxLayout()
        
        # ✅ SECCIÓN DE CAMPOS COMUNES
        form_layout = QFormLayout()
        
        self.movimiento = QComboBox()
        self.movimiento.addItems(["ENTRADA", "SALIDA"])
        self.movimiento.currentIndexChanged.connect(self.on_movimiento_changed)
        form_layout.addRow("Movimiento:", self.movimiento)
        
        self.guia = QLineEdit()
        self.guia.setPlaceholderText("Número de guía")
        form_layout.addRow("Guía:", self.guia)
        
        self.transportista = QComboBox()
        form_layout.addRow("Transportista:", self.transportista)
        
        self.usuario = QComboBox()
        form_layout.addRow("Usuario (registrado por):", self.usuario)
        
        fecha_layout = QHBoxLayout()
        self.fecha = QDateEdit()
        self.fecha.setDate(QDate.currentDate())
        fecha_layout.addWidget(self.fecha)
        fecha_layout.addStretch()
        form_layout.addRow("Fecha:", fecha_layout)
        
        layout.addLayout(form_layout)
        
        # ✅ SECCIÓN DE TABLA CON CILINDROS
        tabla_label = QLabel("Cilindros a registrar:")
        layout.addWidget(tabla_label)
        
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Código Cilindro", 
            "Propietario", 
            "Material", 
            "Fecha Hidrostática",
            "Eliminar"
        ])
        self.tabla.horizontalHeader().setStretchLastSection(False)
        self.tabla.setColumnWidth(0, 150)
        self.tabla.setColumnWidth(1, 150)
        self.tabla.setColumnWidth(2, 150)
        self.tabla.setColumnWidth(3, 150)
        self.tabla.setColumnWidth(4, 80)
        
        layout.addWidget(self.tabla)
        
        # ✅ CHECKBOX PARA GENERAR VALE PDF
        self.generar_vale = QCheckBox("Generar vale PDF para cada cilindro")
        self.generar_vale.setChecked(True)  # Por defecto activado
        layout.addWidget(self.generar_vale)
        
        # ✅ BOTONES
        botones_layout = QHBoxLayout()
        
        btn_agregar = QPushButton("+ Agregar Cilindro")
        btn_agregar.clicked.connect(self.agregar_fila)
        botones_layout.addWidget(btn_agregar)
        
        botones_layout.addStretch()
        
        btn_guardar = QPushButton("Guardar Todo")
        btn_guardar.setStyleSheet("background-color: #4CAF50; color: white; padding: 5px; font-weight: bold;")
        btn_guardar.clicked.connect(self.guardar_todo)
        botones_layout.addWidget(btn_guardar)
        
        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_todos)
        botones_layout.addWidget(btn_limpiar)
        
        layout.addLayout(botones_layout)
        
        self.setLayout(layout)
        
        # Cargar datos iniciales
        self.cargar_transportistas()
        self.cargar_usuarios()
        
        # Agregar primera fila vacía
        self.agregar_fila()
    
    def cargar_transportistas(self):
        db = SessionLocal()
        try:
            data = db.query(Transportista).all()
            for t in data:
                self.transportista.addItem(f"{t.codigo} - {t.nombre}", t.codigo)
        finally:
            db.close()
    
    def cargar_usuarios(self):
        db = SessionLocal()
        try:
            data = db.query(Usuario).all()
            for u in data:
                self.usuario.addItem(f"{u.codigo} - {u.nombre}", u.codigo)
        finally:
            db.close()
    
    def cargar_productos(self):
        """Retorna lista de productos para combobox"""
        db = SessionLocal()
        try:
            return db.query(Producto).all()
        finally:
            db.close()
    
    def cargar_propietarios(self):
        """Retorna lista de propietarios para combobox"""
        db = SessionLocal()
        try:
            return db.query(Propietario).all()
        finally:
            db.close()
    
    def agregar_fila(self):
        """Agrega una nueva fila a la tabla"""
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)
        
        # Código cilindro
        codigo_input = QLineEdit()
        self.tabla.setCellWidget(row, 0, codigo_input)
        
        # Propietario (ComboBox)
        propietario_combo = QComboBox()
        propietarios = self.cargar_propietarios()
        for p in propietarios:
            propietario_combo.addItem(f"{p.codigo} - {p.nombre}", p.codigo)
        self.tabla.setCellWidget(row, 1, propietario_combo)
        
        # Material/Producto (ComboBox)
        material_combo = QComboBox()
        productos = self.cargar_productos()
        for prod in productos:
            material_combo.addItem(f"{prod.codigo} - {prod.nombre}", prod.codigo)
        self.tabla.setCellWidget(row, 2, material_combo)
        
        # Fecha Hidrostática
        fecha_hidro = QDateEdit()
        fecha_hidro.setDate(QDate.currentDate())
        self.tabla.setCellWidget(row, 3, fecha_hidro)
        
        # Botón Eliminar
        btn_eliminar = QPushButton("✕")
        btn_eliminar.setMaximumWidth(60)
        btn_eliminar.clicked.connect(lambda: self.eliminar_fila(row))
        self.tabla.setCellWidget(row, 4, btn_eliminar)
    
    def eliminar_fila(self, row):
        """Elimina una fila de la tabla"""
        self.tabla.removeRow(row)
    
    def on_movimiento_changed(self):
        """Se ejecuta cuando cambia el movimiento (ENTRADA/SALIDA)"""
        pass
    
    def guardar_todo(self):
        """Valida y guarda todos los cilindros"""
        
        # Validar campos comunes
        if not self.guia.text().strip():
            QMessageBox.warning(self, "Error", "Ingrese número de guía")
            return
        
        if not self.transportista.currentData():
            QMessageBox.warning(self, "Error", "Seleccione transportista")
            return
        
        if not self.usuario.currentData():
            QMessageBox.warning(self, "Error", "Seleccione usuario")
            return
        
        if self.tabla.rowCount() == 0:
            QMessageBox.warning(self, "Error", "Agregue al menos un cilindro")
            return
        
        movimiento = self.movimiento.currentText()
        guia = self.guia.text()
        transportista = self.transportista.currentData()
        usuario = self.usuario.currentData()
        fecha = self.fecha.date().toPython()
        
        # Validar que haya al menos una fila con datos
        cilindros_validos = []
        for row in range(self.tabla.rowCount()):
            codigo = self.tabla.cellWidget(row, 0).text().strip()
            if codigo:
                propietario = self.tabla.cellWidget(row, 1).currentData()
                material = self.tabla.cellWidget(row, 2).currentData()
                fecha_hidro = self.tabla.cellWidget(row, 3).date().toPython()
                
                if not propietario or not material:
                    QMessageBox.warning(self, "Error", f"Fila {row+1}: Seleccione propietario y material")
                    return
                
                cilindros_validos.append({
                    "codigo": codigo,
                    "propietario": propietario,
                    "material": material,
                    "fecha_hidro": fecha_hidro
                })
        
        if not cilindros_validos:
            QMessageBox.warning(self, "Error", "Ingrese al menos un código de cilindro")
            return
        
        # Guardar todos
        db = SessionLocal()
        try:
            registrados = 0
            errores = []
            
            for cilindro_data in cilindros_validos:
                try:
                    codigo = cilindro_data["codigo"]
                    propietario = cilindro_data["propietario"]
                    material = cilindro_data["material"]
                    fecha_hidro = cilindro_data["fecha_hidro"]
                    
                    # Verificar si existe
                    cilindro_existente = db.query(Cilindro).filter_by(codigo=codigo).first()
                    
                    # Validar estado
                    estado_actual = db.query(EstadoCilindro).filter_by(cilindro=codigo).first()
                    
                    if movimiento == "ENTRADA":
                        if not verificar_entrada_de_cilindro(movimiento, estado_actual, None):
                            errores.append(f"{codigo}: No cumple validación de ENTRADA")
                            continue
                    elif movimiento == "SALIDA":
                        if not verificar_salida_de_cilindro(movimiento, estado_actual, None):
                            errores.append(f"{codigo}: No cumple validación de SALIDA")
                            continue
                    
                    # Crear cilindro si no existe
                    if not cilindro_existente:
                        nuevo_cilindro = Cilindro(
                            codigo=codigo,
                            propietario=propietario,
                            producto=material,
                            fecha_hidrostatica=fecha_hidro
                        )
                        db.add(nuevo_cilindro)
                    
                    # Registrar movimiento
                    nuevo = EntradaSalida(
                        id=str(datetime.now().timestamp()),
                        fecha=fecha,
                        nro_guia=guia,
                        cilindro=codigo,
                        producto=material,
                        cod_transportista=transportista,
                        transportista=transportista,
                        tipo=movimiento,
                        registrado_por=usuario
                    )
                    db.add(nuevo)
                    
                    # Actualizar estado
                    if movimiento == "ENTRADA":
                        estado = "STOCK"
                        ubicacion = "ALMACEN"
                    else:
                        estado = "EN PROVEEDOR"
                        ubicacion = "PROVEEDOR"
                    
                    actualizar_estado(
                        db,
                        codigo,
                        estado,
                        ubicacion,
                        material,
                        fecha,
                        propietario
                    )
                    
                    registrados += 1
                    
                except Exception as e:
                    errores.append(f"{cilindro_data['codigo']}: {str(e)}")
            
            # Commit una sola vez
            db.commit()
            
            # ✅ GENERAR VALES PDF (uno por cada cilindro registrado)
            if registrados > 0 and self.generar_vale.isChecked():
                for cilindro_data in cilindros_validos:
                    try:
                        data_vale = {
                            "Tipo": movimiento,
                            "Fecha": fecha.strftime("%d/%m/%Y"),
                            "Guía": guia,
                            "Cilindro": cilindro_data["codigo"],
                            "Transportista": self.transportista.currentText(),
                            "Registrado por": self.usuario.currentText()
                        }
                        
                        filename = f"vale_{cilindro_data['codigo']}_{fecha.strftime('%Y%m%d')}.pdf"
                        generar_vale(data_vale, filename, generar_pdf=True)
                    except Exception as e:
                        errores.append(f"Vale {cilindro_data['codigo']}: Error generando PDF - {str(e)}")
            
            # Mostrar resultado
            msg = f"✅ {registrados} cilindro(s) registrado(s)"
            if self.generar_vale.isChecked() and registrados > 0:
                msg += f"\n\n📄 {registrados} vale(s) PDF generado(s)"
            if errores:
                msg += f"\n\n⚠️ Errores:\n" + "\n".join(errores)
            
            QMessageBox.information(self, "Resultado", msg)
            
            if registrados > 0:
                self.limpiar_todos()
        
        except Exception as e:
            db.rollback()
            QMessageBox.critical(self, "Error", f"Error en la transacción: {str(e)}")
        finally:
            db.close()
    
    def limpiar_todos(self):
        """Limpia todos los campos"""
        self.guia.clear()
        self.transportista.setCurrentIndex(0)
        self.usuario.setCurrentIndex(0)
        self.movimiento.setCurrentIndex(0)
        self.fecha.setDate(QDate.currentDate())
        
        # Limpiar tabla
        self.tabla.setRowCount(0)
        self.agregar_fila()
