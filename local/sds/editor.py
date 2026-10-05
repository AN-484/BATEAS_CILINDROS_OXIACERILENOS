import os

import fitz

from PySide6.QtCore import Qt, QBuffer, QByteArray, QIODevice, QPoint, QRectF, QSize
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPen, QPixmap
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QFormLayout, QPushButton,
    QLabel, QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, QFileDialog,
    QMessageBox, QGraphicsView, QGraphicsPixmapItem, QMenu
)

from utils import app_icon, ruta_recurso
from local.sds.items import Escena, RomboNFPA, TextoMaterial, SimboloPNG

ZOOM_RENDER = 2.0      # píxeles de escena por punto PDF
ESCALA_EXPORT = 2.0    # multiplicador de resolución de la capa exportada
PASO_GIRO = 30

SIMBOLOS_BLANCO = [
    ("VACIO", ""),
    ("OX - Oxidante", "OX"),
    ("COR - Corrosivo", "COR"),
    ("\u2622 - Radiactivo", "RAD"),
    ("W - No usar agua", "W"),
    ("\u2623 - Riesgo biológico", "BIO"),
    ("SA - Gas asfixiante", "SA"),
]

ESTILO = """
    QGroupBox { font-weight: bold; color: #1F3A5F; border: 1px solid #2E75B6;
                border-radius: 4px; margin-top: 10px; padding-top: 8px; }
    QGroupBox::title { subcontrol-origin: margin; left: 8px; }
    QPushButton { background-color: #2E75B6; color: white; padding: 6px;
                  border-radius: 4px; font-weight: bold; }
    QPushButton:hover { background-color: #1F5A8A; }
    QPushButton:disabled { background-color: #A0A0A0; }
    QPushButton:checked { background-color: #1F3A5F; }
    QPushButton#peligro { background-color: #C0392B; }
    QPushButton#peligro:disabled { background-color: #A0A0A0; }
"""


def _icono_barril():
    pm = QPixmap(64, 64)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(QPen(QColor("#3E2A14"), 3))
    p.setBrush(QColor("#A0662B"))
    p.drawRoundedRect(14, 6, 36, 52, 8, 8)
    p.setBrush(QColor("#C98A4B"))
    p.drawEllipse(14, 2, 36, 12)
    p.setBrush(Qt.NoBrush)
    p.drawLine(14, 22, 50, 22)
    p.drawLine(14, 42, 50, 42)
    p.end()
    return QIcon(pm)


COLORES_RESALTADO = [
    ("Amarillo", "#FFFF00"), ("Verde brillante", "#00FF00"),
    ("Turquesa", "#00FFFF"), ("Rosa", "#FF00FF"), ("Azul", "#0000FF"),
    ("Rojo", "#FF0000"), ("Azul oscuro", "#000080"),
    ("Verde azulado", "#008080"), ("Verde", "#008000"),
    ("Violeta", "#800080"), ("Rojo oscuro", "#800000"),
    ("Amarillo oscuro", "#808000"), ("Gris 50%", "#808080"),
    ("Gris 25%", "#C0C0C0"), ("Negro", "#000000"),
    ("Sin color (transparente)", None),
]


def _icono_resaltador(color):
    pm = QPixmap(64, 64)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.setPen(Qt.NoPen)
    p.setBrush(color)
    p.drawRect(6, 50, 52, 12)
    if color.alpha() == 0:
        p.setPen(QPen(QColor("#888888"), 2))
        p.setBrush(Qt.NoBrush)
        p.drawRect(6, 50, 52, 12)
        p.setPen(QPen(QColor("#D32F2F"), 3))
        p.drawLine(6, 62, 58, 50)
        p.setPen(Qt.NoPen)
    p.setPen(QPen(QColor("#333333"), 3))
    p.translate(32, 28)
    p.rotate(45)
    p.setBrush(QColor("#F2F2F2"))
    p.drawRect(-8, -22, 16, 30)
    p.setBrush(color)
    p.drawPolygon([QPoint(-8, 8), QPoint(8, 8), QPoint(5, 20), QPoint(-5, 20)])
    p.end()
    return QIcon(pm)


class Vista(QGraphicsView):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.setAcceptDrops(True)
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

    def paintEvent(self, e):
        if self.editor.doc is not None:
            super().paintEvent(e)
            return
        p = QPainter(self.viewport())
        p.fillRect(self.viewport().rect(), QColor("#F4F7FB"))
        r = self.viewport().rect().adjusted(30, 30, -30, -30)
        p.setPen(QPen(QColor("#2E75B6"), 3, Qt.DashLine))
        p.drawRoundedRect(r, 12, 12)
        f = p.font()
        f.setPointSize(16)
        f.setBold(True)
        p.setFont(f)
        p.setPen(QColor("#1F3A5F"))
        p.drawText(r.adjusted(15, 0, -15, 0), Qt.AlignCenter | Qt.TextWordWrap,
                   "Arrastre aquí el PDF (o imagen) de la hoja SDS\n"
                   "o haga clic para seleccionarlo")
        p.end()

    def mousePressEvent(self, e):
        if self.editor.doc is None and e.button() == Qt.LeftButton:
            self.editor.abrir()
            return
        super().mousePressEvent(e)

    @staticmethod
    def _ruta_valida(mime):
        if not mime.hasUrls():
            return None
        ruta = mime.urls()[0].toLocalFile()
        ok = ruta.lower().endswith((".pdf", ".png", ".jpg", ".jpeg"))
        return ruta if ok else None

    def dragEnterEvent(self, e):
        if self._ruta_valida(e.mimeData()):
            e.acceptProposedAction()

    def dragMoveEvent(self, e):
        if self._ruta_valida(e.mimeData()):
            e.acceptProposedAction()

    def dropEvent(self, e):
        ruta = self._ruta_valida(e.mimeData())
        if ruta:
            e.acceptProposedAction()
            self.editor.abrir_ruta(ruta)

    def wheelEvent(self, e):
        paso = 1.15 if e.angleDelta().y() > 0 else 1 / 1.15
        if e.modifiers() & Qt.ControlModifier:
            self.scale(paso, paso)
        elif e.modifiers() & Qt.ShiftModifier:
            it = self.editor.item_actual()
            if it:
                it.setScale(max(0.1, it.scale() * paso))
        else:
            super().wheelEvent(e)


class SDSEditor(QWidget):
    def __init__(self, menu=None):
        super().__init__()
        self.menu = menu
        self.setWindowTitle("SDS - Editor de hojas de seguridad")
        self.setWindowIcon(app_icon())
        self.setStyleSheet(ESTILO)

        self.doc = None
        self.ruta_origen = ""
        self.escenas = {}
        self.pagina = 0
        self._sync = False

        self.vista = Vista(self)
        self._construir_izquierda()
        self._construir_derecha()

        raiz = QHBoxLayout(self)
        raiz.addWidget(self.izq)
        raiz.addWidget(self.vista, 1)
        raiz.addWidget(self.der)

        self._actualizar_habilitado()

    # ---------- UI ----------
    def _construir_izquierda(self):
        self.izq = QWidget()
        self.izq.setFixedWidth(260)
        v = QVBoxLayout(self.izq)

        g = QGroupBox("Documento")
        f = QVBoxLayout(g)
        b_abrir = QPushButton("Abrir PDF / imagen")
        b_abrir.clicked.connect(self.abrir)
        fila = QHBoxLayout()
        self.b_ant = QPushButton("<")
        self.b_sig = QPushButton(">")
        self.l_pag = QLabel("Pág. - / -")
        self.l_pag.setAlignment(Qt.AlignCenter)
        self.b_ant.clicked.connect(lambda: self.ir_pagina(self.pagina - 1))
        self.b_sig.clicked.connect(lambda: self.ir_pagina(self.pagina + 1))
        fila.addWidget(self.b_ant)
        fila.addWidget(self.l_pag, 1)
        fila.addWidget(self.b_sig)
        f.addWidget(b_abrir)
        f.addLayout(fila)
        v.addWidget(g)

        self.g_elem = QGroupBox("Elemento seleccionado")
        f = QFormLayout(self.g_elem)
        self.sp_escala = QDoubleSpinBox()
        self.sp_escala.setRange(10, 2000)
        self.sp_escala.setSuffix(" %")
        self.sp_escala.valueChanged.connect(self._cambia_escala)
        f.addRow("Tamaño:", self.sp_escala)
        self.l_giro = QLabel("0°")
        self.l_giro.setAlignment(Qt.AlignCenter)
        b_anti = QPushButton("\u21BA")  # Antihorario
        b_hor = QPushButton("\u21BB")  # Horario
        b_anti.clicked.connect(lambda: self._girar(-PASO_GIRO))
        b_hor.clicked.connect(lambda: self._girar(PASO_GIRO))
        fila = QHBoxLayout()
        fila.addWidget(b_anti)
        fila.addWidget(b_hor)
        f.addRow(fila)
        f.addRow("Giro actual:", self.l_giro)
        b_del = QPushButton("Eliminar (Supr)")
        b_del.setObjectName("peligro")
        b_del.clicked.connect(self.eliminar)
        f.addRow(b_del)
        v.addWidget(self.g_elem)

        ayuda = QLabel(
            "Clic en un elemento para seleccionarlo.\n"
            "Arrastre para mover. Asa azul: tamaño.\n"
            "Shift+rueda: tamaño. Ctrl+rueda: zoom.\n"
            "Supr o Borrar: eliminar."
        )
        ayuda.setWordWrap(True)
        v.addWidget(ayuda)

        v.addStretch()
        self.b_terminar = QPushButton("Terminar")
        self.b_terminar.setObjectName("peligro")
        self.b_terminar.clicked.connect(self.close)
        v.addWidget(self.b_terminar)
        self.b_guardar = QPushButton("Guardar PDF nuevo")
        self.b_guardar.clicked.connect(self.guardar)
        v.addWidget(self.b_guardar)

    def _construir_derecha(self):
        self.der = QWidget()
        self.der.setFixedWidth(280)
        v = QVBoxLayout(self.der)

        g = QGroupBox("Rombo NFPA")
        f = QFormLayout(g)
        self.s_azul, self.s_rojo, self.s_amar = QSpinBox(), QSpinBox(), QSpinBox()
        for s in (self.s_azul, self.s_rojo, self.s_amar):
            s.setRange(0, 4)
            s.valueChanged.connect(self._edita_rombo)
        self.c_blanco = QComboBox()
        for etiqueta, clave in SIMBOLOS_BLANCO:
            self.c_blanco.addItem(etiqueta, clave)
        self.c_blanco.currentIndexChanged.connect(self._edita_rombo)
        f.addRow("Azul (salud):", self.s_azul)
        f.addRow("Rojo (inflam.):", self.s_rojo)
        f.addRow("Amarillo (reactiv.):", self.s_amar)
        f.addRow("Blanco:", self.c_blanco)
        b_add = QPushButton("Agregar rombo")
        b_add.clicked.connect(self.agregar_rombo)
        f.addRow(b_add)
        v.addWidget(g)

        g = QGroupBox("Símbolos internos")
        f = QVBoxLayout(g)
        self.c_simbolo = QComboBox()
        b_int = QPushButton("Agregar símbolo")
        b_int.clicked.connect(self.agregar_simbolo_interno)
        f.addWidget(self.c_simbolo)
        f.addWidget(b_int)
        v.addWidget(g)
        self.refrescar_simbolos()

        g = QGroupBox("Imagen PNG externa")
        f = QVBoxLayout(g)
        b_sim = QPushButton("Agregar imagen PNG...")
        b_sim.clicked.connect(self.agregar_simbolo)
        f.addWidget(b_sim)
        v.addWidget(g)

        g = QGroupBox("Texto (código-descripción)")
        f = QVBoxLayout(g)
        self.e_texto = QLineEdit()
        self.e_texto.setPlaceholderText("CODIGO-DESCRIPCION")
        self.e_texto.textChanged.connect(self._edita_texto)
        f.addWidget(self.e_texto)
        fila = QHBoxLayout()
        self.b_neg = QPushButton("N")
        self.b_cur = QPushButton("K")
        self.b_sub = QPushButton("S")
        self.b_neg.setToolTip("Negrita")
        self.b_cur.setToolTip("Cursiva")
        self.b_sub.setToolTip("Subrayado")
        for b, est in ((self.b_neg, "font-weight:bold;"),
                       (self.b_cur, "font-style:italic;"),
                       (self.b_sub, "text-decoration:underline;")):
            b.setCheckable(True)
            b.setStyleSheet(est)
            b.toggled.connect(self._edita_texto)
            fila.addWidget(b)
        self.b_color = QPushButton()
        self.b_color.setToolTip("Color de resaltado")
        self.b_color.setIconSize(QSize(20, 20))
        self.b_color.clicked.connect(self.elegir_color)
        fila.addWidget(self.b_color)
        self._pintar_boton_color(QColor("#FFFF00"))
        self.b_neg.setChecked(True)
        f.addLayout(fila)
        b_txt = QPushButton("Agregar texto")
        b_txt.clicked.connect(self.agregar_texto)
        f.addWidget(b_txt)
        v.addWidget(g)
        v.addStretch()

    # ---------- documento ----------
    def abrir(self):
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar hoja SDS", "",
            "PDF e imágenes (*.pdf *.png *.jpg *.jpeg)"
        )
        if not ruta:
            return
        self.abrir_ruta(ruta)

    def abrir_ruta(self, ruta):
        try:
            doc = fitz.open(ruta)
            if not doc.is_pdf:
                doc = fitz.open("pdf", doc.convert_to_pdf())
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{ex}")
            return
        self.doc = doc
        self.ruta_origen = ruta
        self.escenas = {}
        self.ir_pagina(0)

    def _escena(self, idx):
        if idx not in self.escenas:
            pg = self.doc[idx]
            pix = pg.get_pixmap(matrix=fitz.Matrix(ZOOM_RENDER, ZOOM_RENDER), alpha=False)
            img = QImage(pix.samples, pix.width, pix.height, pix.stride,
                         QImage.Format_RGB888).copy()
            sc = Escena()
            fondo = QGraphicsPixmapItem(QPixmap.fromImage(img))
            fondo.setZValue(-1000)
            sc.addItem(fondo)
            sc.fondo = fondo
            sc.exportando = False
            sc.setSceneRect(fondo.boundingRect())
            sc.selectionChanged.connect(self._sel_cambio)
            sc.modificado.connect(self._sel_cambio)
            self.escenas[idx] = sc
        return self.escenas[idx]

    def ir_pagina(self, idx):
        if not self.doc or not (0 <= idx < len(self.doc)):
            return
        self.pagina = idx
        self.vista.setScene(self._escena(idx))
        self.l_pag.setText(f"Pág. {idx + 1} / {len(self.doc)}")
        self.vista.fitInView(self.vista.sceneRect(), Qt.KeepAspectRatio)
        self._sel_cambio()

    def escena_actual(self):
        return self.vista.scene() if self.doc else None

    def _requiere_doc(self):
        if not self.doc:
            QMessageBox.information(self, "SDS", "Primero abra un PDF o imagen.")
            return False
        return True

    # ---------- elementos ----------
    def _colocar(self, item):
        sc = self.escena_actual()
        centro = self.vista.mapToScene(self.vista.viewport().rect().center())
        t = item.tamano()
        item.setPos(centro.x() - t.width() / 2, centro.y() - t.height() / 2)
        sc.addItem(item)
        sc.clearSelection()
        item.setSelected(True)

    def agregar_rombo(self):
        if not self._requiere_doc():
            return
        r = RomboNFPA(self.s_azul.value(), self.s_rojo.value(), self.s_amar.value(),
                      self.c_blanco.currentData())
        r.setScale(1.5)
        self._colocar(r)

    def agregar_simbolo(self):
        if not self._requiere_doc():
            return
        ruta, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar imagen PNG", "", "Imagen PNG (*.png)"
        )
        if not ruta:
            return
        s = SimboloPNG(ruta)
        if s.pix.isNull():
            QMessageBox.warning(self, "SDS", "No se pudo cargar la imagen.")
            return
        self._colocar(s)

    def agregar_simbolo_interno(self):
        if not self._requiere_doc():
            return
        nombre = self.c_simbolo.currentText()
        if not nombre:
            QMessageBox.information(self, "SDS", "No hay símbolos PNG en local/sds/simbolos.")
            return
        s = SimboloPNG(os.path.join(self.carpeta_simbolos, nombre + ".png"))
        s.setScale(2.5)
        self._colocar(s)

    def refrescar_simbolos(self):
        self.carpeta_simbolos = ruta_recurso(os.path.join("local", "sds", "simbolos"))
        os.makedirs(self.carpeta_simbolos, exist_ok=True)
        self.c_simbolo.clear()
        self.c_simbolo.addItems(sorted(
            os.path.splitext(n)[0] for n in os.listdir(self.carpeta_simbolos)
            if n.lower().endswith(".png")
        ))

    def _pintar_boton_color(self, color):
        self.color_resalte = color
        self.b_color.setIcon(_icono_resaltador(color))

    def elegir_color(self):
        menu = QMenu(self)
        for nombre, hexa in COLORES_RESALTADO:
            c = QColor(hexa) if hexa else QColor(0, 0, 0, 0)
            menu.addAction(_icono_resaltador(c), nombre).setData(c)
        accion = menu.exec(self.b_color.mapToGlobal(self.b_color.rect().bottomLeft()))
        if accion is None:
            return
        c = accion.data()
        self._pintar_boton_color(c)
        it = self.item_actual()
        if isinstance(it, TextoMaterial):
            it.color = c
            it.update()

    def agregar_texto(self):
        if not self._requiere_doc():
            return
        t = TextoMaterial(self.e_texto.text().strip() or "CODIGO-DESCRIPCION")
        t.color = QColor(self.color_resalte)
        t.cambiar_estilo(self.b_neg.isChecked(), self.b_cur.isChecked(),
                         self.b_sub.isChecked())
        self._colocar(t)

    def eliminar(self):
        it = self.item_actual()
        if it:
            it.scene().removeItem(it)
            self._sel_cambio()

    def item_actual(self):
        sc = self.escena_actual()
        if not sc:
            return None
        sel = sc.selectedItems()
        return sel[0] if sel else None

    def closeEvent(self, e):
        r = QMessageBox.question(
            self, "Terminar", "¿Está seguro de terminar? Se perderán los cambios no guardados.",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if r != QMessageBox.Yes:
            e.ignore()
            return
        if self.menu is not None:
            self.menu.show()
        e.accept()

    def keyPressEvent(self, e):
        if e.key() in (Qt.Key_Delete, Qt.Key_Backspace) and self.item_actual():
            self.eliminar()
            return
        super().keyPressEvent(e)

    # ---------- edición automática de la selección ----------
    def _actualizar_habilitado(self):
        self.g_elem.setEnabled(self.item_actual() is not None)

    def _sel_cambio(self):
        it = self.item_actual()
        self._actualizar_habilitado()
        self._sync = True
        if it:
            self.sp_escala.setValue(it.scale() * 100)
            self.l_giro.setText(f"{round(it.rotation()) % 360}°")
            if isinstance(it, RomboNFPA):
                self.s_azul.setValue(it.azul)
                self.s_rojo.setValue(it.rojo)
                self.s_amar.setValue(it.amarillo)
                self.c_blanco.setCurrentIndex(max(0, self.c_blanco.findData(it.blanco)))
            elif isinstance(it, TextoMaterial):
                self.e_texto.setText(it.texto)
                self.b_neg.setChecked(it.negrita)
                self.b_cur.setChecked(it.cursiva)
                self.b_sub.setChecked(it.subrayado)
                self._pintar_boton_color(it.color)
        self._sync = False

    def _edita_rombo(self, *_):
        it = self.item_actual()
        if self._sync or not isinstance(it, RomboNFPA):
            return
        it.actualizar(self.s_azul.value(), self.s_rojo.value(),
                      self.s_amar.value(), self.c_blanco.currentData())

    def _edita_texto(self, *_):
        it = self.item_actual()
        if self._sync or not isinstance(it, TextoMaterial):
            return
        it.cambiar_estilo(self.b_neg.isChecked(), self.b_cur.isChecked(),
                          self.b_sub.isChecked())
        it.cambiar_texto(self.e_texto.text() or " ")

    def _cambia_escala(self, val):
        it = self.item_actual()
        if it and not self._sync:
            it.setScale(val / 100)

    def _girar(self, grados):
        it = self.item_actual()
        if it:
            it.setRotation((it.rotation() + grados) % 360)

    # ---------- exportar ----------
    def guardar(self):
        if not self._requiere_doc():
            return
        base = os.path.splitext(os.path.basename(self.ruta_origen))[0]
        destino, _ = QFileDialog.getSaveFileName(
            self, "Guardar PDF", f"{base}_NFPA.pdf", "PDF (*.pdf)"
        )
        if not destino:
            return
        try:
            # Copia para no acumular capas en guardados repetidos
            salida = fitz.open("pdf", self.doc.tobytes())
            for idx, sc in self.escenas.items():
                items = [i for i in sc.items() if i is not sc.fondo and isinstance(
                    i, (RomboNFPA, TextoMaterial, SimboloPNG))]
                if not items:
                    continue
                sc.clearSelection()
                sc.exportando = True
                sc.fondo.setVisible(False)
                rect = sc.sceneRect()
                w = int(rect.width() * ESCALA_EXPORT)
                h = int(rect.height() * ESCALA_EXPORT)
                img = QImage(w, h, QImage.Format_ARGB32_Premultiplied)
                img.fill(Qt.transparent)
                p = QPainter(img)
                p.setRenderHint(QPainter.Antialiasing)
                p.setRenderHint(QPainter.SmoothPixmapTransform)
                sc.render(p, QRectF(0, 0, w, h), rect)
                p.end()
                sc.fondo.setVisible(True)
                sc.exportando = False

                datos = QByteArray()
                buf = QBuffer(datos)
                buf.open(QIODevice.WriteOnly)
                img.save(buf, "PNG")
                buf.close()
                pagina = salida[idx]
                pagina.insert_image(pagina.rect, stream=bytes(datos.data()), overlay=True)

            salida.save(destino, garbage=3, deflate=True)
            salida.close()
        except Exception as ex:
            QMessageBox.critical(self, "Error", f"No se pudo guardar:\n{ex}")
            return
        QMessageBox.information(self, "SDS", f"PDF guardado en:\n{destino}")
