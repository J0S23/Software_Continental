import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RUTA_STATIC = BASE_DIR / "static"
RUTA_TEMPLATES = BASE_DIR / "templates"
RUTA_VISTA = BASE_DIR / "vista"

# En produccion, definir CONTINENTAL_SECRET_KEY como variable de entorno.
SECRET_KEY = os.environ.get("CONTINENTAL_SECRET_KEY", "clave-de-desarrollo-cambiar-en-produccion")
