#DECISIÓN DE DISEÑO: Se implementó un único router de exportación 
#que reutiliza la capa genérica de datos existente. De esta forma, 
# cualquier modelo registrado en el catálogo puede exportarse automáticamente 
# (CSV y, opcionalmente, Excel) sin crear lógica específica para cada módulo.


import io
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, ListFlowable, ListItem,
)

from Modulos.Informes_mensuales import informe_general, informe_por_cliente

router = APIRouter()


def _moneda(valor):
    if valor is None:
        return "N/D"
    return f"$ {valor:,.0f}".replace(",", ".")


def _porcentaje(valor):
    return f"{valor:.1f}%" if valor is not None else "N/D"


def _tabla_indicadores(filas):
    tabla = Table(filas, colWidths=[9 * cm, 6 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#263445")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d8dee6")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tabla


def _pdf_informe_general(periodo, datos):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2 * cm, bottomMargin=2 * cm)
    estilos = getSampleStyleSheet()
    story = [
        Paragraph("Informe Mensual General - Continental", estilos["Title"]),
        Paragraph(f"Periodo: {periodo}", estilos["Normal"]),
        Paragraph(f"Generado: {datetime.utcnow().strftime('%d/%m/%Y %H:%M')} UTC", estilos["Normal"]),
        Spacer(1, 16),
    ]

    filas = [
        ["Indicador", "Valor"],
        ["Contratos activos", datos["total_contratos"]],
        ["Clientes", datos["total_clientes"]],
        ["Equipos", datos["total_equipos"]],
        ["Facturado del mes", _moneda(datos["facturado_mes"])],
        ["Recaudado del mes", _moneda(datos["recaudado_mes"])],
        ["Cartera pendiente", _moneda(datos["cartera_pendiente"])],
        ["Costos del mes", _moneda(datos["costos_mes"])],
        ["Utilidad bruta", _moneda(datos["utilidad_bruta"])],
        ["Margen promedio", _porcentaje(datos["margen_promedio"])],
        ["Toneres entregados", datos["toneres_entregados"] if datos["toneres_entregados"] is not None else "N/D"],
        ["Contratos por vencer (60 dias)", datos["contratos_por_vencer"]],
        ["Clientes en mora", datos["clientes_en_mora"]],
    ]
    story.append(_tabla_indicadores(filas))
    story.append(Spacer(1, 20))

    story.append(Paragraph("Recomendaciones", estilos["Heading2"]))
    if datos["recomendaciones"]:
        items = [ListItem(Paragraph(r, estilos["Normal"])) for r in datos["recomendaciones"]]
        story.append(ListFlowable(items, bulletType="bullet"))
    else:
        story.append(Paragraph("Sin recomendaciones para este periodo.", estilos["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer


def _pdf_informe_cliente(periodo, cliente_id, datos):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=2 * cm, bottomMargin=2 * cm)
    estilos = getSampleStyleSheet()
    story = [
        Paragraph(f"Informe por Cliente #{cliente_id}", estilos["Title"]),
        Paragraph(f"Periodo: {periodo}", estilos["Normal"]),
        Spacer(1, 16),
    ]

    filas = [
        ["Indicador", "Valor"],
        ["Estado del cliente", datos["estado_general"] or "N/D"],
        ["Contratos activos", datos["contratos_activos"]],
        ["Equipos instalados", datos["equipos_instalados"] if datos["equipos_instalados"] is not None else "N/D"],
        ["Valor mensual contratado", _moneda(datos["valor_mensual_contratado"])],
        ["Consumo del mes", datos["consumo"] if datos["consumo"] is not None else "N/D"],
        ["Facturado", _moneda(datos["facturado"])],
        ["Pagado", _moneda(datos["pagado"])],
        ["Saldo pendiente", _moneda(datos["saldo"])],
        ["Costos", _moneda(datos["costos"])],
        ["Utilidad", _moneda(datos["utilidad"])],
        ["Margen", _porcentaje(datos["margen"])],
    ]
    story.append(_tabla_indicadores(filas))

    doc.build(story)
    buffer.seek(0)
    return buffer


@router.get("/api/informes/{periodo}/pdf")
async def exportar_informe_general_pdf(periodo: str):
    try:
        datos = informe_general(periodo)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    buffer = _pdf_informe_general(periodo, datos)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="informe_general_{periodo}.pdf"'},
    )


@router.get("/api/informes/{periodo}/cliente/{cliente_id}/pdf")
async def exportar_informe_cliente_pdf(periodo: str, cliente_id: int):
    try:
        datos = informe_por_cliente(periodo, cliente_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if datos["estado_general"] is None and datos["facturado"] == 0 and datos["costos"] == 0:
        raise HTTPException(status_code=404, detail="Cliente no encontrado o sin datos en el periodo")

    buffer = _pdf_informe_cliente(periodo, cliente_id, datos)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="informe_cliente_{cliente_id}_{periodo}.pdf"'},
    )