from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QDate

from database import SessionLocal
from models import EntradaSalida, Transportista, Cilindro, Usuario


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

        #btn_eliminar = QPushButton(
        #    "Eliminar"
        #)

        btn_editar.clicked.connect(
            self.editar_movimiento
        )

        #btn_eliminar.clicked.connect(
        #    self.eliminar_movimiento
        #)

        botones.addWidget(btn_editar)
        #botones.addWidget(btn_eliminar)

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

                # GUARDAR ID REAL
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

            dialog = QDialog(self)

            dialog.setWindowTitle(
                "Editar Movimiento"
            )

            layout = QFormLayout()

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

            transportista = QComboBox()

            data = db.query(
                Transportista
            ).all()

            for t in data:

                transportista.addItem(
                    f"{t.codigo} - {t.nombre}",
                    t.codigo
                )

            index = transportista.findData(
                mov.cod_transportista
            )

            if index >= 0:

                transportista.setCurrentIndex(
                    index
                )

            #tipo = QComboBox()

            #tipo.addItems([
            #    "INGRESO",
            #    "RECARGA"
            #])

            #tipo.setCurrentText(
            #    mov.tipo
            #)

            layout.addRow("Fecha", fecha)
            layout.addRow("Guía", guia)
            layout.addRow("Documento", documento)
            layout.addRow("Transportista", transportista)
            #layout.addRow("Tipo", tipo)

            btn_guardar = QPushButton(
                "Guardar"
            )

            layout.addRow(btn_guardar)

            dialog.setLayout(layout)

            def guardar():

                mov.fecha = (
                    fecha.date().toPython()
                )

                mov.nro_guia = (
                    guia.text().strip()
                )

                mov.nro_documento = (
                    documento.text().strip()
                )

                mov.cod_transportista = (
                    transportista.currentData()
                )

                mov.transportista = (
                    transportista.currentData()
                )

                #mov.tipo = (
                #    tipo.currentText()
                #)

                db.commit()

                QMessageBox.information(
                    dialog,
                    "OK",
                    "Movimiento actualizado"
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

        confirm = QMessageBox.question(
            self,
            "Confirmar",
            "¿Eliminar movimiento?"
        )

        if confirm != QMessageBox.Yes:

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

            db.delete(
                mov
            )

            db.commit()

            QMessageBox.information(
                self,
                "OK",
                "Movimiento eliminado"
            )

            self.buscar()

        finally:

            db.close()