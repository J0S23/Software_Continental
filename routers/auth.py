# Registro, login y sesion de usuarios. La sesion se guarda en una cookie
# firmada (no en el servidor), asi que no hace falta tabla de sesiones.
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from itsdangerous import URLSafeTimedSerializer, BadSignature
from passlib.context import CryptContext
from pydantic import BaseModel

from configuracion import SECRET_KEY
from Modulos.enums import RolUsuario, EstadoAprobacion
from Persistencia.UsuariosRepositorio import UsuariosRepositorio

router = APIRouter(prefix="/auth", tags=["auth"])

contexto_password = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Firma/verifica el contenido de la cookie de sesion (no la encripta, solo
# garantiza que no fue alterada); ver leer_sesion() mas abajo.
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
    # Queda con estado_aprobacion=PENDIENTE: no puede iniciar sesion hasta que
    # un administrador lo apruebe (ver UsuariosRepositorio.obtener_pendientes).
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

    # El contenido va firmado pero legible (no cifrado): no meter datos sensibles aqui.
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
    # Devuelve None si el token fue alterado o si excede max_age (sesion expirada).
    try:
        return serializador_sesion.loads(token_sesion, max_age=DURACION_SESION_SEGUNDOS)
    except BadSignature:
        return None


def get_current_user(request: Request):
    """Dependencia de FastAPI: lee la cookie de sesion, la valida y devuelve
    el Usuarios correspondiente. Lanza 401 si no hay cookie, si es invalida/
    expirada o si el usuario ya no existe. Usar como Depends(get_current_user)
    en cualquier endpoint que deba exigir sesion iniciada."""
    token_sesion = request.cookies.get(NOMBRE_COOKIE_SESION)
    if not token_sesion:
        raise HTTPException(status_code=401, detail="No has iniciado sesión")

    datos_sesion = leer_sesion(token_sesion)
    if not datos_sesion:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")

    usuario = UsuariosRepositorio.obtener_por_id(datos_sesion["usuario_id"])
    if not usuario:
        raise HTTPException(status_code=401, detail="Sesión inválida o expirada")

    return usuario


def requerir_administrador(usuario=Depends(get_current_user)):
    """Dependencia que ademas exige rol Administrador general. Usarla en vez
    de get_current_user cuando el endpoint es de administracion."""
    if usuario.rol != RolUsuario.ADMINISTRADOR_GENERAL:
        raise HTTPException(status_code=403, detail="Requiere rol Administrador general")
    return usuario


def _serializar_usuario(usuario):
    # No incluye password_hash: este endpoint lo consume el admin, no hace falta exponerlo.
    return {
        "id": usuario.id,
        "nombre_usuario": usuario.nombre_usuario,
        "email": usuario.email,
        "rol": usuario.rol.value if usuario.rol else None,
        "estado": usuario.estado,
        "estado_aprobacion": usuario.estado_aprobacion.value if usuario.estado_aprobacion else None,
    }


class AprobarRequest(BaseModel):
    rol: RolUsuario


@router.get("/pendientes")
async def obtener_pendientes(admin=Depends(requerir_administrador)):
    pendientes = UsuariosRepositorio.obtener_pendientes()
    return {"success": True, "usuarios": [_serializar_usuario(u) for u in pendientes]}

@router.post("/{usuario_id}/aprobar")
async def aprobar_usuario(usuario_id: int, datos: AprobarRequest, admin=Depends(requerir_administrador)):
    # El admin decide el rol final al aprobar (puede diferir del que el
    # usuario pidio en el registro).
    usuario = UsuariosRepositorio.actualizar(
        usuario_id, rol=datos.rol, estado_aprobacion=EstadoAprobacion.APROBADO
    )
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"success": True, "message": "Usuario aprobado", "usuario": _serializar_usuario(usuario)}


@router.post("/{usuario_id}/rechazar")
async def rechazar_usuario(usuario_id: int, admin=Depends(requerir_administrador)):
    usuario = UsuariosRepositorio.actualizar(usuario_id, estado_aprobacion=EstadoAprobacion.RECHAZADO)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {"success": True, "message": "Usuario rechazado", "usuario": _serializar_usuario(usuario)}
