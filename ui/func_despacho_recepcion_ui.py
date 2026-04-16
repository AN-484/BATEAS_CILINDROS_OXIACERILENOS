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


class FuncDespachoRecepcionUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Despacho / Recepción")

        layout = QFormLayout()

        self.fecha = QDateEdit()
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setCalendarPopup(True)

        self.cilindro = QLineEdit()
        self.cilindro.setReadOnly(True)

        self.material = QComboBox()
        self.material.currentIndexChanged.connect(self.verificar_stock)

        self.indicador = QLabel("●")
        self.indicador.setStyleSheet("""
        font-size: 20px;
        color: gray;
        """)

        self.area = QComboBox()
        self.encargado = QComboBox()

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

        self.responsable = QLineEdit()

        self.tipo = "DESPACHO"

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
        layout.addRow("    '--------> Info", self.info)
        layout.addRow("Área", self.area)
        layout.addRow("Autorizado por", self.encargado)
        layout.addRow("Usuario que recoge:", self.responsable)
        layout.addRow("Registrado por", self.registrado)

        self.generar_vale = QCheckBox("Generar vale PDF")
        self.generar_vale.setChecked(False)
        layout.addRow(self.generar_vale)

        layout.addRow(btn)

        self.setLayout(layout)

    def cargar_datos(self):
        self.area.clear()
        self.encargado.clear()
        self.material.clear()

        for u in sorted(listar_ubicaciones(), key=lambda x: x.get("codigo", "")):
            self.area.addItem(u.get("nombre", ""), u.get("codigo", ""))

        aux = 0
        for u in sorted(listar_usuarios(), key=lambda x: x.get("codigo", "")):
            aux += 1
            self.encargado.addItem(u.get("nombre", ""), u.get("codigo", ""))
            if aux == 2:
                break

        for p in sorted(listar_productos(), key=lambda x: x.get("codigo", "")):
            self.material.addItem(p.get("nombre", ""), p.get("codigo", ""))

    def guardar(self):
        tipo = self.tipo
        cilindro = self.cilindro.text().strip()

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

        try:
            if tipo == "DESPACHO":
                ok, msg = validar_despacho(None, cilindro)
            else:
                ok, msg = validar_recepcion(None, cilindro)

            if not ok:
                QMessageBox.warning(self, "Error", msg)
                return

            cilindro_obj = obtener_cilindro_por_codigo(cilindro)
            propietario = cilindro_obj.get("propietario") if cilindro_obj else None

            usuario_actual = get_usuario()

            resp = crear_movimiento_detalle({
                "id": str(datetime.now().timestamp()),
                "fecha": self.fecha.date().toPython().strftime("%Y-%m-%d"),
                "cilindro": cilindro,
                "material": self.material.currentData(),
                "area": self.area.currentData(),
                "tipo": self.tipo,
                "encargado_almacen": self.encargado.currentData(),
                "responsable_area": self.responsable.text().strip(),
                "registrado_por": usuario_actual.codigo
            })

            if resp is None:
                QMessageBox.warning(self, "Error", "No se pudo registrar el movimiento")
                return

            if tipo == "DESPACHO":
                estado = "EN CLIENTE"
                ubicacion = self.area.currentText()
                actualizar_cilindro(None, cilindro)
            else:
                estado = "VACIO"
                ubicacion = "ALMACEN"

            resp_estado = actualizar_estado(
                None,
                cilindro,
                estado,
                ubicacion,
                self.material.currentData(),
                self.fecha.date().toPython(),
                propietario
            )

            if resp_estado is None:
                QMessageBox.warning(self, "Error", "No se pudo actualizar el estado del cilindro")
                return

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
                generar_vale({}, "", generar_pdf=False)

            QMessageBox.information(self, "OK", "Movimiento registrado correctamente")
            self.limpiar_campos()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error: {str(e)}")

    def limpiar_campos(self):
        self.cilindro.clear()
        self.responsable.clear()
        self.material.setCurrentIndex(0)
        self.area.setCurrentIndex(0)
        self.area.setEnabled(True)
        self.encargado.setCurrentIndex(0)

        usuario_actual = get_usuario()
        if usuario_actual:
            self.registrado.setText(f"{usuario_actual.nombre}")

        self.fecha.setDate(QDate.currentDate())
        self.indicador.setText("●")
        self.indicador.setStyleSheet("font-size: 20px; color: gray;")
        self.btn_seleccionar.setEnabled(False)
        self.info.setText("")

    def autocompletar_material(self):
        codigo = self.cilindro.text().strip()

        if not codigo:
            return

        try:
            cil = obtener_cilindro_por_codigo(codigo)

            if cil:
                index = self.material.findData(cil.get("producto"))
                if index >= 0:
                    self.material.setCurrentIndex(index)

            estado = obtener_estado_cilindro_por_codigo(codigo)

            if estado:
                self.info.setText(
                    f"Estado: {estado.get('estado', '')} | Ubicación: {estado.get('ubicacion', '')}"
                )

                if self.tipo == "DEVOLUCION" and estado.get("estado") == "EN CLIENTE":
                    index_area = self.area.findText(estado.get("ubicacion", ""))
                    if index_area >= 0:
                        self.area.setCurrentIndex(index_area)
                    self.area.setEnabled(False)
                else:
                    self.area.setEnabled(True)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar información del cilindro: {str(e)}")

    def set_despacho(self):
        self.tipo = "DESPACHO"
        self.btn_despacho.setStyleSheet("background-color: lightgreen;")
        self.btn_recepcion.setStyleSheet("")
        self.cilindro.clear()
        self.info.setText("")
        self.responsable.clear()
        self.area.setEnabled(True)
        self.verificar_stock()

    def set_recepcion(self):
        self.tipo = "DEVOLUCION"
        self.btn_recepcion.setStyleSheet("background-color: lightblue;")
        self.btn_despacho.setStyleSheet("")
        self.cilindro.clear()
        self.info.setText("")
        self.responsable.clear()
        self.area.setEnabled(True)
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
                datos = obtener_registros(
                    "estado_cilindros",
                    filtros={
                        "material": f"eq.{material}",
                        "estado": "eq.STOCK"
                    }
                )
            else:
                datos = obtener_registros(
                    "estado_cilindros",
                    filtros={
                        "material": f"eq.{material}",
                        "estado": "eq.EN CLIENTE"
                    }
                )

            disponibles = len(datos)

            if disponibles > 0:
                self.indicador.setText("🟢 Disponible")
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
            QMessageBox.warning(self, "Error", f"No se pudo verificar disponibilidad: {str(e)}")

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