from enum import Enum
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from Modulos.Clientes import Clientes
from Modulos.enums import EstadoCliente, TipoCliente
from Modulos.Insumos import Maquinas as Insumos
from Modulos.Modelos import Maquinas as Modelos
from Modulos.Repuestos import Maquinas as Repuestos

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Gestor de Datos Continental")
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

MODELOS = {
    "clientes": {
        "label": "Clientes",
        "model": Clientes,
        "fields": [
            "tipo_cliente",
            "estado_cliente",
            "tipo_contacto",
            "condicion_pago",
            "estado_cartera_cliente",
        ],
        "enums": {
            "tipo_cliente": TipoCliente,
            "estado_cliente": EstadoCliente,
        },
    },
    "modelos": {
        "label": "Modelos",
        "model": Modelos,
        "fields": ["modelo", "toner", "rend_orig", "rend_gen"],
        "numbers": {"rend_orig", "rend_gen"},
    },
    "insumos": {
        "label": "Insumos",
        "model": Insumos,
        "fields": ["tipo_insumo", "color", "estado"],
    },
    "repuestos": {
        "label": "Repuestos",
        "model": Repuestos,
        "fields": [
            "cuchilla_limpieza",
            "cuchilla_transferencia",
            "banda_fusora",
            "rodillo_fusor",
            "sleeven_fusor",
            "telilla",
        ],
    },
}


for config in MODELOS.values():
    config["model"].crear_tabla()


def obtener_config(tipo: str) -> dict:
    key = tipo.lower()
    if key not in MODELOS:
        raise HTTPException(status_code=404, detail="Tipo de dato no soportado")
    return MODELOS[key]


def normalizar_payload(config: dict, data: dict) -> dict:
    valores = {}

    for field in config["fields"]:
        value = data.get(field)
        if value in (None, ""):
            raise HTTPException(status_code=400, detail=f"Falta el campo '{field}'")

        enum_type = config.get("enums", {}).get(field)
        if enum_type:
            try:
                value = enum_type(value)
            except ValueError as exc:
                opciones = ", ".join(item.value for item in enum_type)
                raise HTTPException(
                    status_code=400,
                    detail=f"Valor invalido para '{field}'. Usa: {opciones}",
                ) from exc

        if field in config.get("numbers", set()):
            try:
                value = float(value)
            except (TypeError, ValueError) as exc:
                raise HTTPException(
                    status_code=400,
                    detail=f"El campo '{field}' debe ser numerico",
                ) from exc

        valores[field] = value

    return valores


def serializar(registro, fields: list) -> dict:
    data = {"id": registro.id}

    for field in fields:
        value = getattr(registro, field)
        data[field] = value.value if isinstance(value, Enum) else value

    return data


@app.get("/", response_class=HTMLResponse)
async def index():
    return (BASE_DIR / "templates" / "index.html").read_text(encoding="utf-8")


@app.get("/api/tipos")
async def get_tipos():
    return {key: config["label"] for key, config in MODELOS.items()}


@app.get("/api/{tipo}")
async def obtener_registros(tipo: str):
    config = obtener_config(tipo)
    registros = config["model"].obtener_todos()
    return {
        "success": True,
        "datos": [serializar(registro, config["fields"]) for registro in registros],
    }


@app.post("/api/{tipo}")
async def agregar_registro(tipo: str, request: Request):
    config = obtener_config(tipo)
    data = await request.json()
    valores = normalizar_payload(config, data)
    registro = config["model"].agregar(**valores)

    return {
        "success": True,
        "message": "Registro agregado",
        "registro": serializar(registro, config["fields"]),
    }


@app.put("/api/{tipo}/{registro_id}")
async def editar_registro(tipo: str, registro_id: int, request: Request):
    config = obtener_config(tipo)

    if not hasattr(config["model"], "actualizar"):
        raise HTTPException(status_code=405, detail="Este tipo de dato no permite edicion")

    data = await request.json()
    valores = normalizar_payload(config, data)
    registro = config["model"].actualizar(registro_id, **valores)

    if not registro:
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    return {
        "success": True,
        "message": "Registro actualizado",
        "registro": serializar(registro, config["fields"]),
    }


@app.delete("/api/{tipo}/{registro_id}")
async def eliminar_registro(tipo: str, registro_id: int):
    config = obtener_config(tipo)

    if not config["model"].obtener_por_id(registro_id):
        raise HTTPException(status_code=404, detail="Registro no encontrado")

    config["model"].eliminar(registro_id)
    return {"success": True, "message": "Registro eliminado"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
