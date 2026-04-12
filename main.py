from database import crear_tablas
from ui.menu_principal import iniciar_menu

def main():

    crear_tablas()
    iniciar_menu()

if __name__ == "__main__":
    main()