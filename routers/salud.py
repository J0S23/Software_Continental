# Health check: usado por el orquestador/monitor de turno para saber si la
# app esta viva Y puede hablar con la base de datos (no solo que uvicorn
# responde). No requiere sesion iniciada a proposito.
from fastapi import APIRouter, Response
from sqlalchemy import text

from base_de_datos import SesionLocal, logger

router = APIRouter()


@router.get("/health")
async def salud(response: Response):
    try:
        with SesionLocal() as sesion:
            sesion.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("Health check fallo: no se pudo conectar a la base de datos: %s", exc)
        response.status_code = 503
        return {"status": "error", "database": "desconectada"}

    return {"status": "ok", "database": "conectada"}
