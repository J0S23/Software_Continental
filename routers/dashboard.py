# Endpoints JSON del dashboard gerencial (seccion 18 del documento de
# requerimientos). Las funciones de calculo ya existen en
# Servicio/Dashboard.py; este router solo las expone via HTTP.
# Requieren sesion iniciada (mismo criterio que routers/informes.py).
#
# No se expone serie_consumo_paginas_por_cliente: esa funcion siempre
# devuelve None (bloqueada, ver docstring de Servicio/Dashboard.py) porque
# Equipos no tiene cliente_id/contrato_id historico por lectura. Exponerla
# hoy solo daria un endpoint que nunca trae datos utiles.
from fastapi import APIRouter, Depends, HTTPException

from routers.auth import get_current_user
from Servicio.Dashboard import (
    dashboard_snapshot,
    serie_financiera,
    serie_costos_por_tipo,
    serie_ingresos_por_cliente,
    serie_rentabilidad_por_cliente,
    serie_cartera_por_edad,
    serie_correctivos_por_equipo,
    serie_toneres_por_cliente,
)

router = APIRouter()

@router.get("/api/dashboard/{periodo}")
async def obtener_dashboard(periodo: str, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "dashboard": dashboard_snapshot(periodo)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/dashboard/{periodo}/serie-financiera")
async def obtener_serie_financiera(periodo: str, meses: int = 6, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "serie": serie_financiera(periodo, meses)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/dashboard/{periodo}/costos-por-tipo")
async def obtener_costos_por_tipo(periodo: str, meses: int = 6, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "serie": serie_costos_por_tipo(periodo, meses)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/dashboard/{periodo}/ingresos-por-cliente")
async def obtener_ingresos_por_cliente(periodo: str, meses: int = 6, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "serie": serie_ingresos_por_cliente(periodo, meses)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/dashboard/{periodo}/rentabilidad-por-cliente")
async def obtener_rentabilidad_por_cliente(periodo: str, meses: int = 6, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "serie": serie_rentabilidad_por_cliente(periodo, meses)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/dashboard/{periodo}/cartera-por-edad")
async def obtener_cartera_por_edad(periodo: str, meses: int = 6, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "serie": serie_cartera_por_edad(periodo, meses)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/dashboard/{periodo}/correctivos-por-equipo")
async def obtener_correctivos_por_equipo(periodo: str, meses: int = 6, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "serie": serie_correctivos_por_equipo(periodo, meses)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/api/dashboard/{periodo}/toneres-por-cliente")
async def obtener_toneres_por_cliente(periodo: str, meses: int = 6, usuario=Depends(get_current_user)):
    try:
        return {"success": True, "serie": serie_toneres_por_cliente(periodo, meses)}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc