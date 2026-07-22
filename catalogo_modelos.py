from fastapi import HTTPException

from Variables.Clientes import Clientes
from Variables.Costos import Costos
from Variables.enums import EstadoCliente, TipoCliente, TipoCosto
from Variables.Equipos import Equipos
from Variables.Impuestos import Impuesto
from Variables.Insumos import Insumo
from Variables.Modelos import Modelo
from Variables.Poliza import Poliza
from Variables.Repuestos import Repuesto
from Variables.Valor_facturado import ValorFacturado


def campo(nombre, etiqueta, tipo="text", opciones=None, requerido=True):
    configuracion = {
        "nombre": nombre,
        "etiqueta": etiqueta,
        "label": etiqueta,
        "tipo": tipo,
        "requerido": requerido,
    }

    if opciones:
        configuracion["opciones"] = opciones

    return configuracion


def opciones_enum(tipo_enum):
    return [item.value for item in tipo_enum]


CATALOGO_DATOS = {
    "clientes": {
        "etiqueta": "Clientes",
        "modelo": Clientes,
        "campos": [
            campo("tipo_cliente", "Tipo de cliente", "select", opciones_enum(TipoCliente)),
            campo("estado_cliente", "Estado", "select", opciones_enum(EstadoCliente)),
            campo("tipo_contacto", "Tipo de contacto"),
            campo("condicion_pago", "Condicion de pago"),
            campo("estado_cartera_cliente", "Estado de cartera"),
        ],
        "enumeraciones": {
            "tipo_cliente": TipoCliente,
            "estado_cliente": EstadoCliente,
        },
    },
    "modelos": {
        "etiqueta": "Modelos",
        "modelo": Modelo,
        "campos": [
            campo("modelo", "Modelo"),
            campo("toner", "Toner"),
            campo("rend_orig", "Rendimiento original", "number"),
            campo("rend_gen", "Rendimiento generico", "number"),
        ],
    },
    "equipos": {
        "etiqueta": "Equipos",
        "modelo": Equipos,
        "campos": [
            campo("numero_serie", "Numero de serie"),
            campo("tipo_equipo", "Tipo de equipo"),
            campo("tecnologia", "Tecnologia"),
            campo("color", "Color"),
            campo("estado_equipo", "Estado del equipo"),
            campo("estado_tecnico", "Estado tecnico"),
            campo("recomendacion_tecnica", "Recomendacion tecnica", requerido=False),
        ],
    },
    "insumos": {
        "etiqueta": "Insumos",
        "modelo": Insumo,
        "campos": [
            campo("toner", "Toner"),
        ],
    },
    "polizas": {
        "etiqueta": "Polizas",
        "modelo": Poliza,
        "campos": [
            campo("seriedad", "Seriedad"),
            campo("contrato", "Contrato"),
        ],
    },
    "repuestos": {
        "etiqueta": "Repuestos",
        "modelo": Repuesto,
        "campos": [
            campo("cuchilla_limpieza", "Cuchilla limpieza"),
            campo("cuchilla_transferencia", "Cuchilla transferencia"),
            campo("banda_fusora", "Banda fusora"),
            campo("rodillo_fusor", "Rodillo fusor"),
            campo("sleeven_fusor", "Sleeven fusor"),
            campo("telilla", "Telilla"),
        ],
    },
    "costos": {
        "etiqueta": "Costos",
        "modelo": Costos,
        "campos": [
            campo("fecha_costo", "Fecha del costo", "date"),
            campo("periodo", "Periodo"),
            campo("cliente_id", "Cliente", "number"),
            campo("contrato_id", "Contrato", "number"),
            campo("equipo_id", "Equipo", "number"),
            campo("tipo_costo", "Tipo de costo", "select", opciones_enum(TipoCosto)),
            campo("descripcion", "Descripcion"),
            campo("cantidad", "Cantidad", "number"),
            campo("valor_unitario", "Valor unitario", "number"),
            campo("valor_total", "Valor total", "number", requerido=False),
            campo("responsable", "Responsable"),
            campo("soporte", "Soporte o documento asociado", requerido=False),
            campo("observaciones", "Observaciones", requerido=False),
        ],
        "enumeraciones": {
            "tipo_costo": TipoCosto,
        },
    },
    "impuestos": {
        "etiqueta": "Impuestos",
        "modelo": Impuesto,
        "campos": [
            campo("municipal", "Municipal", "number"),
            campo("departamental", "Departamental", "number"),
            campo("pro_deporte", "Pro Deporte", "number"),
        ],
    },
    "valor_facturado": {
        "etiqueta": "Valor Facturado",
        "modelo": ValorFacturado,
        "campos": [
            campo("facturado", "Valor facturado", "number"),
        ],
    },
}


def obtener_tipos():
    return {clave: configuracion["etiqueta"] for clave, configuracion in CATALOGO_DATOS.items()}


def obtener_configuracion_frontend():
    return {clave: configuracion["campos"] for clave, configuracion in CATALOGO_DATOS.items()}


def obtener_configuracion_tipo(tipo):
    clave = tipo.lower()

    if clave not in CATALOGO_DATOS:
        raise HTTPException(status_code=404, detail="Tipo de dato no soportado")

    return CATALOGO_DATOS[clave]
