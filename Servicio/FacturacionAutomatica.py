#Requiere un contrato con condiciones económicas configuradas y una lectura del período a facturar; de lo contrario, devuelve None

from Modulos.Contratos import Contratos
from Modulos.Facturacion import Facturacion
from Modulos.Lecturas import Lecturas
from Servicio.Informes_mensuales import _parse_periodo


def _lectura_actual_y_anterior(contrato_id, periodo):

    #Lectura del periodo pedido y la ultima lectura anterior a ese periodo, ambas del mismo contrato. 
    #Se usa contrato_id (no equipo_id) porque un contrato puede haber cambiado de equipo (CambiosRetiro) y
    #lo que importa para facturar es el historial del contrato.

    mes, anio = _parse_periodo(periodo)
    lecturas = Lecturas.obtener_por_contrato(contrato_id)

    lecturas_periodo = [l for l in lecturas if l.periodo == periodo]
    anteriores = [
        l for l in lecturas
        if l.fecha_lectura and (l.fecha_lectura.year, l.fecha_lectura.month) < (anio, mes)
    ]

    lectura_actual = lecturas_periodo[-1] if lecturas_periodo else None
    lectura_anterior = anteriores[-1] if anteriores else None
    return lectura_actual, lectura_anterior

def calcular_facturacion(contrato_id, periodo):
    #Calcula consumo, paginas adicionales, valor adicional y subtotal/total (sin IVA) para un contrato en un periodo, SIN guardar nada.
    #Devuelve None si:
    #- el contrato no existe.
    #- no hay lectura registrada para ese periodo (no se puede facturar a ciegas).

    contrato = Contratos.obtener_por_id(contrato_id)
    if not contrato:
        return None

    lectura_actual, lectura_anterior = _lectura_actual_y_anterior(contrato_id, periodo)
    if not lectura_actual:
        return None

    # Si no hay lectura anterior (primera lectura del contrato), se toma 0 como contador anterior. 
    # OJO: esto puede disparar un consumo muy alto en la primera factura si el contador del equipo no arrancab en 0. 
    # Pendiente a revisar: usar el contador inicial del equipo (seccion 5.2 / 7.1 del documento) en vez de 0 cuando no hay lectura previa.
    
    contador_anterior_bn = lectura_anterior.contador_bn if lectura_anterior else 0
    contador_anterior_color = lectura_anterior.contador_color if lectura_anterior else 0

    consumo_bn = max(0, (lectura_actual.contador_bn or 0) - contador_anterior_bn)
    consumo_color = max(0, (lectura_actual.contador_color or 0) - contador_anterior_color)

    paginas_bn_incluidas = contrato.paginas_bn_incluidas or 0
    paginas_color_incluidas = contrato.paginas_color_incluidas or 0

    adicionales_bn = max(0, consumo_bn - paginas_bn_incluidas)
    adicionales_color = max(0, consumo_color - paginas_color_incluidas)

    valor_adicional_bn = adicionales_bn * (contrato.valor_pagina_adicional_bn or 0)
    valor_adicional_color = adicionales_color * (contrato.valor_pagina_adicional_color or 0)

    valor_mensual_base = contrato.valor_mensual_base or 0
    subtotal = valor_mensual_base + valor_adicional_bn + valor_adicional_color

    return {
        "contrato_id": contrato_id,
        "cliente_id": contrato.cliente_id,
        "periodo": periodo,
        "lectura_id": lectura_actual.id,

        "contador_anterior_bn": contador_anterior_bn,
        "contador_actual_bn": lectura_actual.contador_bn,
        "consumo_bn": consumo_bn,
        "paginas_bn_incluidas": paginas_bn_incluidas,
        "paginas_adicionales_bn": adicionales_bn,
        "valor_adicional_bn": valor_adicional_bn,

        "contador_anterior_color": contador_anterior_color,
        "contador_actual_color": lectura_actual.contador_color,
        "consumo_color": consumo_color,
        "paginas_color_incluidas": paginas_color_incluidas,
        "paginas_adicionales_color": adicionales_color,
        "valor_adicional_color": valor_adicional_color,

        "valor_mensual_base": valor_mensual_base,

        # Sin IVA por ahora: subtotal y total_facturado son el mismo valor.
        "subtotal": subtotal,
        "total_facturado": subtotal,
    }

def generar_facturacion(
    contrato_id, periodo, numero_factura, fecha_factura,
    estado_factura, empresa_factura=None, fecha_vencimiento=None,
):
    #Calcula la facturacion del contrato/periodo y crea el registro en Facturacion. 
    # Devuelve None (sin crear nada) si calcular_facturacion() no pudo calcular por falta de contrato o de lectura.
    
    calculo = calcular_facturacion(contrato_id, periodo)
    if calculo is None:
        return None

    return Facturacion.agregar(
        periodo=periodo,
        cliente_id=calculo["cliente_id"],
        contrato_id=contrato_id,
        numero_factura=numero_factura,
        fecha_factura=fecha_factura,
        estado_factura=estado_factura,
        empresa_factura=empresa_factura,
        fecha_vencimiento=fecha_vencimiento,
        valor_mensual_base=calculo["valor_mensual_base"],
        valor_adicionales_bn=calculo["valor_adicional_bn"],
        valor_adicionales_color=calculo["valor_adicional_color"],
        subtotal=calculo["subtotal"],
        # Sin IVA por ahora.
        incluye_iva=False,
        porcentaje_iva=0,
        valor_iva=0,
        total_facturado=calculo["total_facturado"],
    )