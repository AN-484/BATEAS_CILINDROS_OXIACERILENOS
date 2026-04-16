# session.py

usuario_actual = None


class UsuarioSesion:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)


def set_usuario(usuario):
    global usuario_actual

    # si viene como dict (API), lo convertimos a objeto
    if isinstance(usuario, dict):
        usuario_actual = UsuarioSesion(usuario)
    else:
        usuario_actual = usuario


def get_usuario():
    return usuario_actual