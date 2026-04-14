from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QDate

from database import SessionLocal
from models import EntradaSalida, Transportista, Cilindro, Usuario, Propietario, Producto, EstadoCilindro

from crud import actualizar_estado

class ModificarMovimientoUI(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "Modificar / Eliminar Movimiento"
        )

        layout = QVBoxLayout()

        # =====================================================
        # FILTROS
        # =====================================================

        filtros = QHBoxLayout()

        self.input_guia = QLineEdit()
        self.input_guia.setPlaceholderText(
            "N° Guía"
        )

        self.input_documento = QLineEdit()
        self.input_documento.setPlaceholderText(
            "N° Documento"
        )

        btn_buscar = QPushButton(
            "Buscar"
        )

        btn_buscar.clicked.connect(
            self.buscar
        )

        filtros.addWidget(QLabel("Guía:"))
        filtros.addWidget(self.input_guia)

        filtros.addWidget(QLabel("Documento:"))
        filtros.addWidget(self.input_documento)

        filtros.addWidget(btn_buscar)

        layout.addLayout(filtros)

        # =====================================================
        # TABLA
        # =====================================================

        self.tabla = QTableWidget()

        self.tabla.setColumnCount(9)

        self.tabla.setHorizontalHeaderLabels([
            "Sel",
            "Fecha",
            "Cilindro",
            "Fecha Hidrostática",
            "Tipo",
            "Guía",
            "Documento",
            "Transportista",
            "Usuario"
        ])

        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )

        layout.addWidget(self.tabla)

        # =====================================================
        # BOTONES
        # =====================================================

        botones = QHBoxLayout()

        btn_editar = QPushButton(
            "Editar"
        )

        btn_eliminar = QPushButton(
            "Eliminar"
        )

        btn_editar.clicked.connect(
            self.editar_movimiento
        )

        btn_eliminar.clicked.connect(
            self.eliminar_movimiento
        )

        botones.addWidget(btn_editar)
        botones.addWidget(btn_eliminar)

        layout.addLayout(botones)

        self.setLayout(layout)

    # =====================================================
    # BUSCAR
    # =====================================================

    def buscar(self):

        guia = self.input_guia.text().strip()
        documento = self.input_documento.text().strip()

        if not guia and not documento:

            QMessageBox.warning(
                self,
                "Error",
                "Ingrese guía o documento"
            )
            return

        db = SessionLocal()

        try:

            query = db.query(
                EntradaSalida,
                Cilindro,
                Usuario,
                Transportista
            ).join(
                Cilindro,
                EntradaSalida.cilindro == Cilindro.codigo
            ).join(
                Usuario,
                EntradaSalida.registrado_por == Usuario.codigo
            ).join(
                Transportista,
                EntradaSalida.transportista == Transportista.codigo
            )

            if guia:

                query = query.filter(
                    EntradaSalida.nro_guia == guia
                )

            if documento:

                query = query.filter(
                    EntradaSalida.nro_documento == documento
                )

            movimientos = query.all()

            self.tabla.setRowCount(0)

            for row, (mov, cil, usr, trans) in enumerate(movimientos):

                self.tabla.insertRow(row)

                chk = QCheckBox()

                chk.setProperty(
                    "id_mov",
                    mov.id
                )

                self.tabla.setCellWidget(
                    row,
                    0,
                    chk
                )

                self.tabla.setItem(
                    row,
                    1,
                    QTableWidgetItem(
                        str(mov.fecha)
                    )
                )

                self.tabla.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        mov.cilindro
                    )
                )

                self.tabla.setItem(
                    row,
                    3,
                    QTableWidgetItem(
                        str(cil.fecha_hidrostatica)
                        if cil.fecha_hidrostatica
                        else ""
                    )
                )

                self.tabla.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        mov.tipo
                    )
                )

                self.tabla.setItem(
                    row,
                    5,
                    QTableWidgetItem(
                        mov.nro_guia
                    )
                )

                self.tabla.setItem(
                    row,
                    6,
                    QTableWidgetItem(
                        mov.nro_documento
                    )
                )

                self.tabla.setItem(
                    row,
                    7,
                    QTableWidgetItem(
                        trans.nombre
                    )
                )

                self.tabla.setItem(
                    row,
                    8,
                    QTableWidgetItem(
                        usr.nombre
                    )
                )

        finally:

            db.close()

    # =====================================================
    # OBTENER SELECCIONADO
    # =====================================================

    def obtener_seleccionado(self):

        for row in range(
            self.tabla.rowCount()
        ):

            chk = self.tabla.cellWidget(
                row,
                0
            )

            if chk.isChecked():

                return chk.property(
                    "id_mov"
                )

        return None

    # =====================================================
    # EDITAR
    # =====================================================

    def editar_movimiento(self):

        id_mov = self.obtener_seleccionado()

        if not id_mov:

            QMessageBox.warning(
                self,
                "Error",
                "Seleccione un movimiento"
            )
            return

        db = SessionLocal()

        try:

            mov = db.query(
                EntradaSalida
            ).filter_by(
                id=id_mov
            ).first()

            if not mov:

                QMessageBox.warning(
                    self,
                    "Error",
                    "Movimiento no encontrado"
                )
                return

            cil = db.query(
                Cilindro
            ).filter_by(
                codigo=mov.cilindro
            ).first()

            if not cil:

                QMessageBox.warning(
                    self,
                    "Error",
                    "Cilindro no encontrado"
                )
                return

            # VALIDACION

            if cil.nuevo != "SI":

                QMessageBox.warning(
                    self,
                    "No permitido",
                    "Este cilindro ya fue despachado.\n"
                    "No se puede modificar."
                )

                return

            dialog = QDialog(self)

            dialog.setWindowTitle(
                "Editar Movimiento y Cilindro"
            )

            layout = QFormLayout()

            # MOVIMIENTO

            fecha = QDateEdit()
            fecha.setCalendarPopup(True)

            fecha.setDate(
                QDate(
                    mov.fecha.year,
                    mov.fecha.month,
                    mov.fecha.day
                )
            )

            guia = QLineEdit(
                mov.nro_guia
            )

            documento = QLineEdit(
                mov.nro_documento
            )

            # CILINDRO

            codigo_cil = QLineEdit(
                cil.codigo
            )

            propietario = QComboBox()

            propietarios = db.query(
                Propietario
            ).all()

            for p in propietarios:

                propietario.addItem(
                    f"{p.codigo} - {p.nombre}",
                    p.codigo
                )

            index_prop = propietario.findData(
                cil.propietario
            )

            if index_prop >= 0:

                propietario.setCurrentIndex(
                    index_prop
                )

            producto = QComboBox()

            productos = db.query(
                Producto
            ).all()

            for prod in productos:

                producto.addItem(
                    f"{prod.codigo} - {prod.nombre}",
                    prod.codigo
                )

            index_prod = producto.findData(
                cil.producto
            )

            if index_prod >= 0:

                producto.setCurrentIndex(
                    index_prod
                )

            fecha_hidro = QDateEdit()

            fecha_hidro.setCalendarPopup(
                True
            )

            if cil.fecha_hidrostatica:

                fecha_hidro.setDate(
                    QDate(
                        cil.fecha_hidrostatica.year,
                        cil.fecha_hidrostatica.month,
                        cil.fecha_hidrostatica.day
                    )
                )

            layout.addRow("Fecha", fecha)
            layout.addRow("Guía", guia)
            layout.addRow("Documento", documento)

            layout.addRow(
                QLabel("----- CILINDRO -----")
            )

            layout.addRow(
                "Código",
                codigo_cil
            )

            layout.addRow(
                "Propietario",
                propietario
            )

            layout.addRow(
                "Producto",
                producto
            )

            layout.addRow(
                "Fecha Hidrostática",
                fecha_hidro
            )

            btn_guardar = QPushButton(
                "Guardar"
            )

            layout.addRow(
                btn_guardar
            )

            dialog.setLayout(
                layout
            )

            def guardar():

                codigo_anterior = mov.cilindro
                nuevo_codigo = codigo_cil.text().strip()

                # =========================
                # ACTUALIZAR MOVIMIENTO
                # =========================

                mov.fecha = fecha.date().toPython()

                mov.nro_guia = guia.text().strip()

                mov.nro_documento = documento.text().strip()

                # =========================
                # ACTUALIZAR CILINDRO
                # =========================

                cil.codigo = nuevo_codigo

                cil.propietario = propietario.currentData()

                cil.producto = producto.currentData()

                cil.fecha_hidrostatica = (
                    fecha_hidro.date().toPython()
                )

                # =========================
                # ACTUALIZAR LISTA DE ESTADOS
                # =========================

                estado = db.query(
                    EstadoCilindro
                ).filter_by(
                    cilindro=codigo_anterior
                ).first()

                if estado:

                    estado.cilindro = nuevo_codigo

                    estado.propietario = (
                        propietario.currentData()
                    )

                    estado.material = (
                        producto.currentData()
                    )

                    estado.fecha_mov = (
                        fecha.date().toPython()
                    )

                # =========================
                # ACTUALIZAR RELACION
                # =========================

                if codigo_anterior != nuevo_codigo:

                    mov.cilindro = nuevo_codigo

                db.commit()

                QMessageBox.information(
                    dialog,
                    "OK",
                    "Registro actualizado"
                )

                dialog.accept()

                self.buscar()


            btn_guardar.clicked.connect(
                guardar
            )

            dialog.exec()

        finally:

            db.close()

    # =====================================================
    # ELIMINAR
    # =====================================================

    def eliminar_movimiento(self):

        id_mov = self.obtener_seleccionado()

        if not id_mov:

            QMessageBox.warning(
                self,
                "Error",
                "Seleccione un movimiento"
            )
            return

        db = SessionLocal()

        try:

            mov = db.query(
                EntradaSalida
            ).filter_by(
                id=id_mov
            ).first()

            if not mov:

                QMessageBox.warning(
                    self,
                    "Error",
                    "Movimiento no encontrado"
                )
                return

            # =========================
            # BUSCAR CILINDRO
            # =========================

            cil = db.query(
                Cilindro
            ).filter_by(
                codigo=mov.cilindro
            ).first()

            if not cil:

                QMessageBox.warning(
                    self,
                    "Error",
                    "Cilindro no encontrado"
                )
                return

            # =========================
            # BUSCAR ESTADO
            # =========================

            estado = db.query(
                EstadoCilindro
            ).filter_by(
                cilindro=mov.cilindro
            ).first()

            if not cil:

                QMessageBox.warning(
                    self,
                    "Error",
                    "Cilindro no encontrado"
                )
                return

            if cil.nuevo != "SI":

                QMessageBox.warning(
                    self,
                    "No permitido",
                    "No se puede eliminar.\n"
                    "El cilindro ya fue despachado."
                )

                return

            confirm = QMessageBox.question(
                self,
                "Confirmar",
                "¿Eliminar movimiento y cilindro?"
            )

            if confirm != QMessageBox.Yes:

                return

            # =========================
            # ELIMINAR REGISTROS
            # =========================

            db.delete(
                mov
            )

            if estado:

                db.delete(
                    estado
                )

            db.delete(
                cil
            )

            db.commit()

            QMessageBox.information(
                self,
                "OK",
                "Movimiento y cilindro eliminados"
            )

            self.buscar()

        finally:

            db.close()