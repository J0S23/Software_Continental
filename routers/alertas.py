from fastapi import APIRouter

from Modulos.Alertas import generar_alertas

router = APIRouter()

@router.get("/api/alertas")
async def obtener_alertas():
    return generar_alertas()