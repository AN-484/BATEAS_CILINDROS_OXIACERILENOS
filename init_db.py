from database import engine, SessionLocal
from models import Base, Acceso

Base.metadata.create_all(engine)

db = SessionLocal()

if not db.query(Acceso).filter_by(usuario="admin").first():
    db.add(Acceso(usuario="admin", password="1234"))

db.commit()
db.close()

print("BD inicializada")