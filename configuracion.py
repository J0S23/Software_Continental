# Configuracion global compartida por toda la app: rutas base, clave secreta
# y limiter de rate limiting (slowapi).
import os
from pathlib import Path

from dotenv import load_dotenv
from slowapi import Limiter
from slowapi.util import get_remote_address

BASE_DIR = Path(__file__).resolve().parent

# Carga las variables del archivo .env (si existe) al entorno del proceso,
# ANTES de leer cualquier os.environ.get(...) de aqui para abajo. Si no hay
# .env (ej. en un servidor donde las variables ya se definieron a mano o via
# el orquestador de despliegue), load_dotenv() simplemente no hace nada --
# no falla ni exige que el archivo exista.
load_dotenv(BASE_DIR / ".env")

RUTA_STATIC = BASE_DIR / "static"
RUTA_TEMPLATES = BASE_DIR / "templates"
RUTA_VISTA = BASE_DIR / "vista"
RUTA_ADJUNTOS = BASE_DIR / "adjuntos"
RUTA_ADJUNTOS.mkdir(exist_ok=True)

SECRET_KEY = os.environ.get("CONTINENTAL_SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError(
        "Falta la variable de entorno CONTINENTAL_SECRET_KEY. Definela en un "
        "archivo .env en la raiz del proyecto (ver .env.example) o expórtala "
        "en tu entorno antes de iniciar la aplicacion -- ya no se permite un "
        "valor por defecto, porque firma las cookies de sesion y un valor "
        "conocido permite forjarlas."
    )

# Origenes permitidos para CORS. A diferencia de CONTINENTAL_SECRET_KEY, esta
# si tiene un default (no rompe nada si falta): cubre el uso local actual
# (frontend servido por la misma app en 127.0.0.1/localhost:5000).
ORIGENES_PERMITIDOS = os.environ.get(
    "CONTINENTAL_CORS_ORIGENS", "http://127.0.0.1:5000,http://localhost:5000"
).split(",")

# Limiter global de slowapi (clave = IP del cliente). Se registra en app.py
# via app.state.limiter + SlowAPIMiddleware; se usa en routers/auth.py con
# el decorador @limiter.limit(...) sobre /auth/login.
limiter = Limiter(key_func=get_remote_address)