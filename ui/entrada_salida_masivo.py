from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QDate
from datetime import datetime

from crud import actualizar_estado
from ui.reportes.vale_pdf import generar_vale
from ui.func_entrada_salida_ui_2 import verificar_entrada_de_cilindro, verificar_salida_de_cilindro
from session import get_usuario

from supabase_api import (
    listar_transportistas,
    listar_productos,
    listar_propietarios,
    obtener_cilindro_por_codigo,
    obtener_estado_cilindro_por_codigo,
    crear_cilindro,
    crear_entrada_salida
)


class EntradaSalidaMasivoUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ingreso / Recarga Masiva")
        self.resize(1000, 600)

        layout = QVBoxLayout()

        form_layout = QFormLayout()

        self.movimiento = QComboBox()
        self.movimiento.addItems(["INGRESO", "RECARGA"])
        self.movimiento.currentIndexChanged.connect(self.on_movimiento_changed)
        form_layout.addRow("Movimiento:", self.movimiento)

        self.guia = QLineEdit()
        self.guia.setPlaceholderText("Número de guía")
        form_layout.addRow("Guía:", self.guia)

        self.nro_documento = QLineEdit()
        self.nro_documento.setPlaceholderText("Número de documento")
        self.nro_documento.setMaxLength(10)
        form_layout.addRow("N° Documento:", self.nro_documento)

        self.transportista = QComboBox()
        form_layout.addRow("Transportista:", self.transportista)

        self.usuario = QLineEdit()
        self.usuario.setReadOnly(True)

        usuario_actual = get_usuario()
        if usuario_actual:
            self.usuario.setText(f"{usuario_actual.nombre}")

        self.usuario.setStyleSheet("""
            QLineEdit {
                background-color: #E9ECEF;
                color: #495057;
                border: 1px solid #CED4DA;
                font-weight: bold;
            }
        """)

        form_layout.addRow("Usuario (registrado por):", self.usuario)

        fecha_layout = QHBoxLayout()
        self.fecha = QDateEdit()
        self.fecha.setDate(QDate.currentDate())
        fecha_layout.addWidget(self.fecha)
        fecha_layout.addStretch()
        form_layout.addRow("Fecha:", fecha_layout)

        layout.addLayout(form_layout)

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

        self.generar_vale = QCheckBox("Generar vale PDF para cada cilindro")
        self.generar_vale.setChecked(False)
        layout.addWidget(self.generar_vale)

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

        self.cargar_transportistas()
        self.agregar_fila()

    def cargar_transportistas(self):
        self.transportista.clear()
        data = listar_transportistas()
        for t in sorted(data, key=lambda x: x.get("codigo", "")):
            self.transportista.addItem(
                f"{t.get('codigo', '')} - {t.get('nombre', '')}",
                t.get("codigo", "")
            )

    def cargar_usuarios(self):
        pass

    def cargar_productos(self):
        return sorted(listar_productos(), key=lambda x: x.get("codigo", ""))

    def cargar_propietarios(self):
        return sorted(listar_propietarios(), key=lambda x: x.get("codigo", ""))

    def agregar_fila(self):
        row = self.tabla.rowCount()
        self.tabla.insertRow(row)

        codigo_input = QLineEdit()
        codigo_input.editingFinished.connect(
            lambda r=row: self.verificar_cilindro_fila(r)
        )
        self.tabla.setCellWidget(row, 0, codigo_input)

        propietario_combo = QComboBox()
        propietarios = self.cargar_propietarios()
        for p in propietarios:
            propietario_combo.addItem(
                f"{p.get('codigo', '')} - {p.get('nombre', '')}",
                p.get("codigo", "")
            )
        self.tabla.setCellWidget(row, 1, propietario_combo)

        material_combo = QComboBox()
        productos = self.cargar_productos()
        for prod in productos:
            material_combo.addItem(
                f"{prod.get('codigo', '')} - {prod.get('nombre', '')}",
                prod.get("codigo", "")
            )
        self.tabla.setCellWidget(row, 2, material_combo)

        fecha_hidro = QDateEdit()
        fecha_hidro.setCalendarPopup(True)
        fecha_hidro.setDate(QDate.currentDate())
        self.tabla.setCellWidget(row, 3, fecha_hidro)

        btn_eliminar = QPushButton("✕")
        btn_eliminar.setMaximumWidth(60)
        btn_eliminar.clicked.connect(lambda: self.eliminar_fila_por_boton(btn_eliminar))
        self.tabla.setCellWidget(row, 4, btn_eliminar)

    def eliminar_fila_por_boton(self, boton):
        for row in range(self.tabla.rowCount()):
            if self.tabla.cellWidget(row, 4) == boton:
                self.tabla.removeRow(row)
                return

    def eliminar_fila(self, row):
        self.tabla.removeRow(row)

    def on_movimiento_changed(self):
        pass

    def guardar_todo(self):
        if not self.guia.text().strip():
            QMessageBox.warning(self, "Error", "Ingrese número de guía")
            return

        if not self.nro_documento.text().strip():
            QMessageBox.warning(self, "Error", "Ingrese número de documento")
            return

        if not self.transportista.currentData():
            QMessageBox.warning(self, "Error", "Seleccione transportista")
            return

        if self.tabla.rowCount() == 0:
            QMessageBox.warning(self, "Error", "Agregue al menos un cilindro")
            return

        movimiento = self.movimiento.currentText()
        guia = self.guia.text().strip()
        nro_documento = self.nro_documento.text().strip()
        transportista = self.transportista.currentData()
        usuario_actual = get_usuario()
        usuario = usuario_actual.codigo
        fecha = self.fecha.date().toPython()

        cilindros_validos = []
        for row in range(self.tabla.rowCount()):
            codigo_widget = self.tabla.cellWidget(row, 0)
            if not codigo_widget:
                continue

            codigo = codigo_widget.text().strip()
            if codigo:
                propietario = self.tabla.cellWidget(row, 1).currentData()
                material = self.tabla.cellWidget(row, 2).currentData()
                fecha_hidro = self.tabla.cellWidget(row, 3).date().toPython()

                if not propietario or not material:
                    QMessageBox.warning(self, "Error", f"Fila {row + 1}: Seleccione propietario y material")
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

        try:
            registrados = 0
            errores = []

            for cilindro_data in cilindros_validos:
                try:
                    codigo = cilindro_data["codigo"]
                    propietario = cilindro_data["propietario"]
                    material = cilindro_data["material"]
                    fecha_hidro = cilindro_data["fecha_hidro"]

                    cilindro_existente = obtener_cilindro_por_codigo(codigo)
                    estado_actual = obtener_estado_cilindro_por_codigo(codigo)

                    if movimiento == "INGRESO":
                        if not verificar_entrada_de_cilindro(movimiento, estado_actual, self):
                            errores.append(f"{codigo}: No cumple validación de INGRESO")
                            continue
                    elif movimiento == "RECARGA":
                        if not verificar_salida_de_cilindro(movimiento, estado_actual, self):
                            errores.append(f"{codigo}: No cumple validación de RECARGA")
                            continue

                    if not cilindro_existente:
                        resp_cil = crear_cilindro({
                            "codigo": codigo,
                            "propietario": propietario,
                            "producto": material,
                            "fecha_hidrostatica": fecha_hidro.strftime("%Y-%m-%d"),
                            "nuevo": "SI"
                        })
                        if resp_cil is None:
                            errores.append(f"{codigo}: No se pudo crear el cilindro")
                            continue

                    resp_mov = crear_entrada_salida({
                        "id": str(datetime.now().timestamp()),
                        "fecha": fecha.strftime("%Y-%m-%d"),
                        "nro_guia": guia,
                        "nro_documento": nro_documento,
                        "cilindro": codigo,
                        "producto": material,
                        "cod_transportista": transportista,
                        "transportista": transportista,
                        "tipo": movimiento,
                        "registrado_por": usuario
                    })

                    if resp_mov is None:
                        errores.append(f"{codigo}: No se pudo registrar el movimiento")
                        continue

                    if movimiento == "INGRESO":
                        estado = "STOCK"
                        ubicacion = "ALMACEN"
                    else:
                        estado = "EN PROVEEDOR"
                        ubicacion = "PROVEEDOR"

                    resp_estado = actualizar_estado(
                        None,
                        codigo,
                        estado,
                        ubicacion,
                        material,
                        fecha,
                        propietario
                    )

                    if resp_estado is None:
                        errores.append(f"{codigo}: No se pudo actualizar el estado")
                        continue

                    registrados += 1

                except Exception as e:
                    errores.append(f"{cilindro_data['codigo']}: {str(e)}")

            if registrados > 0 and self.generar_vale.isChecked():
                for cilindro_data in cilindros_validos:
                    try:
                        data_vale = {
                            "Tipo": movimiento,
                            "Fecha": fecha.strftime("%d/%m/%Y"),
                            "Guía": guia,
                            "Cilindro": cilindro_data["codigo"],
                            "Transportista": self.transportista.currentText(),
                            "Registrado por": usuario_actual.nombre
                        }

                        filename = f"vale_{cilindro_data['codigo']}_{fecha.strftime('%Y%m%d')}.pdf"
                        generar_vale(data_vale, filename, generar_pdf=True)
                    except Exception as e:
                        errores.append(f"Vale {cilindro_data['codigo']}: Error generando PDF - {str(e)}")

            msg = f"✅ {registrados} cilindro(s) registrado(s)"
            if self.generar_vale.isChecked() and registrados > 0:
                msg += f"\n\n📄 {registrados} vale(s) PDF generado(s)"
            if errores:
                msg += f"\n\n⚠️ Errores:\n" + "\n".join(errores)

            QMessageBox.information(self, "Resultado", msg)

            if registrados > 0:
                self.limpiar_todos()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en la transacción: {str(e)}")

    def limpiar_todos(self):
        self.guia.clear()
        self.nro_documento.clear()
        self.transportista.setCurrentIndex(0)

        usuario_actual = get_usuario()
        if usuario_actual:
            self.usuario.setText(f"{usuario_actual.nombre}")

        self.movimiento.setCurrentIndex(0)
        self.fecha.setDate(QDate.currentDate())

        self.tabla.setRowCount(0)
        self.agregar_fila()

    def verificar_cilindro_fila(self, row):
        codigo_widget = self.tabla.cellWidget(row, 0)

        if not codigo_widget:
            return

        codigo = codigo_widget.text().strip()

        if not codigo:
            return

        try:
            c = obtener_cilindro_por_codigo(codigo)

            propietario_combo = self.tabla.cellWidget(row, 1)
            material_combo = self.tabla.cellWidget(row, 2)
            fecha_hidro_widget = self.tabla.cellWidget(row, 3)

            if c:
                propietario_codigo = c.get("propietario")
                producto_codigo = c.get("producto")

                if propietario_codigo:
                    index_prop = propietario_combo.findData(propietario_codigo)
                    if index_prop >= 0:
                        propietario_combo.setCurrentIndex(index_prop)

                if producto_codigo:
                    index_prod = material_combo.findData(producto_codigo)
                    if index_prod >= 0:
                        material_combo.setCurrentIndex(index_prod)

                fecha_hidro = c.get("fecha_hidrostatica")
                if fecha_hidro:
                    fecha_qt = QDate.fromString(str(fecha_hidro), "yyyy-MM-dd")
                    if fecha_qt.isValid():
                        fecha_hidro_widget.setDate(fecha_qt)

                propietario_combo.setEnabled(False)
                material_combo.setEnabled(False)
                fecha_hidro_widget.setEnabled(False)

            else:
                propietario_combo.setEnabled(True)
                material_combo.setEnabled(True)
                fecha_hidro_widget.setEnabled(True)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo verificar el cilindro: {str(e)}")