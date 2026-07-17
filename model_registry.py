from base_de_datos import crear_tablas
from catalogo_modelos import (
    CATALOGO_DATOS,
    campo,
    obtener_configuracion_frontend,
    obtener_configuracion_tipo,
    obtener_tipos,
    opciones_enum,
)
from servicios_datos import normalizar_payload, serializar


def _configuracion_legacy(configuracion):
    return {
        "label": configuracion["etiqueta"],
        "model": configuracion["modelo"],
        "fields": configuracion["campos"],
        "enums": configuracion.get("enumeraciones", {}),
    }


MODELOS = {
    clave: _configuracion_legacy(configuracion)
    for clave, configuracion in CATALOGO_DATOS.items()
}


def obtener_config(tipo):
    return _configuracion_legacy(obtener_configuracion_tipo(tipo))
