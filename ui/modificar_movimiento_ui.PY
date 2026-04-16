from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QDate

from supabase_api import (
    listar_entradas_salidas,
    listar_transportistas,
    listar_productos,
    listar_propietarios,
    listar_usuarios,
    listar_cilindros,
    obtener_cilindro_por_codigo,
    obtener_estado_cilindro_por_codigo,
    actualizar_registro,
    eliminar_registro
)


class ModificarMovimientoUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Modificar / Eliminar Movimiento")

        layout = QVBoxLayout()

        filtros = QHBoxLayout()

        self.input_guia = QLineEdit()
        self.input_guia.setPlaceholderText("N° Guía")

        self.input_documento = QLineEdit()
        self.input_documento.setPlaceholderText("N° Documento")

        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self.buscar)

        filtros.addWidget(QLabel("Guía:"))
        filtros.addWidget(self.input_guia)
        filtros.addWidget(QLabel("Documento:"))
        filtros.addWidget(self.input_documento)
        filtros.addWidget(btn_buscar)

        layout.addLayout(filtros)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(10)
        self.tabla.setHorizontalHeaderLabels([
            "Sel",
            "Fecha",
            "Cilindro",
            "Producto",
            "Fecha Hidrostática",
            "Tipo",
            "Guía",
            "Documento",
            "Transportista",
            "Usuario"
        ])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addWidget(self.tabla)

        botones = QHBoxLayout()

        btn_editar = QPushButton("Editar")
        btn_eliminar = QPushButton("Eliminar")

        btn_editar.clicked.connect(self.editar_movimiento)
        btn_eliminar.clicked.connect(self.eliminar_movimiento)

        botones.addWidget(btn_editar)
        botones.addWidget(btn_eliminar)

        layout.addLayout(botones)

        self.setLayout(layout)

    def buscar(self):
        guia = self.input_guia.text().strip()
        documento = self.input_documento.text().strip()

        if not guia and not documento:
            QMessageBox.warning(self, "Error", "Ingrese guía o documento")
            return

        try:
            movimientos = listar_entradas_salidas()

            if guia:
                movimientos = [m for m in movimientos if m.get("nro_guia", "") == guia]

            if documento:
                movimientos = [m for m in movimientos if m.get("nro_documento", "") == documento]

            cilindros = {c.get("codigo"): c for c in listar_cilindros()}
            usuarios = {u.get("codigo"): u for u in listar_usuarios()}
            transportistas = {t.get("codigo"): t for t in listar_transportistas()}
            productos = {p.get("codigo"): p for p in listar_productos()}

            self.tabla.setRowCount(0)

            for row, mov in enumerate(movimientos):
                cil = cilindros.get(mov.get("cilindro"))
                usr = usuarios.get(mov.get("registrado_por"))
                trans = transportistas.get(mov.get("transportista"))
                prod = productos.get(cil.get("producto")) if cil else None

                self.tabla.insertRow(row)

                chk = QCheckBox()
                chk.setProperty("id_mov", mov.get("id"))
                self.tabla.setCellWidget(row, 0, chk)

                self.tabla.setItem(row, 1, QTableWidgetItem(str(mov.get("fecha", ""))))
                self.tabla.setItem(row, 2, QTableWidgetItem(mov.get("cilindro", "")))
                self.tabla.setItem(row, 3, QTableWidgetItem(prod.get("nombre", "") if prod else ""))
                self.tabla.setItem(
                    row,
                    4,
                    QTableWidgetItem(str(cil.get("fecha_hidrostatica", "")) if cil else "")
                )
                self.tabla.setItem(row, 5, QTableWidgetItem(mov.get("tipo", "")))
                self.tabla.setItem(row, 6, QTableWidgetItem(mov.get("nro_guia", "")))
                self.tabla.setItem(row, 7, QTableWidgetItem(mov.get("nro_documento", "")))
                self.tabla.setItem(row, 8, QTableWidgetItem(trans.get("nombre", "") if trans else ""))
                self.tabla.setItem(row, 9, QTableWidgetItem(usr.get("nombre", "") if usr else ""))

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo buscar movimientos: {str(e)}")

    def obtener_seleccionado(self):
        for row in range(self.tabla.rowCount()):
            chk = self.tabla.cellWidget(row, 0)
            if chk and chk.isChecked():
                return chk.property("id_mov")
        return None

    def editar_movimiento(self):
        id_mov = self.obtener_seleccionado()

        if not id_mov:
            QMessageBox.warning(self, "Error", "Seleccione un movimiento")
            return

        try:
            movimientos = listar_entradas_salidas()
            mov = next((m for m in movimientos if m.get("id") == id_mov), None)

            if not mov:
                QMessageBox.warning(self, "Error", "Movimiento no encontrado")
                return

            cil = obtener_cilindro_por_codigo(mov.get("cilindro"))

            if not cil:
                QMessageBox.warning(self, "Error", "Cilindro no encontrado")
                return

            if cil.get("nuevo") != "SI":
                QMessageBox.warning(
                    self,
                    "No permitido",
                    "Este cilindro ya fue despachado.\nNo se puede modificar."
                )
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Editar Movimiento y Cilindro")

            layout = QFormLayout()

            fecha = QDateEdit()
            fecha.setCalendarPopup(True)
            fecha_str = str(mov.get("fecha", ""))
            fecha_qt = QDate.fromString(fecha_str, "yyyy-MM-dd")
            fecha.setDate(fecha_qt if fecha_qt.isValid() else QDate.currentDate())

            guia = QLineEdit(mov.get("nro_guia", ""))
            documento = QLineEdit(mov.get("nro_documento", ""))

            transportista_combo = QComboBox()
            transportistas = listar_transportistas()
            for t in transportistas:
                transportista_combo.addItem(
                    f"{t.get('codigo', '')} - {t.get('nombre', '')}",
                    t.get("codigo", "")
                )

            index_trans = transportista_combo.findData(mov.get("transportista"))
            if index_trans >= 0:
                transportista_combo.setCurrentIndex(index_trans)

            codigo_cil = QLineEdit(cil.get("codigo", ""))

            propietario = QComboBox()
            propietarios = listar_propietarios()
            for p in propietarios:
                propietario.addItem(
                    f"{p.get('codigo', '')} - {p.get('nombre', '')}",
                    p.get("codigo", "")
                )

            index_prop = propietario.findData(cil.get("propietario"))
            if index_prop >= 0:
                propietario.setCurrentIndex(index_prop)

            producto = QComboBox()
            productos = listar_productos()
            for prod in productos:
                producto.addItem(
                    f"{prod.get('codigo', '')} - {prod.get('nombre', '')}",
                    prod.get("codigo", "")
                )

            index_prod = producto.findData(cil.get("producto"))
            if index_prod >= 0:
                producto.setCurrentIndex(index_prod)

            fecha_hidro = QDateEdit()
            fecha_hidro.setCalendarPopup(True)
            fecha_hidro_str = str(cil.get("fecha_hidrostatica", ""))
            fecha_hidro_qt = QDate.fromString(fecha_hidro_str, "yyyy-MM-dd")
            if fecha_hidro_qt.isValid():
                fecha_hidro.setDate(fecha_hidro_qt)
            else:
                fecha_hidro.setDate(QDate.currentDate())

            layout.addRow("Fecha", fecha)
            layout.addRow("Guía", guia)
            layout.addRow("Documento", documento)
            layout.addRow("Transportista", transportista_combo)
            layout.addRow(QLabel("----- CILINDRO -----"))
            layout.addRow("Código", codigo_cil)
            layout.addRow("Propietario", propietario)
            layout.addRow("Producto", producto)
            layout.addRow("Fecha Hidrostática", fecha_hidro)

            btn_guardar = QPushButton("Guardar")
            layout.addRow(btn_guardar)

            dialog.setLayout(layout)

            def guardar():
                codigo_anterior = mov.get("cilindro")
                nuevo_codigo = codigo_cil.text().strip()

                if not nuevo_codigo:
                    QMessageBox.warning(dialog, "Error", "Ingrese código de cilindro")
                    return

                resp_mov = actualizar_registro(
                    "entradas_salidas",
                    {"id": f"eq.{id_mov}"},
                    {
                        "fecha": fecha.date().toPython().strftime("%Y-%m-%d"),
                        "nro_guia": guia.text().strip(),
                        "nro_documento": documento.text().strip(),
                        "cod_transportista": transportista_combo.currentData(),
                        "transportista": transportista_combo.currentData(),
                        "cilindro": nuevo_codigo
                    }
                )

                if resp_mov is None:
                    QMessageBox.warning(dialog, "Error", "No se pudo actualizar el movimiento")
                    return

                if codigo_anterior != nuevo_codigo:
                    resp_cil = actualizar_registro(
                        "cilindros",
                        {"codigo": f"eq.{codigo_anterior}"},
                        {
                            "codigo": nuevo_codigo,
                            "propietario": propietario.currentData(),
                            "producto": producto.currentData(),
                            "fecha_hidrostatica": fecha_hidro.date().toPython().strftime("%Y-%m-%d")
                        }
                    )
                else:
                    resp_cil = actualizar_registro(
                        "cilindros",
                        {"codigo": f"eq.{codigo_anterior}"},
                        {
                            "propietario": propietario.currentData(),
                            "producto": producto.currentData(),
                            "fecha_hidrostatica": fecha_hidro.date().toPython().strftime("%Y-%m-%d")
                        }
                    )

                if resp_cil is None:
                    QMessageBox.warning(dialog, "Error", "No se pudo actualizar el cilindro")
                    return

                estado = obtener_estado_cilindro_por_codigo(codigo_anterior)

                if estado:
                    filtros_estado = {"cilindro": f"eq.{codigo_anterior}"}
                    payload_estado = {
                        "propietario": propietario.currentData(),
                        "material": producto.currentData(),
                        "fecha_mov": fecha.date().toPython().strftime("%Y-%m-%d")
                    }

                    if codigo_anterior != nuevo_codigo:
                        payload_estado["cilindro"] = nuevo_codigo

                    resp_estado = actualizar_registro(
                        "estado_cilindros",
                        filtros_estado,
                        payload_estado
                    )

                    if resp_estado is None:
                        QMessageBox.warning(dialog, "Error", "No se pudo actualizar el estado del cilindro")
                        return

                QMessageBox.information(dialog, "OK", "Registro actualizado")
                dialog.accept()
                self.buscar()

            btn_guardar.clicked.connect(guardar)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo editar el movimiento: {str(e)}")

    def eliminar_movimiento(self):
        id_mov = self.obtener_seleccionado()

        if not id_mov:
            QMessageBox.warning(self, "Error", "Seleccione un movimiento")
            return

        try:
            movimientos = listar_entradas_salidas()
            mov = next((m for m in movimientos if m.get("id") == id_mov), None)

            if not mov:
                QMessageBox.warning(self, "Error", "Movimiento no encontrado")
                return

            cil = obtener_cilindro_por_codigo(mov.get("cilindro"))

            if not cil:
                QMessageBox.warning(self, "Error", "Cilindro no encontrado")
                return

            estado = obtener_estado_cilindro_por_codigo(mov.get("cilindro"))

            if cil.get("nuevo") != "SI":
                QMessageBox.warning(
                    self,
                    "No permitido",
                    "No se puede eliminar.\nEl cilindro ya fue despachado."
                )
                return

            confirm = QMessageBox.question(
                self,
                "Confirmar",
                "¿Eliminar movimiento y cilindro?"
            )

            if confirm != QMessageBox.Yes:
                return

            resp_mov = eliminar_registro(
                "entradas_salidas",
                {"id": f"eq.{id_mov}"}
            )

            if resp_mov is None:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el movimiento")
                return

            if estado:
                resp_estado = eliminar_registro(
                    "estado_cilindros",
                    {"cilindro": f"eq.{mov.get('cilindro')}"}
                )

                if resp_estado is None:
                    QMessageBox.warning(self, "Error", "No se pudo eliminar el estado del cilindro")
                    return

            resp_cil = eliminar_registro(
                "cilindros",
                {"codigo": f"eq.{mov.get('cilindro')}"}
            )

            if resp_cil is None:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el cilindro")
                return

            QMessageBox.information(self, "OK", "Movimiento y cilindro eliminados")
            self.buscar()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el movimiento: {str(e)}")