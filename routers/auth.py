from fastapi import APIRouter, HTTPException, Response
from itsdangerous import URLSafeTimedSerializer, BadSignature
from passlib.context import CryptContext
from pydantic import BaseModel

from configuracion import SECRET_KEY
from Modulos.enums import RolUsuario, EstadoAprobacion
from Persistencia.UsuariosRepositorio import UsuariosRepositorio

router = APIRouter(prefix="/auth", tags=["auth"])

contexto_password = CryptContext(schemes=["bcrypt"], deprecated="auto")
serializador_sesion = URLSafeTimedSerializer(SECRET_KEY, salt="sesion-usuario")

NOMBRE_COOKIE_SESION = "session"
DURACION_SESION_SEGUNDOS = 60 * 60 * 8


class RegistroRequest(BaseModel):
    email: str
    contrasena: str
    rol: RolUsuario


class LoginRequest(BaseModel):
    email: str
    contrasena: str


@router.post("/registro")
async def registro(datos: RegistroRequest):
    if UsuariosRepositorio.obtener_por_email(datos.email):
        raise HTTPException(status_code=400, detail="Ya existe un usuario registrado con ese correo")

    password_hash = contexto_password.hash(datos.contrasena)
    UsuariosRepositorio.agregar(
        nombre_usuario=datos.email,
        email=datos.email,
        rol=datos.rol,
        estado="Activo",
        password_hash=password_hash,
        estado_aprobacion=EstadoAprobacion.PENDIENTE,
    )

    return {"success": True, "message": "Registro recibido, pendiente de aprobación"}


@router.post("/login")
async def login(datos: LoginRequest, response: Response):
    usuario = UsuariosRepositorio.obtener_por_email(datos.email)
    if not usuario or not usuario.password_hash or not contexto_password.verify(datos.contrasena, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    if usuario.estado_aprobacion != EstadoAprobacion.APROBADO:
        if usuario.estado_aprobacion == EstadoAprobacion.RECHAZADO:
            mensaje = "Tu registro fue rechazado. Contacta a un administrador."
        else:
            mensaje = "Tu registro aún está pendiente de aprobación."
        raise HTTPException(status_code=403, detail=mensaje)

    token_sesion = serializador_sesion.dumps({
        "usuario_id": usuario.id,
        "email": usuario.email,
        "rol": usuario.rol.value,
    })

    response.set_cookie(
        key=NOMBRE_COOKIE_SESION,
        value=token_sesion,
        httponly=True,
        samesite="lax",
        max_age=DURACION_SESION_SEGUNDOS,
    )

    return {"success": True, "message": "Sesión iniciada", "email": usuario.email, "rol": usuario.rol.value}


def leer_sesion(token_sesion: str):
    try:
        return serializador_sesion.loads(token_sesion, max_age=DURACION_SESION_SEGUNDOS)
    except BadSignature:
        return None
