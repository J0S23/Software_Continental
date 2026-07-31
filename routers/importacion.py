# Importacion masiva desde Excel, reutiliza la misma capa generica que el CRUD manual
# (catalogo_modelos + servicios_datos.normalizar_payload/crear_registro), asi
# que cada fila se valida y se registra en Historial exactamente igual que si
# se hubiera creado una por una desde el formulario -- no hay logica de validacion duplicada aqui.
import io
from datetime import date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill

from catalogo_modelos import obtener_configuracion_tipo
from routers.auth import get_current_user
from servicios_datos import crear_registro, normalizar_payload, obtener_campos, obtener_modelo

router = APIRouter()

# Restringido a los 3 tipos que mas volumen de carga manual tienen. No se generaliza a "cualquier tipo del
# catalogo" a proposito: entidades como usuarios o facturacion no deberian poblarse por lote sin mas control.
TIPOS_IMPORTABLES = {"lecturas", "clientes", "equipos"}

ESTILO_ENCABEZADO_FONT = Font(bold=True, color="FFFFFF")
ESTILO_ENCABEZADO_FILL = PatternFill(start_color="263445", end_color="263445", fill_type="solid")


def _validar_tipo_importable(tipo):
    if tipo not in TIPOS_IMPORTABLES:
        opciones = ", ".join(sorted(TIPOS_IMPORTABLES))
        raise HTTPException(
            status_code=400,
            detail=f"Tipo no importable. Usa uno de: {opciones}",
        )
    return obtener_configuracion_tipo(tipo)


def _valor_desde_excel(configuracion_campo, valor):
    """Convierte lo que openpyxl trae de una celda al formato que espera
    servicios_datos.normalizar_payload, segun el tipo de campo del catalogo.
    Sin esto, una celda de fecha (que openpyxl entrega como datetime, no como
    texto 'YYYY-MM-DD') o un booleano nativo de Excel siempre fallarian la
    validacion aunque el dato sea correcto."""
    if valor is None or valor == "":
        return None

    tipo_campo = configuracion_campo.get("tipo")

    if tipo_campo == "date" and isinstance(valor, (datetime, date)):
        return valor.strftime("%Y-%m-%d")

    if tipo_campo == "boolean" and isinstance(valor, bool):
        return "Si" if valor else "No"

    if isinstance(valor, str):
        return valor.strip()

    return valor


@router.get("/api/importar/{tipo}/plantilla")
async def descargar_plantilla_importacion(tipo: str, usuario=Depends(get_current_user)):
    """Excel con solo la fila de encabezados (los nombres de campo exactos
    que espera el importador), para que el usuario no tenga que adivinar
    como se llama cada columna."""
    configuracion = _validar_tipo_importable(tipo)
    campos = obtener_campos(configuracion)

    wb = Workbook()
    hoja = wb.active
    hoja.title = tipo[:31]
    encabezados = [c["nombre"] for c in campos]
    hoja.append(encabezados)
    for celda in hoja[1]:
        celda.font = ESTILO_ENCABEZADO_FONT
        celda.fill = ESTILO_ENCABEZADO_FILL
    for indice, campo_config in enumerate(campos, start=1):
        hoja.cell(row=2, column=indice, value=f"({campo_config['etiqueta']})")
        hoja.column_dimensions[hoja.cell(row=1, column=indice).column_letter].width = 22

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="plantilla_{tipo}.xlsx"'},
    )


@router.post("/api/importar/{tipo}")
async def importar_desde_excel(tipo: str, archivo: UploadFile = File(...), usuario=Depends(get_current_user)):
    """Crea un registro por cada fila con datos del Excel. No detiene el
    proceso ante una fila invalida: la reporta en 'errores' y sigue con las
    demas. Fila vacia (todas las celdas en blanco) se ignora en silencio."""
    configuracion = _validar_tipo_importable(tipo)
    modelo = obtener_modelo(configuracion)
    campos = obtener_campos(configuracion)
    campos_por_nombre = {c["nombre"]: c for c in campos}

    contenido = await archivo.read()
    try:
        wb = load_workbook(io.BytesIO(contenido), data_only=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"No se pudo leer el archivo Excel: {exc}") from exc

    hoja = wb.active
    filas = list(hoja.iter_rows(values_only=True))
    if not filas:
        raise HTTPException(status_code=400, detail="El archivo esta vacio")

    encabezados = [str(celda).strip() if celda is not None else "" for celda in filas[0]]
    encabezados_reconocidos = [e for e in encabezados if e in campos_por_nombre]
    if not encabezados_reconocidos:
        raise HTTPException(
            status_code=400,
            detail=(
                "Ninguna columna del Excel coincide con los campos esperados. "
                f"Descarga la plantilla en GET /api/importar/{tipo}/plantilla."
            ),
        )

    creados = 0
    errores = []

    for numero_fila, fila in enumerate(filas[1:], start=2):
        datos_fila_crudos = dict(zip(encabezados, fila))
        # se descartan columnas del excel que no correspondan a un campo del catalogo
        datos_fila = {
            nombre_campo: _valor_desde_excel(campos_por_nombre[nombre_campo], valor)
            for nombre_campo, valor in datos_fila_crudos.items()
            if nombre_campo in campos_por_nombre
        }

        if not any(v not in (None, "") for v in datos_fila.values()):
            continue  # fila completamente vacia, no cuenta como error

        try:
            valores = normalizar_payload(configuracion, datos_fila)
            crear_registro(modelo, valores, usuario_id=usuario.id, tipo_entidad=tipo)
            creados += 1
        except HTTPException as exc:
            errores.append({"fila": numero_fila, "error": exc.detail})
        except Exception as exc:
            errores.append({"fila": numero_fila, "error": str(exc)})

    return {
        "success": True,
        "message": f"{creados} registro(s) importado(s), {len(errores)} con error(es)",
        "creados": creados,
        "errores": errores,
    }