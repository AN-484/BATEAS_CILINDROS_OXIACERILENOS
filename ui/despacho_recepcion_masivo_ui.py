from PySide6.QtWidgets import *
from datetime import datetime

from crud import validar_despacho, validar_recepcion, actualizar_estado, actualizar_cilindro
from ui.reportes.vale_pdf import generar_vale
from PySide6.QtWidgets import QDateEdit
from PySide6.QtCore import QDate

from ui.selector_cilindro_ui import SelectorCilindroUI
from session import get_usuario

from supabase_api import (
    listar_ubicaciones,
    listar_usuarios,
    listar_productos,
    obtener_cilindro_por_codigo,
    obtener_estado_cilindro_por_codigo,
    crear_movimiento_detalle,
    obtener_registros
)


class DespachoRecepcionMasivoUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Despacho / Devolución Masiva")

        self.productos_map = {}

        self.area_devolucion_codigo = None
        self.area_devolucion_nombre = None

        layout = QVBoxLayout()

        form = QFormLayout()

        self.fecha = QDateEdit()
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setCalendarPopup(True)

        self.tipo = "DESPACHO"

        self.btn_despacho = QPushButton("🚚 DESPACHO")
        self.btn_recepcion = QPushButton("📥 DEVOLUCION")

        self.btn_despacho.setStyleSheet("background-color: lightgreen;")
        self.btn_recepcion.setStyleSheet("")

        self.btn_despacho.clicked.connect(self.set_despacho)
        self.btn_recepcion.clicked.connect(self.set_recepcion)

        tipo_layout = QHBoxLayout()
        tipo_layout.addWidget(self.btn_despacho)
        tipo_layout.addWidget(self.btn_recepcion)

        self.material = QComboBox()
        self.material.currentIndexChanged.connect(self.verificar_stock)

        self.indicador = QLabel("●")
        self.indicador.setStyleSheet("font-size: 20px; color: gray;")

        self.btn_seleccionar = QPushButton("+ Agregar cilindro")
        self.btn_seleccionar.setEnabled(False)
        self.btn_seleccionar.clicked.connect(self.abrir_selector)

        self.area = QComboBox()
        self.encargado = QComboBox()

        self.responsable = QLineEdit()
        self.responsable.setPlaceholderText("Usuario que recoge / devuelve")

        self.registrado = QLineEdit()
        self.registrado.setReadOnly(True)

        usuario_actual = get_usuario()
        if usuario_actual:
            self.registrado.setText(f"{usuario_actual.nombre}")

        self.registrado.setStyleSheet("""
            QLineEdit {
                background-color: #E9ECEF;
                color: #495057;
                border: 1px solid #CED4DA;
                font-weight: bold;
            }
        """)

        self.cargar_datos()

        form.addRow("Tipo", tipo_layout)
        form.addRow("Fecha", self.fecha)
        form.addRow("Material a buscar", self.material)
        form.addRow("Disponibilidad", self.indicador)
        form.addRow("", self.btn_seleccionar)
        form.addRow("Área", self.area)
        form.addRow("Autorizado por", self.encargado)
        form.addRow("Usuario que recoge/devuelve", self.responsable)
        form.addRow("Registrado por", self.registrado)

        layout.addLayout(form)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels([
            "Cilindro",
            "Material",
            "Estado actual",
            "Ubicación actual",
            "Eliminar"
        ])

        self.tabla.setColumnWidth(0, 140)
        self.tabla.setColumnWidth(1, 320)
        self.tabla.setColumnWidth(2, 140)
        self.tabla.setColumnWidth(3, 180)
        self.tabla.setColumnWidth(4, 80)

        layout.addWidget(QLabel("Cilindros seleccionados:"))
        layout.addWidget(self.tabla)

        self.generar_vale = QCheckBox("Generar vale PDF por cada cilindro")
        self.generar_vale.setChecked(False)
        layout.addWidget(self.generar_vale)

        botones = QHBoxLayout()

        btn_guardar = QPushButton("Guardar todo")
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 6px;
            }
        """)
        btn_guardar.clicked.connect(self.guardar)

        btn_limpiar = QPushButton("Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_campos)

        botones.addStretch()
        botones.addWidget(btn_guardar)
        botones.addWidget(btn_limpiar)

        layout.addLayout(botones)

        self.setLayout(layout)

    def cargar_datos(self):
        self.area.clear()
        self.encargado.clear()
        self.material.clear()
        self.productos_map.clear()

        for u in sorted(listar_ubicaciones(), key=lambda x: x.get("codigo", "")):
            self.area.addItem(u.get("nombre", ""), u.get("codigo", ""))

        aux = 0
        for u in sorted(listar_usuarios(), key=lambda x: x.get("codigo", "")):
            aux += 1
            self.encargado.addItem(u.get("nombre", ""), u.get("codigo", ""))
            if aux == 2:
                break

        for p in sorted(listar_productos(), key=lambda x: x.get("nombre", "")):
            codigo = p.get("codigo", "")
            nombre = p.get("nombre", "")

            self.productos_map[codigo] = nombre
            self.material.addItem(nombre, codigo)

    def agregar_cilindro_tabla(self, cilindro, material_codigo, estado_actual="", ubicacion_actual=""):
        for row in range(self.tabla.rowCount()):
            if self.tabla.item(row, 0) and self.tabla.item(row, 0).text() == cilindro:
                QMessageBox.warning(self, "Duplicado", f"El cilindro {cilindro} ya fue agregado")
                return

        row = self.tabla.rowCount()
        self.tabla.insertRow(row)

        material_nombre = self.productos_map.get(material_codigo, material_codigo)

        self.tabla.setItem(row, 0, QTableWidgetItem(cilindro))
        self.tabla.setItem(row, 1, QTableWidgetItem(material_nombre))
        self.tabla.setItem(row, 2, QTableWidgetItem(estado_actual))
        self.tabla.setItem(row, 3, QTableWidgetItem(ubicacion_actual))

        self.tabla.item(row, 1).setData(1000, material_codigo)

        btn_eliminar = QPushButton("✕")
        btn_eliminar.setMaximumWidth(60)
        btn_eliminar.clicked.connect(lambda: self.eliminar_fila_por_boton(btn_eliminar))
        self.tabla.setCellWidget(row, 4, btn_eliminar)

    def eliminar_fila_por_boton(self, boton):
        for row in range(self.tabla.rowCount()):
            if self.tabla.cellWidget(row, 4) == boton:
                self.tabla.removeRow(row)
                break

        # Si estamos en DEVOLUCION y ya no quedan cilindros,
        # se libera nuevamente el área
        if self.tipo == "DEVOLUCION" and self.tabla.rowCount() == 0:
            self.area_devolucion_codigo = None
            self.area_devolucion_nombre = None

            self.area.setEnabled(True)
            self.area.setCurrentIndex(0)

    def guardar(self):
        tipo = self.tipo

        if self.tabla.rowCount() == 0:
            QMessageBox.warning(self, "Error", "Agregue al menos un cilindro")
            return

        if not self.area.currentData():
            QMessageBox.warning(self, "Error", "Seleccione un área")
            return

        if not self.encargado.currentData():
            QMessageBox.warning(self, "Error", "Seleccione un encargado")
            return

        if not self.responsable.text().strip():
            QMessageBox.warning(self, "Error", "Ingrese usuario que recoge/devuelve")
            return

        usuario_actual = get_usuario()
        fecha = self.fecha.date().toPython()

        registrados = 0
        errores = []

        for row in range(self.tabla.rowCount()):
            try:
                cilindro = self.tabla.item(row, 0).text()
                material = self.tabla.item(row, 1).data(1000)

                if tipo == "DESPACHO":
                    ok, msg = validar_despacho(None, cilindro)
                else:
                    ok, msg = validar_recepcion(None, cilindro)

                if not ok:
                    errores.append(f"{cilindro}: {msg}")
                    continue

                cilindro_obj = obtener_cilindro_por_codigo(cilindro)
                propietario = cilindro_obj.get("propietario") if cilindro_obj else None

                resp = crear_movimiento_detalle({
                    "id": f"{datetime.now().timestamp()}_{row}",
                    "fecha": fecha.strftime("%Y-%m-%d"),
                    "cilindro": cilindro,
                    "material": material,
                    "area": self.area.currentData(),
                    "tipo": tipo,
                    "encargado_almacen": self.encargado.currentData(),
                    "responsable_area": self.responsable.text().strip(),
                    "registrado_por": usuario_actual.codigo
                })

                if resp is None:
                    errores.append(f"{cilindro}: No se pudo registrar movimiento")
                    continue

                if tipo == "DESPACHO":
                    nuevo_estado = "EN CLIENTE"
                    ubicacion = self.area.currentText()
                    actualizar_cilindro(None, cilindro)
                else:
                    nuevo_estado = "VACIO"
                    ubicacion = "ALMACEN"

                resp_estado = actualizar_estado(
                    None,
                    cilindro,
                    nuevo_estado,
                    ubicacion,
                    material,
                    fecha,
                    propietario
                )

                if resp_estado is None:
                    errores.append(f"{cilindro}: No se pudo actualizar estado")
                    continue

                if self.generar_vale.isChecked():
                    data_vale = {
                        "Tipo": tipo,
                        "Cilindro": cilindro,
                        "Material": self.productos_map.get(material, material),
                        "Área": self.area.currentText(),
                        "Encargado": self.encargado.currentText(),
                        "Responsable": self.responsable.text(),
                        "Registrado por": usuario_actual.nombre
                    }

                    generar_vale(
                        data_vale,
                        f"vale_{cilindro}_{fecha.strftime('%Y%m%d')}.pdf",
                        generar_pdf=True
                    )

                registrados += 1

            except Exception as e:
                errores.append(f"Fila {row + 1}: {str(e)}")

        msg = f"✅ {registrados} cilindro(s) registrado(s) correctamente"

        if errores:
            msg += "\n\n⚠️ Errores:\n" + "\n".join(errores)

        QMessageBox.information(self, "Resultado", msg)

        if registrados > 0:
            self.limpiar_campos()

    def limpiar_campos(self):
        self.responsable.clear()
        self.material.setCurrentIndex(0)

        # ✅ Resetear control de área en DEVOLUCIÓN
        self.area_devolucion_codigo = None
        self.area_devolucion_nombre = None

        self.area.setCurrentIndex(0)
        self.area.setEnabled(True)

        self.encargado.setCurrentIndex(0)
        self.fecha.setDate(QDate.currentDate())
        self.tabla.setRowCount(0)

        usuario_actual = get_usuario()
        if usuario_actual:
            self.registrado.setText(f"{usuario_actual.nombre}")

        self.indicador.setText("●")
        self.indicador.setStyleSheet("font-size: 20px; color: gray;")
        self.verificar_stock()

    def set_despacho(self):
        self.tipo = "DESPACHO"
        self.btn_despacho.setStyleSheet("background-color: lightgreen;")
        self.btn_recepcion.setStyleSheet("")
        self.tabla.setRowCount(0)

        self.area_devolucion_codigo = None
        self.area_devolucion_nombre = None

        self.area.setEnabled(True)
        self.area.setCurrentIndex(0)

        self.verificar_stock()

    def set_recepcion(self):
        self.tipo = "DEVOLUCION"
        self.btn_recepcion.setStyleSheet("background-color: lightblue;")
        self.btn_despacho.setStyleSheet("")
        self.tabla.setRowCount(0)

        self.area_devolucion_codigo = None
        self.area_devolucion_nombre = None

        self.area.setEnabled(True)
        self.area.setCurrentIndex(0)

        self.verificar_stock()

    def verificar_stock(self):
        material = self.material.currentData()

        if not material:
            self.indicador.setText("🔴 No disponible")
            self.indicador.setStyleSheet("color: red; font-weight: bold;")
            self.btn_seleccionar.setEnabled(False)
            return

        try:
            if self.tipo == "DESPACHO":
                estado_buscar = "STOCK"
            else:
                estado_buscar = "EN CLIENTE"

            datos = obtener_registros(
                "estado_cilindros",
                filtros={
                    "material": f"eq.{material}",
                    "estado": f"eq.{estado_buscar}"
                }
            )

            disponibles = len(datos)

            if disponibles > 0:
                self.indicador.setText(f"🟢 Disponible ({disponibles})")
                self.indicador.setStyleSheet("color: green; font-weight: bold;")
                self.btn_seleccionar.setEnabled(True)
            else:
                self.indicador.setText("🔴 No disponible")
                self.indicador.setStyleSheet("color: red; font-weight: bold;")
                self.btn_seleccionar.setEnabled(False)

        except Exception as e:
            self.indicador.setText("🔴 Error")
            self.indicador.setStyleSheet("color: red; font-weight: bold;")
            self.btn_seleccionar.setEnabled(False)
            QMessageBox.warning(
                self,
                "Error",
                f"No se pudo verificar disponibilidad: {str(e)}"
            )

    def abrir_selector(self):
        material = self.material.currentData()

        dialog = SelectorCilindroUI(
            material,
            self.tipo
        )

        if dialog.exec():
            cilindro = dialog.cilindro_seleccionado

            if cilindro:
                estado = obtener_estado_cilindro_por_codigo(cilindro)
                cilindro_obj = obtener_cilindro_por_codigo(cilindro)

                if not estado:
                    QMessageBox.warning(
                        self,
                        "Error",
                        "No se encontró el estado del cilindro seleccionado"
                    )
                    return

                material_codigo = material

                if cilindro_obj and cilindro_obj.get("producto"):
                    material_codigo = cilindro_obj.get("producto")

                estado_actual = estado.get("estado", "")
                ubicacion_actual = estado.get("ubicacion", "")

                # =====================================================
                # VALIDACIÓN ESPECIAL PARA DEVOLUCIÓN
                # =====================================================
                if self.tipo == "DEVOLUCION":

                    if not ubicacion_actual:
                        QMessageBox.warning(
                            self,
                            "Error",
                            f"El cilindro {cilindro} no tiene área/ubicación registrada"
                        )
                        return

                    # Primer cilindro: fija el área de devolución
                    if self.area_devolucion_nombre is None:
                        self.area_devolucion_nombre = ubicacion_actual

                        index_area = self.area.findText(ubicacion_actual)

                        if index_area >= 0:
                            self.area.setCurrentIndex(index_area)
                            self.area_devolucion_codigo = self.area.currentData()
                        else:
                            QMessageBox.warning(
                                self,
                                "Error",
                                f"El área '{ubicacion_actual}' no existe en la lista de áreas"
                            )
                            return

                        self.area.setEnabled(False)

                    # Siguientes cilindros: deben ser de la misma área
                    else:
                        if ubicacion_actual != self.area_devolucion_nombre:
                            QMessageBox.warning(
                                self,
                                "No permitido",
                                f"El cilindro {cilindro} pertenece al área:\n\n"
                                f"{ubicacion_actual}\n\n"
                                f"Pero esta devolución corresponde al área:\n\n"
                                f"{self.area_devolucion_nombre}"
                            )
                            return

                self.agregar_cilindro_tabla(
                    cilindro,
                    material_codigo,
                    estado_actual,
                    ubicacion_actual
                )