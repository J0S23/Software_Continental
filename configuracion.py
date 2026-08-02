# Configuracion global compartida por toda la app: rutas base y clave secreta.
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RUTA_STATIC = BASE_DIR / "static"
RUTA_TEMPLATES = BASE_DIR / "templates"
RUTA_VISTA = BASE_DIR / "vista"
RUTA_ADJUNTOS = BASE_DIR / "adjuntos"
RUTA_ADJUNTOS.mkdir(exist_ok=True)

SECRET_KEY = os.environ.get("CONTINENTAL_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "Falta la variable de entorno CONTINENTAL_SECRET_KEY. Definela antes "
        "de iniciar la aplicacion (ej. 'export CONTINENTAL_SECRET_KEY=...' o "
        "en tu .env) -- ya no se permite un valor por defecto, porque firma "
        "las cookies de sesion y un valor conocido permite forjarlas."
    )