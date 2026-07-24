#DECISIÓN DE DISEÑO: Se implementó un único router de exportación 
#que reutiliza la capa genérica de datos existente. De esta forma, 
# cualquier modelo registrado en el catálogo puede exportarse automáticamente 
# (CSV y, opcionalmente, Excel) sin crear lógica específica para cada módulo.


import csv
import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from catalogo_modelos import obtener_configuracion_tipo
from servicios_datos import listar_registros, obtener_campos, obtener_modelo, serializar

router = APIRouter()

def _fila_valores(registro_serializado, campos):
    """Convierte el dict serializado en una fila plana en el mismo orden
    que las columnas, evitando que un valor None rompa el CSV/Excel."""
    return [
        registro_serializado.get(c["nombre"], "") if registro_serializado.get(c["nombre"]) is not None else ""
        for c in campos
    ]


@router.get("/api/{tipo}/exportar/csv")
async def exportar_csv(tipo: str):
    configuracion = obtener_configuracion_tipo(tipo)
    modelo = obtener_modelo(configuracion)
    campos = obtener_campos(configuracion)
    registros = listar_registros(modelo)

    buffer = io.StringIO()
    writer = csv.writer(buffer)

    # Encabezado: ID + etiquetas legibles (no los nombres tecnicos de columna).
    writer.writerow(["ID"] + [c.get("etiqueta") or c.get("label") for c in campos])

    for registro in registros:
        fila = serializar(registro, campos)
        writer.writerow([fila["id"]] + _fila_valores(fila, campos))

    buffer.seek(0)
    # BOM UTF-8 (\ufeff) para que Excel en Windows abra tildes/enes bien;
    # sin esto, "Facturacion" con enes se ve mal en Excel aunque el CSV
    # este correcto.
    contenido = "\ufeff" + buffer.getvalue()

    return StreamingResponse(
        iter([contenido]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{tipo}.csv"'},
    )


@router.get("/api/{tipo}/exportar/excel")
async def exportar_excel(tipo: str):
    try:
        from openpyxl import Workbook
    except ImportError as exc:
        # No se asume que openpyxl esta instalado: si falta, se informa
        # con claridad en vez de un 500 generico.
        raise HTTPException(
            status_code=501,
            detail="Exportacion a Excel requiere 'openpyxl'. Agregalo a requirements.txt e instala con pip.",
        ) from exc

    configuracion = obtener_configuracion_tipo(tipo)
    modelo = obtener_modelo(configuracion)
    campos = obtener_campos(configuracion)
    registros = listar_registros(modelo)

    libro = Workbook()
    hoja = libro.active
    hoja.title = tipo[:31]  # Excel limita el nombre de hoja a 31 caracteres.

    hoja.append(["ID"] + [c.get("etiqueta") or c.get("label") for c in campos])
    for registro in registros:
        fila = serializar(registro, campos)
        hoja.append([fila["id"]] + _fila_valores(fila, campos))

    buffer = io.BytesIO()
    libro.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{tipo}.xlsx"'},
    )