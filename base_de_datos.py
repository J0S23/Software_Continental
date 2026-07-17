from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

URL_BASE_DATOS = "sqlite:///./continental_app.db"

motor = create_engine(URL_BASE_DATOS, connect_args={"check_same_thread": False})
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)
Base = declarative_base()


def crear_tablas():
    Base.metadata.create_all(bind=motor)


# Alias de compatibilidad para archivos antiguos.
DATABASE_URL = URL_BASE_DATOS
engine = motor
SessionLocal = SesionLocal
