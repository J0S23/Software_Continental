from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from Persistencia.AlertaEstadoRepositorio import AlertaEstadoRepositorio
from Servicio.Alertas import generar_alertas

router = APIRouter()


def _serializar_estado(estado):
    return {
        "id": f"{estado.tipo}:{estado.referencia_id}",
        "tipo": estado.tipo,
        "referencia_id": estado.referencia_id,
        "mensaje": estado.mensaje,
        "nivel": estado.nivel,
        "leida": estado.leida,
        "guardada": estado.guardada,
        "descartada": estado.descartada,
        "fecha_actualizacion": estado.fecha_actualizacion.isoformat() if estado.fecha_actualizacion else None,
    }


class EstadoAlertaRequest(BaseModel):
    tipo: str
    referencia_id: Optional[int] = None
    mensaje: Optional[str] = None
    nivel: Optional[str] = None
    leida: Optional[bool] = None
    guardada: Optional[bool] = None
    descartada: Optional[bool] = None


@router.get("/api/alertas")
async def obtener_alertas(incluir_descartadas: bool = False):
    return generar_alertas(incluir_descartadas=incluir_descartadas)


@router.post("/api/alertas/estado")
async def actualizar_estado_alerta(datos: EstadoAlertaRequest):
    """Marca una alerta como leida/guardada/descartada (upsert). Los campos
    que no se envian no se modifican."""
    estado = AlertaEstadoRepositorio.marcar(
        tipo=datos.tipo,
        referencia_id=datos.referencia_id,
        mensaje=datos.mensaje,
        nivel=datos.nivel,
        leida=datos.leida,
        guardada=datos.guardada,
        descartada=datos.descartada,
    )
    return {"success": True, "estado": _serializar_estado(estado)}


@router.get("/api/alertas/guardadas")
async def obtener_alertas_guardadas():
    guardadas = AlertaEstadoRepositorio.obtener_guardadas()
    return {"success": True, "alertas": [_serializar_estado(estado) for estado in guardadas]}
