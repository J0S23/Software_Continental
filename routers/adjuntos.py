# Sube/lista/descarga/elimina adjuntos genericos (ver Modulos/Adjuntos.py).
# Se registra ANTES de routers/datos.py por el mismo motivo que
# alertas/exportacion/facturacion_automatica: routers/datos.py define
# catch-alls GET /api/{tipo} y PUT|DELETE /api/{tipo}/{registro_id} que
# interceptarian estas rutas si se registrara primero.
import uuid
from pathlib import PurePosixPath

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from catalogo_modelos import obtener_tipos
from configuracion import RUTA_ADJUNTOS
from Persistencia.AdjuntosRepositorio import AdjuntosRepositorio
from routers.auth import get_current_user

router = APIRouter()

# Formatos recomendados (PDF, JPG, PNG, Excel, Word), con sus variantes de extension mas usuales.
EXTENSIONES_PERMITIDAS = {
    ".pdf", ".jpg", ".jpeg", ".png", ".xls", ".xlsx", ".doc", ".docx",
}

# Limite por archivo para no llenar el disco local por accidente.
TAMANO_MAXIMO_BYTES = 10 * 1024 * 1024


def _serializar(adjunto):
    return {
        "id": adjunto.id,
        "tipo_entidad": adjunto.tipo_entidad,
        "entidad_id": adjunto.entidad_id,
        "tipo_documento": adjunto.tipo_documento,
        "nombre_original": adjunto.nombre_original,
        "content_type": adjunto.content_type,
        "tamano_bytes": adjunto.tamano_bytes,
        "subido_por": adjunto.subido_por,
        "observaciones": adjunto.observaciones,
        "fecha_subida": adjunto.fecha_subida.isoformat() if adjunto.fecha_subida else None,
        "url_descarga": f"/api/adjuntos/{adjunto.id}/descargar",
    }


@router.post("/api/adjuntos")
async def subir_adjunto(
    tipo_entidad: str = Form(...),
    entidad_id: int = Form(...),
    tipo_documento: str = Form(None),
    observaciones: str = Form(None),
    archivo: UploadFile = File(...),
    usuario=Depends(get_current_user),
):
    #Sube un archivo y crea su registro de Adjuntos. tipo_entidad debe ser una de las claves de catalogo_modelos.CATALOGO_DATOS (clientes, equipos,
    #contratos, lecturas, facturacion, etc), para poder despues listarlo con GET /api/adjuntos?tipo_entidad=...&entidad_id=...
    tipos_validos = obtener_tipos()
    if tipo_entidad not in tipos_validos:
        opciones = ", ".join(sorted(tipos_validos.keys()))
        raise HTTPException(
            status_code=400,
            detail=f"tipo_entidad invalido. Usa uno de: {opciones}",
        )

    extension = PurePosixPath(archivo.filename or "").suffix.lower()
    if extension not in EXTENSIONES_PERMITIDAS:
        opciones = ", ".join(sorted(EXTENSIONES_PERMITIDAS))
        raise HTTPException(
            status_code=400,
            detail=f"Extension no permitida. Usa una de: {opciones}",
        )

    contenido = await archivo.read()
    if len(contenido) > TAMANO_MAXIMO_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"El archivo supera el limite de {TAMANO_MAXIMO_BYTES // (1024 * 1024)} MB",
        )

    # Nombre generado (no el original) para evitar colisiones y path
    # traversal; nombre_original se conserva solo como metadato a mostrar.
    nombre_archivo = f"{uuid.uuid4().hex}{extension}"
    (RUTA_ADJUNTOS / nombre_archivo).write_bytes(contenido)

    nuevo_adjunto = AdjuntosRepositorio.agregar(
        tipo_entidad=tipo_entidad,
        entidad_id=entidad_id,
        nombre_original=archivo.filename,
        nombre_archivo=nombre_archivo,
        tipo_documento=tipo_documento,
        content_type=archivo.content_type,
        tamano_bytes=len(contenido),
        subido_por=usuario.email,
        observaciones=observaciones,
    )

    return {"success": True, "message": "Adjunto subido", "adjunto": _serializar(nuevo_adjunto)}


@router.get("/api/adjuntos")
async def listar_adjuntos(tipo_entidad: str, entidad_id: int):
    adjuntos = AdjuntosRepositorio.obtener_por_entidad(tipo_entidad, entidad_id)
    return {"success": True, "adjuntos": [_serializar(a) for a in adjuntos]}


@router.get("/api/adjuntos/{adjunto_id}/descargar")
async def descargar_adjunto(adjunto_id: int):
    adjunto = AdjuntosRepositorio.obtener_por_id(adjunto_id)
    if not adjunto:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")

    ruta_archivo = RUTA_ADJUNTOS / adjunto.nombre_archivo
    if not ruta_archivo.exists():
        raise HTTPException(status_code=404, detail="El archivo ya no existe en disco")

    return FileResponse(
        ruta_archivo,
        media_type=adjunto.content_type or "application/octet-stream",
        filename=adjunto.nombre_original,
    )


@router.delete("/api/adjuntos/{adjunto_id}")
async def eliminar_adjunto(adjunto_id: int, usuario=Depends(get_current_user)):
    nombre_archivo = AdjuntosRepositorio.eliminar(adjunto_id)
    if not nombre_archivo:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")

    ruta_archivo = RUTA_ADJUNTOS / nombre_archivo
    if ruta_archivo.exists():
        ruta_archivo.unlink()

    return {"success": True, "message": "Adjunto eliminado"}