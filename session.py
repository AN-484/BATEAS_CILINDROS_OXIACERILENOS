# session.py

usuario_actual = None


def set_usuario(usuario):
    global usuario_actual
    usuario_actual = usuario


def get_usuario():
    return usuario_actual