from fastapi import HTTPException

from Variables.Clientes import Clientes
from Variables.Costos import Costos
from Variables.enums import EstadoCliente, TipoCliente, TipoCosto, EstadoFactura
from Variables.Equipos import Equipos
from Variables.Facturacion import Facturacion
from Variables.Insumos import Insumo
from Variables.Modelos import Modelo
from Variables.Poliza import Poliza
from Variables.Repuestos import Repuesto


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
    "facturacion": {
        "etiqueta": "Facturacion",
        "modelo": Facturacion,
        "campos": [
            campo("periodo", "Periodo"),
            campo("cliente_id", "Cliente", "number"),
            campo("contrato_id", "Contrato", "number"),
            campo("numero_factura", "Numero de factura"),
            campo("fecha_factura", "Fecha de factura", "date"),
            campo("fecha_vencimiento", "Fecha de vencimiento", "date", requerido=False),
            campo("valor_mensual_base", "Valor mensual base", "number"),
            campo("valor_adicionales_bn", "Adicionales blanco y negro", "number", requerido=False),
            campo("valor_adicionales_color", "Adicionales color", "number", requerido=False),
            campo("valor_adicionales_escaneo", "Adicionales escaneo", "number", requerido=False),
            campo("otros_cargos", "Otros cargos", "number", requerido=False),
            campo("subtotal", "Subtotal", "number", requerido=False),
            campo("incluye_iva", "Los valores ya incluyen IVA (1=si, 0=no)", "number", requerido=False),
            campo("porcentaje_iva", "Porcentaje de IVA", "number", requerido=False),
            campo("valor_iva", "Valor IVA", "number", requerido=False),
            campo("impuesto_municipal", "Impuesto municipal", "number", requerido=False),
            campo("impuesto_departamental", "Impuesto departamental", "number", requerido=False),
            campo("impuesto_pro_deporte", "Impuesto pro deporte", "number", requerido=False),
            campo("retenciones", "Retenciones", "number", requerido=False),
            campo("total_facturado", "Total facturado", "number", requerido=False),
            campo("estado_factura", "Estado de la factura", "select", opciones_enum(EstadoFactura)),
            campo("fecha_envio", "Fecha de envio al cliente", "date", requerido=False),
            campo("medio_envio", "Medio de envio", requerido=False),
            campo("observaciones", "Observaciones", requerido=False),
        ],
        "enumeraciones": {
            "estado_factura": EstadoFactura,
        },
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
