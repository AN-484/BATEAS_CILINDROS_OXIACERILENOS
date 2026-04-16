import requests

SUPABASE_URL = "https://qqnycxnnlzevniaxcbqf.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFxbnljeG5ubHpldm5pYXhjYnFmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzYxOTY1NjksImV4cCI6MjA5MTc3MjU2OX0.6gJU_cGm6ESHhD9IL0vbUHG-R1kajoCWnU0oXXlCk2Y"

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

TIMEOUT = 10


def _request(method, endpoint, params=None, json=None, extra_headers=None):
    url = f"{SUPABASE_URL}{endpoint}"

    headers = HEADERS.copy()
    if extra_headers:
        headers.update(extra_headers)

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            timeout=TIMEOUT
        )

        if response.status_code >= 400:
            print("Error API:")
            print("STATUS:", response.status_code)
            print("URL:", response.url)
            print("RESPUESTA:", response.text)
            return None

        if response.text.strip():
            try:
                return response.json()
            except Exception:
                return response.text

        return None

    except requests.exceptions.RequestException as e:
        print("Error de conexión con API:", e)
        return None
    except Exception as e:
        print("Error inesperado API:", e)
        return None


# =========================================================
# LOGIN / USUARIOS
# =========================================================

def obtener_usuario_por_dni(dni):
    params = {
        "dni": f"eq.{dni}",
        "select": "*",
        "limit": "1"
    }

    data = _request(
        "GET",
        "/rest/v1/usuarios",
        params=params
    )

    if data and len(data) > 0:
        return data[0]

    return None


def login_usuario(dni):
    return obtener_usuario_por_dni(dni)


# =========================================================
# CONSULTAS GENERALES
# =========================================================

def obtener_registros(tabla, filtros=None, select="*"):
    params = {"select": select}

    if filtros:
        params.update(filtros)

    data = _request("GET", f"/rest/v1/{tabla}", params=params)

    if data is None:
        return []

    return data


def obtener_registro_por_campo(tabla, campo, valor, select="*", limit=1):
    params = {
        campo: f"eq.{valor}",
        "select": select,
        "limit": str(limit)
    }

    data = _request("GET", f"/rest/v1/{tabla}", params=params)

    if data and len(data) > 0:
        return data[0]

    return None


def insertar_registro(tabla, payload):
    return _request(
        "POST",
        f"/rest/v1/{tabla}",
        json=payload,
        extra_headers={
            "Prefer": "return=representation"
        }
    )


def actualizar_registro(tabla, filtros, payload):
    params = {}
    if filtros:
        params.update(filtros)

    return _request(
        "PATCH",
        f"/rest/v1/{tabla}",
        params=params,
        json=payload,
        extra_headers={
            "Prefer": "return=representation"
        }
    )


def eliminar_registro(tabla, filtros):
    params = {}
    if filtros:
        params.update(filtros)

    return _request(
        "DELETE",
        f"/rest/v1/{tabla}",
        params=params,
        extra_headers={
            "Prefer": "return=representation"
        }
    )


# =========================================================
# CILINDROS
# =========================================================

def obtener_cilindro_por_codigo(codigo):
    return obtener_registro_por_campo("cilindros", "codigo", codigo)


def crear_cilindro(payload):
    return insertar_registro("cilindros", payload)


def actualizar_cilindro_api(codigo, payload):
    return actualizar_registro(
        "cilindros",
        {"codigo": f"eq.{codigo}"},
        payload
    )


def eliminar_cilindro_api(codigo):
    return eliminar_registro(
        "cilindros",
        {"codigo": f"eq.{codigo}"}
    )


# =========================================================
# ESTADO CILINDROS
# =========================================================

def obtener_estado_cilindro_por_codigo(cilindro):
    return obtener_registro_por_campo("estado_cilindros", "cilindro", cilindro)


def crear_estado_cilindro(payload):
    return insertar_registro("estado_cilindros", payload)


def actualizar_estado_cilindro_api(cilindro, payload):
    return actualizar_registro(
        "estado_cilindros",
        {"cilindro": f"eq.{cilindro}"},
        payload
    )


def eliminar_estado_cilindro_api(cilindro):
    return eliminar_registro(
        "estado_cilindros",
        {"cilindro": f"eq.{cilindro}"}
    )


# =========================================================
# TABLAS MAESTRAS
# =========================================================

def listar_productos():
    return obtener_registros("productos")


def crear_producto(payload):
    return insertar_registro("productos", payload)


def eliminar_producto_api(codigo):
    return eliminar_registro(
        "productos",
        {"codigo": f"eq.{codigo}"}
    )


def listar_transportistas():
    return obtener_registros("transportistas")


def crear_transportista(payload):
    return insertar_registro("transportistas", payload)


def eliminar_transportista_api(codigo):
    return eliminar_registro(
        "transportistas",
        {"codigo": f"eq.{codigo}"}
    )


def listar_ubicaciones():
    return obtener_registros("ubicaciones")


def crear_ubicacion(payload):
    return insertar_registro("ubicaciones", payload)


def eliminar_ubicacion_api(codigo):
    return eliminar_registro(
        "ubicaciones",
        {"codigo": f"eq.{codigo}"}
    )


def listar_almacenes():
    return obtener_registros("almacenes")


def crear_almacen(payload):
    return insertar_registro("almacenes", payload)


def eliminar_almacen_api(codigo):
    return eliminar_registro(
        "almacenes",
        {"codigo": f"eq.{codigo}"}
    )


def listar_propietarios():
    return obtener_registros("propietarios")


def crear_propietario(payload):
    return insertar_registro("propietarios", payload)


def eliminar_propietario_api(codigo):
    return eliminar_registro(
        "propietarios",
        {"codigo": f"eq.{codigo}"}
    )


def listar_usuarios():
    return obtener_registros("usuarios")


def crear_usuario(payload):
    return insertar_registro("usuarios", payload)


def eliminar_usuario_api(codigo):
    return eliminar_registro(
        "usuarios",
        {"codigo": f"eq.{codigo}"}
    )


def listar_cilindros():
    return obtener_registros("cilindros")


# =========================================================
# MOVIMIENTOS
# =========================================================

def crear_entrada_salida(payload):
    return insertar_registro("entradas_salidas", payload)


def listar_entradas_salidas(filtros=None):
    return obtener_registros("entradas_salidas", filtros=filtros)


def crear_movimiento_detalle(payload):
    return insertar_registro("movimientos_detalle", payload)


def listar_movimientos_detalle(filtros=None):
    return obtener_registros("movimientos_detalle", filtros=filtros)




    

def listar_usuarios():
    return obtener_registros("usuarios")