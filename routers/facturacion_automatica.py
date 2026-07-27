from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from Modulos.enums import EmpresaFacturadora, EstadoFactura
from Servicio.FacturacionAutomatica import calcular_facturacion, generar_facturacion

router = APIRouter()


class GenerarFacturacionRequest(BaseModel):
    numero_factura: str
    fecha_factura: datetime
    estado_factura: EstadoFactura
    empresa_factura: Optional[EmpresaFacturadora] = None
    fecha_vencimiento: Optional[datetime] = None
    # Salta las validaciones de duplicado e inconsistencia equipo-contrato
    # que hace generar_facturacion(). Se deja en False por defecto para
    # que el frontend tenga que pedirlo explicitamente tras ver la advertencia.
    forzar: bool = False


@router.get("/api/facturacion-automatica/{contrato_id}/{periodo}")
async def previsualizar_facturacion(contrato_id: int, periodo: str):
    """Calcula la facturacion del contrato/periodo SIN crear ningun registro.
    Util para mostrar un preview antes de que el usuario confirme."""
    calculo = calcular_facturacion(contrato_id, periodo)

    if calculo is None:
        raise HTTPException(
            status_code=404,
            detail="No se pudo calcular: el contrato no existe o no hay lectura registrada para ese periodo",
        )

    return calculo


@router.post("/api/facturacion-automatica/{contrato_id}/{periodo}")
async def generar_facturacion_automatica(contrato_id: int, periodo: str, datos: GenerarFacturacionRequest):
    """Calcula y crea el registro de Facturacion. Devuelve 409 si ya existe
    una factura para ese contrato+periodo o si hay inconsistencias
    equipo-contrato (salvo que forzar=True)."""
    try:
        factura = generar_facturacion(
            contrato_id=contrato_id,
            periodo=periodo,
            numero_factura=datos.numero_factura,
            fecha_factura=datos.fecha_factura,
            estado_factura=datos.estado_factura,
            empresa_factura=datos.empresa_factura,
            fecha_vencimiento=datos.fecha_vencimiento,
            forzar=datos.forzar,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if factura is None:
        raise HTTPException(
            status_code=404,
            detail="No se pudo generar: el contrato no existe o no hay lectura registrada para ese periodo",
        )

    return {
        "success": True,
        "message": "Factura generada automaticamente",
        "factura_id": factura.id,
        "total_facturado": factura.total_facturado,
    }