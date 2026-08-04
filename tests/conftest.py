import os

# Debe ir ANTES de importar cualquier modulo de la app: base_de_datos.py lee
# CONTINENTAL_DATABASE_URL al importarse (para fijar URL_BASE_DATOS) y
# configuracion.py exige CONTINENTAL_SECRET_KEY o lanza RuntimeError. Como
# load_dotenv() no sobreescribe variables ya definidas, esto tambien gana
# sobre cualquier .env real que exista en la maquina.
os.environ["CONTINENTAL_DATABASE_URL"] = "sqlite:///./test_continental.db"
os.environ["CONTINENTAL_SECRET_KEY"] = "clave-de-pruebas-no-usar-en-produccion"

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from passlib.context import CryptContext

from app import app
from base_de_datos import crear_tablas, motor
from Modulos.enums import EstadoAprobacion, RolUsuario
from Persistencia.UsuariosRepositorio import UsuariosRepositorio

RUTA_BD_PRUEBA = Path(__file__).resolve().parent.parent / "test_continental.db"

# Mismo esquema de hash que routers/auth.py y crear_admin_inicial.py.
contexto_password = CryptContext(schemes=["bcrypt"], deprecated="auto")


@pytest.fixture(scope="session", autouse=True)
def preparar_base_datos():
    crear_tablas()
    yield
    # Sin dispose() el engine deja el archivo sqlite abierto y unlink() falla
    # en Windows con PermissionError (el archivo "esta siendo usado por otro
    # proceso").
    motor.dispose()
    if RUTA_BD_PRUEBA.exists():
        RUTA_BD_PRUEBA.unlink()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def usuario_aprobado():
    """Crea un usuario ya aprobado (estado_aprobacion=APROBADO), igual que
    crear_admin_inicial.py, para poder probar login sin pasar por el flujo
    normal de registro + aprobacion manual. Devuelve el email y la
    contraseña en texto plano (la contraseña guardada en la base es el hash).
    """
    email = "usuario.prueba@test.com"
    password = "ClaveDePrueba123!"

    UsuariosRepositorio.agregar(
        nombre_usuario=email,
        email=email,
        rol=RolUsuario.ADMINISTRADOR_GENERAL,
        estado="Activo",
        password_hash=contexto_password.hash(password),
        estado_aprobacion=EstadoAprobacion.APROBADO,
    )

    return {"email": email, "password": password}
