# CRUD generico para cualquier tipo definido en catalogo_modelos.CATALOGO_DATOS:
# GET/POST/PUT/DELETE /api/{tipo}[/{registro_id}]. El {tipo} en la URL (p. ej.
# "clientes", "equipos") selecciona la configuracion y el repositorio a usar.
from fastapi import APIRouter, Depends, HTTPException, Request

from catalogo_modelos import (
    obtener_configuracion_tipo,
    obtener_configuracion_frontend,
    obtener_tipos,
)
from routers.auth import get_current_user
from servicios_datos import (
    actualizar_registro,
    crear_registro,
    eliminar_registro as borrar_registro,
    listar_registros,
    normalizar_payload,
    obtener_campos,
    obtener_modelo,
    serializar,
)

router = APIRouter()


@router.get("/api/tipos")
async def get_tipos():
    return obtener_tipos()


@router.get("/api/configuracion")
async def get_configuracion():
    return obtener_configuracion_frontend()


@router.get("/api/{tipo}")
async def obtener_registros(tipo: str):
    # Catch-all de 2 segmentos: por eso app.py registra este router al final,
    # despues de exportacion/alertas/facturacion_automatica.
    configuracion = obtener_configuracion_tipo(tipo)
    modelo = obtener_modelo(configuracion)
    campos = obtener_campos(configuracion)
    registros = listar_registros(modelo)

    return {
        "success": True,
        "datos": [serializar(registro, campos) for registro in registros],
    }


@router.post("/api/{tipo}")
async def agregar_registro(tipo: str, request: Request, usuario=Depends(get_current_user)):
    configuracion = obtener_configuracion_tipo(tipo)
    modelo = obtener_modelo(configuracion)
    campos = obtener_campos(configuracion)
    datos = await request.json()
    valores = normalizar_payload(configuracion, datos)
    registro = crear_registro(modelo, valores)

    return {
        "success": True,
        "message": "Registro agregado",
        "registro": serializar(registro, campos),
    }


@router.put("/api/{tipo}/{registro_id}")
async def editar_registro(tipo: str, registro_id: int, request: Request, usuario=Depends(get_current_user)):
    configuracion = obtener_configuracion_tipo(tipo)
    modelo = obtener_modelo(configuracion)
    campos = obtener_campos(configuracion)
    datos = await request.json()
    valores = normalizar_payload(configuracion, datos)
    registro = actualizar_registro(modelo, registro_id, valores)

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    return {
        "success": True,
        "message": "Registro actualizado",
        "registro": serializar(registro, campos),
    }


@router.delete("/api/{tipo}/{registro_id}")
async def eliminar_registro(tipo: str, registro_id: int, usuario=Depends(get_current_user)):
    configuracion = obtener_configuracion_tipo(tipo)
    modelo = obtener_modelo(configuracion)

    if not borrar_registro(modelo, registro_id):
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    return {"success": True, "message": "Registro eliminado"}
