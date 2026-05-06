from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QSplitter,
    QSizePolicy,
    QToolBar
)

from PySide6.QtGui import (
    QAction,
    QPixmap,
    QShortcut,
    QKeySequence
)

from PySide6.QtCore import (
    Qt,
    QTimer
)

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
from ui.despacho_recepcion_masivo_ui import DespachoRecepcionMasivoUI
from ui.func_entrada_salida_ui import FuncEntradaSalidaUI
from ui.entrada_salida_masivo import EntradaSalidaMasivoUI

# REPORTES
from ui.reportes.rep_movimientos import ReporteMovimientos
from ui.reportes.rep_kardex import KardexUI
from ui.reportes.dashboard import DashboardUI
from ui.reportes.rep_estado_cilindros import ReporteEstadoCilindros
from ui.reportes.rep_entradas_salidas import ReporteEntradasSalidas

from utils import ruta_recurso


class MainWindow(QMainWindow):

    def __init__(self, usuario):

        super().__init__()

        self.usuario = usuario
        self.ventanas = []

        # =====================================================
        # CONFIGURACION PRINCIPAL
        # =====================================================

        self.setWindowTitle(
            f"SCCO :  Cilindros   -   {usuario}"
        )

        # 🔥 QUITAR BOTON MAXIMIZAR
        self.setWindowFlags(
            Qt.Window |
            Qt.CustomizeWindowHint |
            Qt.WindowTitleHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowMinimizeButtonHint
        )

        # =====================================================
        # WIDGET CENTRAL
        # =====================================================

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.layout = QVBoxLayout(self.central)

        self.splitter = QSplitter(Qt.Horizontal)
        self.layout.addWidget(self.splitter)

        # =====================================================
        # PANEL IZQUIERDO
        # =====================================================

        self.panel_izq = QWidget()
        self.panel_izq_layout = QVBoxLayout(self.panel_izq)

        self.logo = QLabel()

        ruta = ruta_recurso("img/boar2.png")

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

        # =====================================================
        # PANEL DERECHO
        # =====================================================

        self.panel_der = QWidget()

        self.panel_der_layout = QVBoxLayout(
            self.panel_der
        )

        self.banner = QLabel()

        self.banner.setFixedHeight(32)

        self.banner.setAlignment(
            Qt.AlignCenter
        )

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

        self.banner.setText(
            f"Bienvenido {self.usuario}"
        )

        self.panel_der_layout.addWidget(
            self.banner
        )

        self.splitter.addWidget(
            self.panel_der
        )

        # =====================================================
        # TIMER INACTIVIDAD
        # =====================================================

        self.timer_inactividad = QTimer()

        self.timer_inactividad.setInterval(
            30 * 60 * 1000
        )

        self.timer_inactividad.timeout.connect(
            self.cerrar_por_inactividad
        )

        self.timer_inactividad.start()

        # =====================================================
        # MENU
        # =====================================================

        menubar = self.menuBar()

        # =====================================================
        # TOOLBAR
        # =====================================================

        toolbar = QToolBar()

        toolbar.setMovable(False)

        toolbar.setStyleSheet("""
            QToolBar {
                spacing: 8px;
                padding: 4px;
            }
        """)

        self.addToolBar(
            Qt.TopToolBarArea,
            toolbar
        )

        spacer = QWidget()

        spacer.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred
        )

        toolbar.addWidget(spacer)

        # =====================================================
        # BOTON NUEVA VENTANA
        # =====================================================

        accion_nueva = QAction(
            "Nueva ventana",
            self
        )

        accion_nueva.setShortcut(
            "Ctrl+N"
        )

        accion_nueva.triggered.connect(
            self.abrir_nueva_ventana
        )

        toolbar.addAction(
            accion_nueva
        )

        btn_nueva = toolbar.widgetForAction(
            accion_nueva
        )

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

        # =====================================================
        # BOTON SALIR
        # =====================================================

        accion_salir = QAction(
            "Salir",
            self
        )

        accion_salir.triggered.connect(
            self.cerrar_sesion
        )

        toolbar.addAction(
            accion_salir
        )

        btn_salir = toolbar.widgetForAction(
            accion_salir
        )

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

        # =====================================================
        # MENU DATOS
        # =====================================================

        self.menu_datos = menubar.addMenu("DATOS")

        self.menu_datos.addAction(
            QAction(
                "Productos",
                self,
                triggered=self.abrir_productos
            )
        )

        self.menu_datos.addAction(
            QAction(
                "Transportistas",
                self,
                triggered=self.abrir_transportistas
            )
        )

        self.menu_datos.addAction(
            QAction(
                "Ubicaciones",
                self,
                triggered=self.abrir_ubicaciones
            )
        )

        self.menu_datos.addAction(
            QAction(
                "Almacenes",
                self,
                triggered=self.abrir_almacenes
            )
        )

        self.menu_datos.addAction(
            QAction(
                "Cilindros",
                self,
                triggered=self.abrir_cilindros
            )
        )

        self.menu_datos.addAction(
            QAction(
                "Propietarios",
                self,
                triggered=self.abrir_propietarios
            )
        )

        self.menu_datos.addAction(
            QAction(
                "Personal",
                self,
                triggered=self.abrir_usuarios
            )
        )

        # =====================================================
        # MENU FUNCIONES
        # =====================================================

        menu_func = menubar.addMenu(
            "FUNCIONES"
        )

        menu_func.addAction(
            QAction(
                "Ingreso / Recarga (Proveedor)",
                self,
                triggered=self.abrir_entrada_salida
            )
        )

        menu_func.addAction(
            QAction(
                "Ingreso / Recarga |Masiva|",
                self,
                triggered=self.abrir_entrada_salida_masiva
            )
        )

        menu_func.addAction(
            QAction(
                "Despacho / Devolución [Almacén]",
                self,
                triggered=self.abrir_despacho_recepcion
            )
        )

        menu_func.addAction(
            QAction(
                "Despacho / Devolución [Almacén] |Masiva|",
                self,
                triggered=self.abrir_despacho_recepcion_masiva
            )
        )

        menu_func.addSeparator()

        menu_func.addAction(
            QAction(
                "Modificar / Eliminar Movimiento",
                self,
                triggered=self.abrir_modificar_movimiento
            )
        )

        # =====================================================
        # MENU INFORMES
        # =====================================================

        menu_inf = menubar.addMenu(
            "INFORMES"
        )

        menu_inf.addAction(
            QAction(
                "Estado de Cilindros",
                self,
                triggered=self.ver_estado
            )
        )

        menu_inf.addAction(
            QAction(
                "Ingresos / Recargas",
                self,
                triggered=self.ver_entradas_salidas
            )
        )

        menu_inf.addAction(
            QAction(
                "Buscar Despacho / Devolución",
                self,
                triggered=self.ver_busqueda
            )
        )

        menu_inf.addAction(
            QAction(
                "Kardex por cilindro",
                self,
                triggered=self.ver_kardex
            )
        )

        menu_inf.addAction(
            QAction(
                "Dashboard",
                self,
                triggered=self.ver_dashboard
            )
        )

        # =====================================================
        # PERMISOS
        # =====================================================

        self.aplicar_permisos()

        # =====================================================
        # ABRIR MAXIMIZADO
        # =====================================================

        self.showMaximized()

        # =====================================================
        # BLOQUEAR TAMAÑO
        # =====================================================

        QTimer.singleShot(
            100,
            self.bloquear_tamano
        )

    # =====================================================
    # BLOQUEAR REDIMENSIONAMIENTO
    # =====================================================

    def bloquear_tamano(self):

        self.setFixedSize(
            self.size()
        )

    # =====================================================
    # ABRIR VISTAS
    # =====================================================

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

    def abrir_despacho_recepcion_masiva(self):
        self.set_view(DespachoRecepcionMasivoUI())

    def abrir_modificar_movimiento(self):

        from ui.modificar_movimiento_ui import (
            ModificarMovimientoUI
        )

        self.set_view(
            ModificarMovimientoUI()
        )

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

    # =====================================================
    # CAMBIAR VISTA
    # =====================================================

    def set_view(self, widget):

        for i in reversed(
            range(
                self.panel_der_layout.count()
            )
        ):

            item = self.panel_der_layout.itemAt(i)

            if (
                item.widget()
                and item.widget() != self.banner
            ):
                item.widget().setParent(None)

        titulo = widget.__class__.__name__

        nombres = {

            "ProductosUI":
                "Gestión de Productos",

            "TransportistasUI":
                "Gestión de Transportistas",

            "UbicacionesUI":
                "Gestión de Ubicaciones",

            "AlmacenesUI":
                "Gestión de Almacenes",

            "CilindrosUI":
                "Gestión de Cilindros",

            "UsuariosUI":
                "Gestión de Personal",

            "PropietariosUI":
                "Gestión de Propietarios",

            "FuncEntradaSalidaUI":
                "Ingreso / Recarga",

            "EntradaSalidaMasivoUI":
                "Ingreso / Recarga Masiva",

            "FuncDespachoRecepcionUI":
                "Despacho / Devolución",

            "DespachoRecepcionMasivoUI":
                "Despacho / Devolución Masiva",

            "ReporteEntradasSalidas":
                "Reporte de Ingresos / Recargas",

            "ReporteEstadoCilindros":
                "Estado de Cilindros",

            "ReporteMovimientos":
                "Búsqueda Avanzada - Despachos / Devoluciones",

            "KardexUI":
                "Kardex por Cilindro",

            "DashboardUI":
                "Dashboard"
        }

        titulo_legible = nombres.get(
            titulo,
            titulo
        )

        self.banner.setText(
            f"{titulo_legible}"
        )

        self.panel_der_layout.addWidget(
            widget
        )

    # =====================================================
    # NUEVA VENTANA
    # =====================================================

    def abrir_nueva_ventana(self):

        nueva = MainWindow(self.usuario)

        nueva.show()

        self.ventanas.append(
            nueva
        )

    # =====================================================
    # TIMER
    # =====================================================

    def reset_timer(self):

        self.timer_inactividad.start()

    def mousePressEvent(self, event):

        self.reset_timer()

        super().mousePressEvent(event)

    def keyPressEvent(self, event):

        self.reset_timer()

        super().keyPressEvent(event)

    # =====================================================
    # CERRAR POR INACTIVIDAD
    # =====================================================

    def cerrar_por_inactividad(self):

        from ui.login import Login

        print(
            "Sesión cerrada por inactividad"
        )

        for v in self.ventanas:
            v.close()

        self.close()

        self.login = Login()

        self.login.show()

    # =====================================================
    # CERRAR SESION
    # =====================================================

    def cerrar_sesion(self):

        from ui.login import Login

        for v in self.ventanas:
            v.close()

        self.close()

        self.login = Login()

        self.login.show()

    # =====================================================
    # PERMISOS
    # =====================================================

    def aplicar_permisos(self):

        USUARIOS_CON_DATOS = [

            "MANUEL NIFLA LL",

            "CESAR RAMIREZ MALDONADO",

            "MIGUEL BENITES "
        ]

        if self.usuario not in USUARIOS_CON_DATOS:

            self.menu_datos.setEnabled(False)