from PySide6.QtWidgets import *
from datetime import datetime

from crud import actualizar_estado
from ui.reportes.vale_pdf import generar_vale
from session import get_usuario
from ui.func_entrada_salida_ui_2 import *

from PySide6.QtWidgets import QDateEdit
from PySide6.QtCore import QDate

from supabase_api import (
    listar_transportistas,
    listar_productos,
    listar_propietarios,
    obtener_cilindro_por_codigo,
    obtener_estado_cilindro_por_codigo,
    crear_cilindro,
    crear_entrada_salida
)


class _FilaAPI:
    def __init__(self, data):
        if not data:
            return
        for k, v in data.items():
            setattr(self, k, v)


class FuncEntradaSalidaUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ingreso / Recarga")

        layout = QFormLayout()

        self.fecha = QDateEdit()
        self.fecha.setDate(QDate.currentDate())
        self.fecha.setCalendarPopup(True)

        self.guia = QLineEdit()
        self.guia.setPlaceholderText("Número de Guia, Ejemplo: G001-12345")

        self.nro_documento = QLineEdit()
        self.nro_documento.setPlaceholderText("Número de documento")
        self.nro_documento.setMaxLength(10)

        self.cilindro = QLineEdit()
        self.cilindro.setPlaceholderText("Código de Cilindro existente o nuevo (presione ENTER para verificar)")
        self.cilindro.editingFinished.connect(self.verificar_cilindro)

        self.propietario = QComboBox()
        self.cargar_propietarios()

        self.producto = QComboBox()
        self.cargar_productos()

        self.fecha_hidro = QDateEdit()
        self.fecha_hidro.setCalendarPopup(True)
        self.fecha_hidro.setDate(QDate.currentDate())

        self.transportista = QComboBox()
        self.cargar_transportistas()

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

        self.movimiento = QComboBox()
        self.movimiento.addItems(["INGRESO", "RECARGA"])

        self.generar_vale = QCheckBox("Generar vale PDF")
        self.generar_vale.setChecked(False)

        btn = QPushButton("Guardar")
        btn.clicked.connect(self.guardar)

        layout.addRow("Fecha", self.fecha)
        layout.addRow("Cod. Cilindro", self.cilindro)
        layout.addRow("Cod. Propietario", self.propietario)
        layout.addRow("Cod. Producto", self.producto)
        layout.addRow("Fecha Hidrostática", self.fecha_hidro)
        layout.addRow("Guía", self.guia)
        layout.addRow("N° Documento", self.nro_documento)
        layout.addRow("Transportista", self.transportista)
        layout.addRow("Movimiento", self.movimiento)
        layout.addRow("Registrado por", self.usuario)
        layout.addRow(self.generar_vale)
        layout.addRow(btn)

        self.setLayout(layout)

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
        self.producto.clear()
        data = listar_productos()

        for p in sorted(data, key=lambda x: x.get("codigo", "")):
            self.producto.addItem(
                f"{p.get('codigo', '')} - {p.get('nombre', '')}",
                p.get("codigo", "")
            )

    def cargar_propietarios(self):
        self.propietario.clear()
        data = listar_propietarios()

        for p in sorted(data, key=lambda x: x.get("codigo", "")):
            self.propietario.addItem(
                f"{p.get('codigo', '')} - {p.get('nombre', '')}",
                p.get("codigo", "")
            )

    def guardar(self):
        codigo_cilindro = self.cilindro.text().strip()

        if not codigo_cilindro:
            QMessageBox.warning(self, "Error", "Ingrese código de cilindro")
            return

        movimiento = self.movimiento.currentText()

        if not self.guia.text().strip():
            QMessageBox.warning(self, "Error", "Ingrese número de guía")
            return

        if not self.nro_documento.text().strip():
            QMessageBox.warning(self, "Error", "Ingrese número de documento")
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

        try:
            cilindro_existente = obtener_cilindro_por_codigo(codigo_cilindro)
            estado_actual_dict = obtener_estado_cilindro_por_codigo(codigo_cilindro)
            estado_actual = _FilaAPI(estado_actual_dict) if estado_actual_dict else None

            if movimiento == "INGRESO":
                if not verificar_entrada_de_cilindro(movimiento, estado_actual, self):
                    return
            elif movimiento == "RECARGA":
                if not verificar_salida_de_cilindro(movimiento, estado_actual, self):
                    return

            if not cilindro_existente:
                resp_cil = crear_cilindro({
                    "codigo": codigo_cilindro,
                    "propietario": self.propietario.currentData(),
                    "producto": self.producto.currentData(),
                    "fecha_hidrostatica": self.fecha_hidro.date().toPython().strftime("%Y-%m-%d"),
                    "nuevo": "SI"
                })

                if resp_cil is None:
                    QMessageBox.warning(self, "Error", "No se pudo registrar el cilindro")
                    return

            usuario_actual = get_usuario()

            resp_mov = crear_entrada_salida({
                "id": str(datetime.now().timestamp()),
                "fecha": self.fecha.date().toPython().strftime("%Y-%m-%d"),
                "nro_guia": self.guia.text().strip(),
                "nro_documento": self.nro_documento.text().strip(),
                "cilindro": codigo_cilindro,
                "producto": self.producto.currentData(),
                "cod_transportista": self.transportista.currentData(),
                "transportista": self.transportista.currentData(),
                "tipo": movimiento,
                "registrado_por": usuario_actual.codigo
            })

            if resp_mov is None:
                QMessageBox.warning(self, "Error", "No se pudo registrar el movimiento")
                return

            if movimiento == "INGRESO":
                estado = "STOCK"
                ubicacion = "ALMACEN"
            else:
                estado = "EN PROVEEDOR"
                ubicacion = "PROVEEDOR"

            resp_estado = actualizar_estado(
                None,
                codigo_cilindro,
                estado,
                ubicacion,
                self.producto.currentData(),
                self.fecha.date().toPython(),
                self.propietario.currentData()
            )

            if resp_estado is None:
                QMessageBox.warning(self, "Error", "No se pudo actualizar el estado del cilindro")
                return

            if self.generar_vale.isChecked():
                data_vale = {
                    "Tipo": movimiento,
                    "Guía": self.guia.text(),
                    "Transportista": self.transportista.currentText(),
                    "Registrado por": usuario_actual.nombre
                }
                generar_vale(data_vale, f"vale_{self.guia.text()}.pdf", generar_pdf=True)
            else:
                generar_vale({}, "", generar_pdf=False)

            QMessageBox.information(self, "OK", "Registro guardado")
            self.limpiar_campos()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error: {str(e)}")

    def limpiar_campos(self):
        self.cilindro.clear()
        self.guia.clear()
        self.nro_documento.clear()
        self.propietario.setCurrentIndex(0)
        self.producto.setCurrentIndex(0)
        self.transportista.setCurrentIndex(0)

        usuario_actual = get_usuario()
        if usuario_actual:
            self.usuario.setText(f"{usuario_actual.nombre}")

        self.movimiento.setCurrentIndex(0)
        self.fecha.setDate(QDate.currentDate())
        self.fecha_hidro.setDate(QDate.currentDate())

        self.propietario.setEnabled(True)
        self.producto.setEnabled(True)
        self.fecha_hidro.setEnabled(True)

    def verificar_cilindro(self):
        codigo = self.cilindro.text().strip()

        if not codigo:
            return

        try:
            c = obtener_cilindro_por_codigo(codigo)

            if c:
                propietario_codigo = c.get("propietario")
                producto_codigo = c.get("producto")

                if propietario_codigo:
                    index_prop = self.propietario.findData(propietario_codigo)
                    if index_prop >= 0:
                        self.propietario.setCurrentIndex(index_prop)

                if producto_codigo:
                    index_prod = self.producto.findData(producto_codigo)
                    if index_prod >= 0:
                        self.producto.setCurrentIndex(index_prod)

                self.propietario.setEnabled(False)
                self.producto.setEnabled(False)

                fecha_hidro = c.get("fecha_hidrostatica")
                if fecha_hidro:
                    try:
                        fecha_qt = QDate.fromString(str(fecha_hidro), "yyyy-MM-dd")
                        if fecha_qt.isValid():
                            self.fecha_hidro.setDate(fecha_qt)
                    except Exception:
                        pass

                self.fecha_hidro.setEnabled(False)

            else:
                self.propietario.setEnabled(True)
                self.producto.setEnabled(True)
                self.fecha_hidro.setEnabled(True)

        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo verificar el cilindro: {str(e)}")