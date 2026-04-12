from database import SessionLocal
from models import Usuario, Producto, Transportista, Ubicacion, Almacen, Cilindro, Propietario

def seed():
    db = SessionLocal()

    # 🧑 USUARIOS (PERSONAL)
    usuarios = [
        Usuario(codigo="P001",dni="40500778", nombre="CESAR RAMIREZ MALDONADO", cargo="Supervisor"),
        Usuario(codigo="P002",dni="40780411", nombre="MIGUEL BENITES ", cargo="Asistente"),
        Usuario(codigo="P003",dni="43180022", nombre="BERNARDO CAYLLAHUE", cargo="Operario"),
        Usuario(codigo="P004",dni="40950681", nombre="CLAUDIO SISA", cargo="Auxiliar 1"),
        Usuario(codigo="P005",dni="45167507", nombre="FREDDY CUTIPA CHURA", cargo="Auxiliar 2"),
        Usuario(codigo="P006",dni="80385123", nombre="SANTOS LENGUANI QUISPE", cargo="Auxiliar 1"),
        Usuario(codigo="P007",dni="41727399", nombre="ANGEL CHOQUE", cargo="Auxiliar 1"),
        Usuario(codigo="P008",dni="72278030", nombre="WALTER SUNI", cargo="Auxiliar 2"),
        Usuario(codigo="P009",dni="48058310", nombre="RONAL VALENCIA QUISPE", cargo="Auxiliar 2"),
        Usuario(codigo="P010",dni="40858173", nombre="SEBASTIAN MAYHUA", cargo="Bodeguero"),
        Usuario(codigo="P011",dni="02172614", nombre="JOSE QUISPE", cargo="Bodeguero"),
        Usuario(codigo="P012",dni="24884512", nombre="SANTIAGO CUYO CCAPA", cargo="Bodeguero"),
        Usuario(codigo="P013",dni="71784498", nombre="ALDAIR DIAZ", cargo="Auxiliar 2"),
        Usuario(codigo="P014",dni="72029619", nombre="MANUEL NIFLA LL", cargo="Practicante"),
    ]

    # 📦 PRODUCTOS
    productos = [
        Producto(codigo="1000026903", nombre="OXIGENO INDUSTRIAL x 10M3", medida="LC"),
        Producto(codigo="1000000540", nombre="OXIGENO INDUSTRIAL x 6M3", medida="LC"),
        Producto(codigo="1000021484", nombre="OXIGENO MEDICINAL x 10M3", medida="LC"),
        Producto(codigo="1000000545", nombre="OXIGENO MEDICINAL x 1M3", medida="LC"),
        Producto(codigo="1000013946", nombre="OXIGENO MEDICINAL x 3M3", medida="LC"),
        Producto(codigo="1000000539", nombre="OXIGENO MEDICINAL x 6 M3", medida="LC"),
        Producto(codigo="1000019965", nombre="DIOXIDO DE CARBONO x 30KG", medida="LC"),
        Producto(codigo="1000000550", nombre="ACETILENO ABSORCION ATOMICA x 9KG", medida="LC"),
        Producto(codigo="1000000541", nombre="ACETILENO INDUSTRIAL x 9KG", medida="LC"),
        Producto(codigo="1000026797", nombre="CILINDRO P/OXIGENO MEDICINAL  x 10 M3", medida="UN"),
        Producto(codigo="1000026796", nombre="CILINDRO P/OXIGENOS", medida="UN"),
        Producto(codigo="1000031504", nombre="STARGOLD TUB 10M3", medida="LC"),
        Producto(codigo="1000019966", nombre="STARGOLD TUB 7M3", medida="LC"),
        Producto(codigo="1000030666", nombre="NITROGENO GAS x 10M3", medida="LC"),
    ]

    # 🚛 TRANSPORTISTAS
    transportistas = [
        Transportista(codigo="T001", nombre="EQUIPAT CAYLLOMA S.R.L", ruc="20611678810"),
        Transportista(codigo="T002", nombre="TRANSPORTES  & LOGISTICA HERRERA SAC", ruc="20606653663"),
    ]

    # PROPIETARIOS
    propietarios = [
        Propietario(codigo="PP01", nombre="BATEAS"),
        Propietario(codigo="PP02", nombre="LINDE"),
    ]

    # 📍 UBICACIONES
    ubicaciones = [
        Ubicacion(codigo="1001", nombre="SSOMA"),
        Ubicacion(codigo="1101", nombre="PULSO"),
        Ubicacion(codigo="1002", nombre="Lab. Quimico"),
        Ubicacion(codigo="1003", nombre="Lab. Metalúrgico"),
        Ubicacion(codigo="1004", nombre="TIC"),
        Ubicacion(codigo="1005", nombre="DHO"),
        Ubicacion(codigo="1006", nombre="Planeamiento"),
        Ubicacion(codigo="1007", nombre="Exploraciones"),
        Ubicacion(codigo="1008", nombre="RRCC"),
        Ubicacion(codigo="1009", nombre="Almacen"),
        Ubicacion(codigo="1010", nombre="Legal"),
        Ubicacion(codigo="1011", nombre="Seguridad Patrimonial"),
        Ubicacion(codigo="1012", nombre="Mina"),
        Ubicacion(codigo="1013", nombre="Geología"),
        Ubicacion(codigo="1014", nombre="Mantenimiento"),
        Ubicacion(codigo="1015", nombre="Planta"),
        Ubicacion(codigo="1016", nombre="Contabilidad y Tesoreria"),
        Ubicacion(codigo="1017", nombre="Administración Oficina"),
        Ubicacion(codigo="1018", nombre="Abastecimiento Tráfico"),
        Ubicacion(codigo="1019", nombre="Adm. Mina"),
        Ubicacion(codigo="1020", nombre="Costos y Presupuestos"),
        Ubicacion(codigo="1021", nombre="Proyecto"),
        Ubicacion(codigo="1022", nombre="Mantenimiento Planta"),
        Ubicacion(codigo="1099", nombre="Otros"),
    ]

    # 🏭 ALMACENES
    almacenes = [
        Almacen(codigo="0001", nombre="Almacén Principal"),
        Almacen(codigo="0002", nombre="Patio Principal"),
        Almacen(codigo="0004", nombre="Polvorin Accesorios"),
        Almacen(codigo="0005", nombre="Polvorin Explosivos"),
        Almacen(codigo="0007", nombre="Almacen Reactivos"),
        Almacen(codigo="0008", nombre="Almacen Cal"),
        Almacen(codigo="0009", nombre="Materiales Pesados"),
        Almacen(codigo="0010", nombre="Grifo"),
        Almacen(codigo="0011", nombre="Bolas de Acero"),
        Almacen(codigo="0013", nombre="Alm.Dist.Diesel"),
        Almacen(codigo="0014", nombre="Almacen Medicinas"),
        Almacen(codigo="0028", nombre="Almacen Proyectos"),
        Almacen(codigo="0028", nombre="Almacen Molycop"),
    ]

    # 🛢️ CILINDROS
    '''cilindros = [
        Cilindro(codigo="C001", propietario="LINDE", producto=""),
        Cilindro(codigo="C002", propietario="INDURA", producto=""),
        Cilindro(codigo="C003", propietario="PRAXAIR", producto=""),
    ]'''

    # 🔥 Guardar todo (evitando duplicados)
    def insertar(lista, modelo):
        for item in lista:
            existe = db.query(modelo).filter_by(codigo=item.codigo).first()
            if not existe:
                db.add(item)

    insertar(usuarios, Usuario)
    insertar(productos, Producto)
    insertar(transportistas, Transportista)
    insertar(ubicaciones, Ubicacion)
    insertar(almacenes, Almacen)
    insertar(propietarios,Propietario)
    #insertar(cilindros, Cilindro)

    db.commit()
    db.close()

    print("✅ Datos de prueba insertados correctamente")


if __name__ == "__main__":
    seed()