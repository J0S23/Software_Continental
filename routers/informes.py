# Endpoints JSON de los informes mensuales. Las funciones de calculo ya existen en
# Servicio/Informes_mensuales.py; este router solo las expone via HTTP.
# Requieren sesion iniciada porque traen datos financieros y de cartera.
from fastapi import APIRouter, Depends, HTTPException

from routers.auth import get_current_user
from Servicio.Informes_mensuales import (
    informe_general,
    informe_por_cliente,
    informe_por_equipo,
    informe_cartera,
    informe_tecnico,
)

router = APIRouter()

@router.get("/api/informes/{periodo}")
async def obtener_informe_general(periodo: str, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "informe": informe_general(periodo)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/informes/{periodo}/cliente/{cliente_id}")
async def obtener_informe_cliente(periodo: str, cliente_id: int, usuario=Depends(get_current_user)):
    try:
        datos = informe_por_cliente(periodo, cliente_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # informe_por_cliente() nunca devuelve None (siempre arma el dict, aunque el cliente no exista), asi que se detecta "sin datos" igual que ya
    # hace routers/exportacion.py para el PDF de este mismo informe.
    if datos["estado_general"] is None and datos["facturado"] == 0 and datos["costos"] == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o sin datos en el periodo")

    return {"success": True, "informe": datos}


@router.get("/api/informes/{periodo}/equipo/{equipo_id}")
async def obtener_informe_equipo(periodo: str, equipo_id: int, usuario=Depends(get_current_user)):
    try:
        datos = informe_por_equipo(periodo, equipo_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if datos is None:
        raise HTTPException(status_code=404, detail="Equipo no encontrado")

    return {"success": True, "informe": datos}


@router.get("/api/informes/{periodo}/cartera")
async def obtener_informe_cartera(periodo: str, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "informe": informe_cartera(periodo)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/informes/{periodo}/tecnico")
async def obtener_informe_tecnico(periodo: str, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "informe": informe_tecnico(periodo)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc