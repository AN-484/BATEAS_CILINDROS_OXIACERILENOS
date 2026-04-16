from PySide6.QtWidgets import QMainWindow, QVBoxLayout
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QSizePolicy

from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSplitter
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QPixmap

# DATOS
from ui.productos_ui import ProductosUI
from ui.transportistas_ui import TransportistasUI
from ui.ubicaciones_ui import UbicacionesUI
from ui.almacenes_ui import AlmacenesUI
from ui.cilindros_ui import CilindrosUI
from ui.usuarios_ui import UsuariosUI
from ui.propietarios_ui import PropietariosUI

# FUNCIONES
from ui.func_despacho_recepcion_ui import FuncDespachoRecepcionUI
from ui.func_entrada_salida_ui import FuncEntradaSalidaUI
from ui.entrada_salida_masivo import EntradaSalidaMasivoUI

from ui.reportes.rep_movimientos import ReporteMovimientos
from ui.reportes.rep_kardex import KardexUI

from ui.reportes.dashboard import DashboardUI

from PySide6.QtWidgets import QToolBar
from PySide6.QtCore import Qt

from utils import ruta_recurso

from ui.reportes.rep_estado_cilindros import ReporteEstadoCilindros
from ui.reportes.rep_entradas_salidas import ReporteEntradasSalidas
from PySide6.QtGui import QShortcut, QKeySequence


class MainWindow(QMainWindow):
    def __init__(self, usuario):

        super().__init__()

        self.usuario = usuario
        self.ventanas = []

        self.setWindowTitle(f"SCCO :  Cilindros   -   {usuario}")
        self.resize(1000, 600)

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.layout = QVBoxLayout(self.central)

        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        self.panel_izq = QWidget()
        self.panel_izq_layout = QVBoxLayout(self.panel_izq)

        self.logo = QLabel()
        ruta = ruta_recurso("img/boar.jpeg")

        self.setStyleSheet(f"""
            QWidget {{
                background-image: url({ruta});
                background-repeat: no-repeat;
                background-position: center;
            }}
        """)

        pixmap = QPixmap(ruta)
        self.logo.setPixmap(pixmap)
        self.logo.setScaledContents(True)

        self.panel_izq_layout.addWidget(self.logo)

        self.splitter.addWidget(self.panel_izq)
        self.panel_izq.setMaximumWidth(250)

        self.panel_der = QWidget()
        self.panel_der_layout = QVBoxLayout(self.panel_der)

        self.banner = QLabel()
        self.banner.setFixedHeight(32)
        self.banner.setAlignment(Qt.AlignCenter)

        self.banner.setStyleSheet("""
            QLabel {
                background-color: #1F3A5F;
                color: white;
                font-size: 13px;
                font-weight: 600;
                padding: 4px 10px;
                border: none;
                border-bottom: 2px solid #2E75B6;
                letter-spacing: 0.5px;
            }
        """)

        self.banner.setText(f"Bienvenido {self.usuario}")
        self.panel_der_layout.addWidget(self.banner)

        self.splitter.addWidget(self.panel_der)

        self.timer_inactividad = QTimer()
        self.timer_inactividad.setInterval(10 * 60 * 1000)
        self.timer_inactividad.timeout.connect(self.cerrar_por_inactividad)
        self.timer_inactividad.start()

        menubar = self.menuBar()

        toolbar = QToolBar()
        toolbar.setMovable(False)

        toolbar.setStyleSheet("""
            QToolBar {
                spacing: 8px;
                padding: 4px;
            }
        """)

        self.addToolBar(Qt.TopToolBarArea, toolbar)

        spacer = QWidget()
        spacer.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )
        toolbar.addWidget(spacer)

        accion_nueva = QAction("Nueva ventana", self)
        accion_nueva.setShortcut("Ctrl+N")
        accion_nueva.triggered.connect(self.abrir_nueva_ventana)

        toolbar.addAction(accion_nueva)
        btn_nueva = toolbar.widgetForAction(accion_nueva)

        btn_nueva.setStyleSheet("""
            QToolButton {
                background-color: #2E75B6;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }

            QToolButton:hover {
                background-color: #1F5A8A;
            }
        """)

        accion_salir = QAction("Salir", self)
        accion_salir.triggered.connect(self.cerrar_sesion)

        toolbar.addAction(accion_salir)

        btn_salir = toolbar.widgetForAction(accion_salir)

        btn_salir.setStyleSheet("""
            QToolButton {
                background-color: #C00000;
                color: white;
                font-weight: bold;
                padding: 6px 12px;
                border-radius: 4px;
            }

            QToolButton:hover {
                background-color: #7A0000;
            }
        """)

        self.menu_datos = menubar.addMenu("DATOS")
        self.menu_datos.addAction(QAction("Productos", self, triggered=self.abrir_productos))
        self.menu_datos.addAction(QAction("Transportistas", self, triggered=self.abrir_transportistas))
        self.menu_datos.addAction(QAction("Ubicaciones", self, triggered=self.abrir_ubicaciones))
        self.menu_datos.addAction(QAction("Almacenes", self, triggered=self.abrir_almacenes))
        self.menu_datos.addAction(QAction("Cilindros", self, triggered=self.abrir_cilindros))
        self.menu_datos.addAction(QAction("Propietarios", self, triggered=self.abrir_propietarios))
        self.menu_datos.addAction(QAction("Personal", self, triggered=self.abrir_usuarios))

        menu_func = menubar.addMenu("FUNCIONES")
        menu_func.addAction(QAction("Ingreso / Recarga (Proveedor)", self, triggered=self.abrir_entrada_salida))
        menu_func.addAction(QAction("Ingreso / Recarga Masiva", self, triggered=self.abrir_entrada_salida_masiva))
        menu_func.addAction(QAction("Despacho / Devolución [Almacén]", self, triggered=self.abrir_despacho_recepcion))
        menu_func.addSeparator()

        menu_func.addAction(
            QAction(
                "Modificar / Eliminar Movimiento",
                self,
                triggered=self.abrir_modificar_movimiento
            )
        )

        menu_inf = menubar.addMenu("INFORMES")
        menu_inf.addAction(QAction("Estado de Cilindros", self, triggered=self.ver_estado))
        menu_inf.addAction(QAction("Ingresos / Recargas", self, triggered=self.ver_entradas_salidas))
        menu_inf.addAction(QAction("Buscar Despacho / Devolución", self, triggered=self.ver_busqueda))
        menu_inf.addAction(QAction("Kardex por cilindro", self, triggered=self.ver_kardex))
        menu_inf.addAction(QAction("Dashboard", self, triggered=self.ver_dashboard))

        self.aplicar_permisos()
        self.showMaximized()

    def abrir_productos(self):
        self.set_view(ProductosUI())

    def abrir_transportistas(self):
        self.set_view(TransportistasUI())

    def abrir_ubicaciones(self):
        self.set_view(UbicacionesUI())

    def abrir_almacenes(self):
        self.set_view(AlmacenesUI())

    def abrir_cilindros(self):
        self.set_view(CilindrosUI())

    def abrir_propietarios(self):
        self.set_view(PropietariosUI())

    def abrir_usuarios(self):
        self.set_view(UsuariosUI())

    def abrir_entrada_salida(self):
        self.set_view(FuncEntradaSalidaUI())

    def abrir_entrada_salida_masiva(self):
        self.set_view(EntradaSalidaMasivoUI())

    def abrir_despacho_recepcion(self):
        self.set_view(FuncDespachoRecepcionUI())

    def abrir_modificar_movimiento(self):
        from ui.modificar_movimiento_ui import ModificarMovimientoUI
        self.set_view(ModificarMovimientoUI())

    def ver_entradas_salidas(self):
        self.set_view(ReporteEntradasSalidas())

    def ver_estado(self):
        self.set_view(ReporteEstadoCilindros())

    def ver_busqueda(self):
        self.set_view(ReporteMovimientos())

    def ver_kardex(self):
        self.set_view(KardexUI())

    def ver_dashboard(self):
        self.set_view(DashboardUI())

    def set_view(self, widget):
        for i in reversed(range(self.panel_der_layout.count())):
            item = self.panel_der_layout.itemAt(i)
            if item.widget() and item.widget() != self.banner:
                item.widget().setParent(None)

        titulo = widget.__class__.__name__

        nombres = {
            "ProductosUI": "Gestión de Productos",
            "TransportistasUI": "Gestión de Transportistas",
            "UbicacionesUI": "Gestión de Ubicaciones",
            "AlmacenesUI": "Gestión de Almacenes",
            "CilindrosUI": "Gestión de Cilindros",
            "UsuariosUI": "Gestión de Personal",
            "PropietariosUI": "Gestión de Propietarios",
            "FuncEntradaSalidaUI": "Ingreso / Recarga",
            "EntradaSalidaMasivoUI": "Ingreso / Recarga Masiva",
            "FuncDespachoRecepcionUI": "Despacho / Devolución",
            "ReporteEntradasSalidas": "Reporte de Ingresos / Recargas",
            "ReporteEstadoCilindros": "Estado de Cilindros",
            "ReporteMovimientos": "Búsqueda Avanzada - Despachos / Devoluciones",
            "KardexUI": "Kardex por Cilindro",
            "DashboardUI": "Dashboard"
        }

        titulo_legible = nombres.get(titulo, titulo)
        self.banner.setText(f"{titulo_legible}")
        self.panel_der_layout.addWidget(widget)

    def abrir_nueva_ventana(self):
        nueva = MainWindow(self.usuario)
        nueva.show()
        self.ventanas.append(nueva)

    def reset_timer(self):
        self.timer_inactividad.start()

    def mousePressEvent(self, event):
        self.reset_timer()
        super().mousePressEvent(event)

    def keyPressEvent(self, event):
        self.reset_timer()
        super().keyPressEvent(event)

    def cerrar_por_inactividad(self):
        from ui.login import Login

        print("Sesión cerrada por inactividad")

        for v in self.ventanas:
            v.close()

        self.close()

        self.login = Login()
        self.login.show()

    def cerrar_sesion(self):
        from ui.login import Login

        for v in self.ventanas:
            v.close()

        self.close()

        self.login = Login()
        self.login.show()

    def aplicar_permisos(self):
        USUARIOS_CON_DATOS = [
            "MANUEL NIFLA LL",
            "CESAR RAMIREZ MALDONADO",
            "MIGUEL BENITES "
        ]

        if self.usuario not in USUARIOS_CON_DATOS:
            self.menu_datos.setEnabled(False)