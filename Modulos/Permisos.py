# Matriz de permisos por rol para el CRUD generico de routers/datos.py.
#
# Reglas fijas (no dependen de esta matriz, se aplican aparte):
#   - Lectura (GET): cualquier usuario logueado, sin importar el rol.
#   - Eliminar (DELETE): solo Administrador general, para TODOS los tipos
#    "Eliminar registros, solo para administrador".
#   - "usuarios" es un caso especial: solo Administrador general puede
#     crear/editar (ademas de eliminar). No sigue la matriz de abajo porque
#     un rol no-admin editando/creando cuentas podria escalar su propio rol.
from fastapi import HTTPException

from Modulos.enums import RolUsuario

# Tipos que solo el Administrador general puede crear/editar, sin excepcion.
TIPOS_SOLO_ADMIN_ESCRITURA = {"usuarios"}

# tipo -> roles (ademas de Administrador general, que siempre puede todo)
# habilitados para crear/editar (POST/PUT) ese tipo. Un tipo del catalogo
# que no aparezca aqui (y que tampoco este en TIPOS_SOLO_ADMIN_ESCRITURA)
# queda cerrado a cualquier no-admin: falla cerrado, no abierto.
PERMISOS_CREAR_EDITAR = {
    "clientes": {RolUsuario.COORDINACION_RENTA, RolUsuario.EJECUTIVO_COMERCIAL},
    "sedes": {RolUsuario.COORDINACION_RENTA, RolUsuario.EJECUTIVO_COMERCIAL},
    "equipos": {RolUsuario.COORDINACION_RENTA, RolUsuario.SERVICIO_TECNICO},
    "contrato_equipos": {RolUsuario.COORDINACION_RENTA},
    "contratos": {RolUsuario.COORDINACION_RENTA, RolUsuario.EJECUTIVO_COMERCIAL},
    "cambios_retiros": {RolUsuario.SERVICIO_TECNICO},
    "equipos_respaldo": {RolUsuario.SERVICIO_TECNICO},
    "lecturas": {RolUsuario.COORDINACION_RENTA, RolUsuario.SERVICIO_TECNICO},
    "servicios": {RolUsuario.SERVICIO_TECNICO},
    "mantenimientos_preventivos": {RolUsuario.SERVICIO_TECNICO},
    "repuestos": {RolUsuario.LOGISTICA_ALMACEN, RolUsuario.SERVICIO_TECNICO},
    "insumos": {RolUsuario.LOGISTICA_ALMACEN},
    "tipos_insumo": {RolUsuario.LOGISTICA_ALMACEN},
    "entregas_toner": {RolUsuario.LOGISTICA_ALMACEN, RolUsuario.SERVICIO_TECNICO},
    "costos": {
        RolUsuario.SUBGERENCIA_FINANCIERA,
        RolUsuario.SERVICIO_TECNICO,
        RolUsuario.LOGISTICA_ALMACEN,
    },
    "facturacion": {RolUsuario.FACTURACION, RolUsuario.SUBGERENCIA_FINANCIERA},
    "rentabilidad": {RolUsuario.SUBGERENCIA_FINANCIERA},
}


def _es_administrador(usuario):
    return usuario.rol == RolUsuario.ADMINISTRADOR_GENERAL


def verificar_permiso_escritura(tipo, usuario):
    """Bloquea (403) un POST/PUT sobre 'tipo' si el rol de 'usuario' no esta
    autorizado. Administrador general siempre puede, sobre cualquier tipo."""
    if _es_administrador(usuario):
        return

    clave_tipo = tipo.lower()

    if clave_tipo in TIPOS_SOLO_ADMIN_ESCRITURA:
        raise HTTPException(
            status_code=403,
            detail=f"Solo un administrador general puede crear o editar '{tipo}'",
        )

    roles_permitidos = PERMISOS_CREAR_EDITAR.get(clave_tipo)
    if not roles_permitidos or usuario.rol not in roles_permitidos:
        raise HTTPException(
            status_code=403,
            detail=f"Tu rol ({usuario.rol.value}) no tiene permiso para crear o editar '{tipo}'",
        )


def verificar_permiso_eliminar(usuario):
    """DELETE: solo Administrador general, para todos los tipos sin excepcion
    (incluye 'usuarios')."""
    if not _es_administrador(usuario):
        raise HTTPException(
            status_code=403,
            detail="Solo un administrador general puede eliminar registros",
        )