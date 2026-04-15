from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

USER = "postgres.qqnycxnnlzevniaxcbqf"
PASSWORD = "Almacen2026*"
HOST = "aws-1-us-east-2.pooler.supabase.com"
DB = "postgres"

def crear_engine_con_fallback():
    puertos = [443,6543]

    for puerto in puertos:
        try:
            print(f"Intentando conectar por puerto {puerto}...")

            DATABASE_URL = (
                f"postgresql+psycopg2://{USER}:{PASSWORD}@"
                f"{HOST}:{puerto}/{DB}"
            )

            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_recycle=300,
                connect_args={
                    "connect_timeout": 5,
                    "sslmode": "require"
                },
                echo=False
            )

            # probar conexión real
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))

            print(f"Conectado correctamente por puerto {puerto}")
            return engine

        except OperationalError:
            print(f"No se pudo conectar por puerto {puerto}")

    raise Exception(
        "No se pudo conectar a la base de datos.\n"
        "Verifique su conexión a Internet o la red."
    )

engine = crear_engine_con_fallback()

SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()