from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

#DATABASE_URL = "sqlite:///db.sqlite3"}

DATABASE_URL = "postgresql+psycopg2://postgres.qqnycxnnlzevniaxcbqf:Almacen2026*@aws-1-us-east-2.pooler.supabase.com:6543/postgres"

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()