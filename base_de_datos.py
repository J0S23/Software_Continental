# Configuracion central de SQLAlchemy: motor, fabrica de sesiones y clase Base
# de la que heredan todos los modelos ORM del proyecto.
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

URL_BASE_DATOS = "sqlite:///./continental_app.db"

# check_same_thread=False porque FastAPI puede atender una request en un thread
# distinto al que abrio la conexion (SQLite por defecto lo prohibe).
motor = create_engine(URL_BASE_DATOS, connect_args={"check_same_thread": False})
SesionLocal = sessionmaker(autocommit=False, autoflush=False, bind=motor)
Base = declarative_base()


def crear_tablas():
    # Crea las tablas que falten segun los modelos que hereden de Base.
    # No modifica tablas ya existentes (no es una migracion).
    Base.metadata.create_all(bind=motor)


# Alias de compatibilidad para archivos antiguos.
DATABASE_URL = URL_BASE_DATOS
engine = motor
SessionLocal = SesionLocal
