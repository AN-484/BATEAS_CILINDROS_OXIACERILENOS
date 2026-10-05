import math
import os

from PySide6.QtCore import Qt, QPointF, QRectF, QSizeF, Signal
from PySide6.QtGui import (
    QBrush, QColor, QFont, QFontMetricsF, QPen, QPixmap, QPolygonF
)
from PySide6.QtWidgets import QGraphicsItem, QGraphicsScene

MARGEN = 10
ASA = 12


class Escena(QGraphicsScene):
    modificado = Signal()


class ItemEditable(QGraphicsItem):
    """Item movible, redimensionable (asa inferior derecha) y rotable."""

    def __init__(self):
        super().__init__()
        self.setFlags(
            QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemSendsGeometryChanges
        )
        self._redimensionando = False

    # --- a implementar ---
    def tamano(self) -> QSizeF:
        raise NotImplementedError

    def dibujar(self, painter):
        raise NotImplementedError

    # --- geometría ---
    def centrar_origen(self):
        t = self.tamano()
        self.setTransformOriginPoint(t.width() / 2, t.height() / 2)

    def boundingRect(self):
        t = self.tamano()
        return QRectF(-MARGEN, -MARGEN, t.width() + 2 * MARGEN, t.height() + 2 * MARGEN)

    def _rect_asa(self):
        t = self.tamano()
        lado = ASA / max(self.scale(), 0.05)
        return QRectF(t.width() - lado / 2, t.height() - lado / 2, lado, lado)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(painter.RenderHint.Antialiasing)
        painter.setRenderHint(painter.RenderHint.SmoothPixmapTransform)
        self.dibujar(painter)
        if self.isSelected() and not getattr(self.scene(), "exportando", False):
            t = self.tamano()
            lapiz = QPen(QColor("#2E75B6"), 0, Qt.DashLine)
            painter.setPen(lapiz)
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(QRectF(0, 0, t.width(), t.height()))
            painter.setBrush(QColor("#2E75B6"))
            painter.drawRect(self._rect_asa())

    def itemChange(self, change, value):
        if change in (
            QGraphicsItem.ItemScaleHasChanged,
            QGraphicsItem.ItemRotationHasChanged,
        ):
            sc = self.scene()
            if sc is not None:
                sc.modificado.emit()
        return super().itemChange(change, value)

    # --- ratón ---
    def mousePressEvent(self, event):
        if (
            event.button() == Qt.LeftButton
            and self.isSelected()
            and self._rect_asa().contains(event.pos())
        ):
            self._redimensionando = True
            event.accept()
            return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._redimensionando:
            t = self.tamano()
            centro = self.mapToScene(self.transformOriginPoint())
            d = event.scenePos() - centro
            d0 = math.hypot(t.width() / 2, t.height() / 2)
            self.setScale(max(0.1, math.hypot(d.x(), d.y()) / d0))
            event.accept()
            return
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._redimensionando = False
        super().mouseReleaseEvent(event)


_cache_pix = {}


def cargar_pixmap(ruta):
    if ruta not in _cache_pix:
        _cache_pix[ruta] = QPixmap(ruta)
    return _cache_pix[ruta]


class RomboNFPA(ItemEditable):
    LADO = 100

    def __init__(self, azul=0, rojo=0, amarillo=0, blanco=""):
        super().__init__()
        self.azul, self.rojo, self.amarillo = azul, rojo, amarillo
        self.blanco = blanco
        self.centrar_origen()

    def tamano(self):
        return QSizeF(self.LADO, self.LADO)

    def actualizar(self, azul, rojo, amarillo, blanco):
        self.azul, self.rojo, self.amarillo, self.blanco = azul, rojo, amarillo, blanco
        self.update()

    def _dibujar_blanco(self, p, r):
        clave = self.blanco
        if not clave:
            return
        p.setPen(Qt.black)
        f = QFont("Segoe UI Symbol" if clave in ("RAD", "BIO") else "Arial")
        f.setBold(True)
        f.setPixelSize({"OX": 13, "COR": 9, "SA": 12, "W": 17, "RAD": 24, "BIO": 24}[clave])
        p.setFont(f)
        texto = {"RAD": "\u2622", "BIO": "\u2623"}.get(clave, clave)
        p.drawText(r, Qt.AlignCenter, texto)
        if clave == "W":
            p.setPen(QPen(Qt.black, 1.8))
            c = r.center()
            p.drawLine(QPointF(c.x() - 8, c.y()), QPointF(c.x() + 8, c.y()))

    def dibujar(self, p):
        def poly(*pts):
            return QPolygonF([QPointF(x, y) for x, y in pts])

        cuadros = [
            (poly((50, 0), (75, 25), (50, 50), (25, 25)), "#E02020", self.rojo, "white", (50, 25)),
            (poly((75, 25), (100, 50), (75, 75), (50, 50)), "#F5D800", self.amarillo, "black", (75, 50)),
            (poly((25, 25), (50, 50), (25, 75), (0, 50)), "#1F5FBF", self.azul, "white", (25, 50)),
            (poly((50, 50), (75, 75), (50, 100), (25, 75)), "#FFFFFF", None, "black", (50, 75)),
        ]
        p.setPen(QPen(Qt.black, 2))
        fuente = QFont("Arial")
        fuente.setBold(True)
        fuente.setPixelSize(22)
        for pol, color, valor, color_txt, (cx, cy) in cuadros:
            p.setBrush(QBrush(QColor(color)))
            p.drawPolygon(pol)
            r = QRectF(cx - 12.5, cy - 12.5, 25, 25)
            if valor is not None:
                p.setFont(fuente)
                p.setPen(QColor(color_txt))
                p.drawText(r, Qt.AlignCenter, str(valor))
                p.setPen(QPen(Qt.black, 2))
            else:
                self._dibujar_blanco(p, r)
                p.setPen(QPen(Qt.black, 2))


class TextoMaterial(ItemEditable):
    def __init__(self, texto="CODIGO-DESCRIPCION"):
        super().__init__()
        self.texto = texto
        self.color = QColor("#FFFF00")
        self._fuente = QFont("Arial")
        self._fuente.setBold(True)
        self._fuente.setPixelSize(28)
        self.centrar_origen()

    @property
    def negrita(self):
        return self._fuente.bold()

    @property
    def cursiva(self):
        return self._fuente.italic()

    @property
    def subrayado(self):
        return self._fuente.underline()

    def cambiar_estilo(self, negrita, cursiva, subrayado):
        self.prepareGeometryChange()
        self._fuente.setBold(negrita)
        self._fuente.setItalic(cursiva)
        self._fuente.setUnderline(subrayado)
        self.centrar_origen()
        self.update()

    def tamano(self):
        fm = QFontMetricsF(self._fuente)
        return QSizeF(fm.horizontalAdvance(self.texto) + 16, fm.height() + 8)

    def cambiar_texto(self, texto):
        self.prepareGeometryChange()
        self.texto = texto
        self.centrar_origen()
        self.update()

    def dibujar(self, p):
        t = self.tamano()
        r = QRectF(0, 0, t.width(), t.height())
        p.setPen(Qt.NoPen)
        p.setBrush(self.color)
        p.drawRect(r)
        p.setFont(self._fuente)
        p.setPen(Qt.white if 0 < self.color.alpha() and self.color.lightness() < 110 else Qt.black)
        p.drawText(r, Qt.AlignCenter, self.texto)


class SimboloPNG(ItemEditable):
    def __init__(self, ruta):
        super().__init__()
        self.ruta = ruta
        self.pix = cargar_pixmap(ruta)
        self.centrar_origen()

    def tamano(self):
        w, h = self.pix.width(), self.pix.height()
        mayor = max(w, h, 1)
        k = 100 / mayor
        return QSizeF(w * k, h * k)

    def dibujar(self, p):
        t = self.tamano()
        p.drawPixmap(QRectF(0, 0, t.width(), t.height()), self.pix, QRectF(self.pix.rect()))
