# Configuracion central de SQLAlchemy: motor, fabrica de sesiones y clase Base
# de la que heredan todos los modelos ORM del proyecto. Tambien centraliza la
# configuracion de logging de toda la app (ver `logger` mas abajo).
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent

# Carga las variables del archivo .env (si existe) al entorno del proceso,
# ANTES de leer CONTINENTAL_DATABASE_URL mas abajo. Se llama aqui tambien
# (y no solo en configuracion.py) para que esto funcione sin importar el
# orden de imports -- load_dotenv() no hace nada si el .env no existe.
load_dotenv(BASE_DIR / ".env")

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

URL_BASE_DATOS = os.environ.get(
    "CONTINENTAL_DATABASE_URL", "sqlite:///./continental_app.db"
)

# check_same_thread=False porque FastAPI puede atender una request en un thread
# distinto al que abrio la conexion (SQLite por defecto lo prohibe). Otros
# motores (Postgres, MySQL, etc.) no aceptan este argumento.
CONNECT_ARGS = (
    {"check_same_thread": False} if URL_BASE_DATOS.startswith("sqlite") else {}
)
motor = create_engine(URL_BASE_DATOS, connect_args=CONNECT_ARGS)
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
