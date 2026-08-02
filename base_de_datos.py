# Configuracion central de SQLAlchemy: motor, fabrica de sesiones y clase Base
# de la que heredan todos los modelos ORM del proyecto. Tambien centraliza la
# configuracion de logging de toda la app (ver `logger` mas abajo).
import logging
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
RUTA_LOGS = BASE_DIR / "logs"
RUTA_LOGS.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(RUTA_LOGS / "app.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

# Logger reutilizable para toda la app: from base_de_datos import logger.
logger = logging.getLogger("continental")

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
