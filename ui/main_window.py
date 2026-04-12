from PySide6.QtWidgets import QMainWindow, QVBoxLayout
from PySide6.QtGui import QAction

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


#from PySide6.QtWidgets import QWidget


from ui.reportes.rep_estado_cilindros import ReporteEstadoCilindros
from ui.reportes.rep_entradas_salidas import ReporteEntradasSalidas


class MainWindow(QMainWindow):
    def __init__(self, usuario):
        super().__init__()
        self.setWindowTitle(f"SCCO: Cilindros - {usuario}")
        self.resize(1000, 600)

        # ===== CENTRAL WIDGET =====

        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.layout = QVBoxLayout(self.central)

        # SPLITTER (divide pantalla)
        self.splitter = QSplitter(Qt.Horizontal)

        self.layout.addWidget(self.splitter)
        # ===== PANEL IZQUIERDO =====

        self.panel_izq = QWidget()
        self.panel_izq_layout = QVBoxLayout(self.panel_izq)

        self.logo = QLabel()

        pixmap = QPixmap("img/boar.jpeg")  # tu imagen
        self.logo.setPixmap(pixmap)
        self.logo.setScaledContents(True)

        self.panel_izq_layout.addWidget(self.logo)

        self.splitter.addWidget(self.panel_izq)

        self.panel_izq.setMaximumWidth(250)
        # ===== PANEL DERECHO =====

        self.panel_der = QWidget()
        self.panel_der_layout = QVBoxLayout(self.panel_der)

        self.splitter.addWidget(self.panel_der)
        # =====  =====

        menubar = self.menuBar()

        # 📦 DATOS
        menu_datos = menubar.addMenu("DATOS")
        menu_datos.addAction(QAction("Productos", self, triggered=self.abrir_productos))
        menu_datos.addAction(QAction("Transportistas", self, triggered=self.abrir_transportistas))
        menu_datos.addAction(QAction("Ubicaciones", self, triggered=self.abrir_ubicaciones))
        menu_datos.addAction(QAction("Almacenes", self, triggered=self.abrir_almacenes))
        menu_datos.addAction(QAction("Cilindros", self, triggered=self.abrir_cilindros))
        menu_datos.addAction(QAction("Propietarios", self, triggered=self.abrir_propietarios))
        menu_datos.addAction(QAction("Personal", self, triggered=self.abrir_usuarios))

        # ⚙️ FUNCIONES
        menu_func = menubar.addMenu("FUNCIONES")
        menu_func.addAction(QAction("Ingreso / Recarga (Proveedor)", self, triggered=self.abrir_entrada_salida))
        menu_func.addAction(QAction("Ingreso / Recarga Masiva", self, triggered=self.abrir_entrada_salida_masiva))
        menu_func.addAction(QAction("Despacho / Devolución (Operación)", self, triggered=self.abrir_despacho_recepcion))

        # 📊 INFORMES
        menu_inf = menubar.addMenu("INFORMES")
        menu_inf.addAction(QAction("Estado de Cilindros", self, triggered=self.ver_estado))
        menu_inf.addAction(QAction("Ingresos / Recargas", self, triggered=self.ver_entradas_salidas))
        menu_inf.addAction(QAction("Búsqueda avanzada", self, triggered=self.ver_busqueda))
        menu_inf.addAction(QAction("Kardex por cilindro", self, triggered=self.ver_kardex))
        menu_inf.addAction(QAction("Dashboard", self, triggered=self.ver_dashboard))

    # ================= DATOS =================
    def abrir_productos(self): #self.w = ProductosUI(); self.w.show()
        self.set_view(ProductosUI())
    def abrir_transportistas(self): #self.w = TransportistasUI(); self.w.show()
        self.set_view(TransportistasUI())
    def abrir_ubicaciones(self): #self.w = UbicacionesUI(); self.w.show()
        self.set_view(UbicacionesUI())
    def abrir_almacenes(self): #self.w = AlmacenesUI(); self.w.show()
        self.set_view(AlmacenesUI())
    def abrir_cilindros(self): #self.w = CilindrosUI(); self.w.show()
        self.set_view(CilindrosUI())
    def abrir_propietarios(self): #self.w = PropietariosUI(); self.w.show()
        self.set_view(PropietariosUI())
    def abrir_usuarios(self): #self.w = UsuariosUI(); self.w.show()
        self.set_view(UsuariosUI())

    # ================= FUNCIONES =================
    def abrir_entrada_salida(self):
        #self.w = FuncEntradaSalidaUI()
        #self.w.show()
        self.set_view(FuncEntradaSalidaUI())

    def abrir_entrada_salida_masiva(self):
        self.set_view(EntradaSalidaMasivoUI())

    def abrir_despacho_recepcion(self):
        #self.w = FuncDespachoRecepcionUI()
        #self.w.show()
        self.set_view(FuncDespachoRecepcionUI())
    

    # ================= INFORMES =================
    def ver_entradas_salidas(self):
        #self.w = ReporteEntradasSalidas()
        #self.w.show()
        self.set_view(ReporteEntradasSalidas())

    def ver_estado(self):
        #self.w = ReporteEstadoCilindros()
        #self.w.show()
        self.set_view(ReporteEstadoCilindros())


    def ver_busqueda(self):
        #self.w = ReporteMovimientos()
        #self.w.show()
        self.set_view(ReporteMovimientos())

    def ver_kardex(self):
        #self.w = KardexUI()
        #self.w.show()
        self.set_view(KardexUI())

    def ver_dashboard(self):
        #self.w = DashboardUI()
        #self.w.show()
        self.set_view(DashboardUI())
    
    def set_view(self, widget):

        # limpiar contenido anterior
        for i in reversed(range(self.panel_der_layout.count())):
            item = self.panel_der_layout.itemAt(i)
            if item.widget():
                item.widget().setParent(None)

        # agregar nuevo contenido
        self.panel_der_layout.addWidget(widget)