#Requiere un contrato con condiciones económicas configuradas y al menos una lectura del período a facturar
# para alguno de sus equipos activos; de lo contrario, devuelve None

from Persistencia.ContratosRepositorio import ContratosRepositorio
from Persistencia.ContratoEquipoRepositorio import ContratoEquipoRepositorio
from Persistencia.EquiposRepositorio import EquiposRepositorio
from Persistencia.FacturacionRepositorio import FacturacionRepositorio
from Persistencia.LecturasRepositorio import LecturasRepositorio
from Servicio.Informes_mensuales import _parse_periodo


class _AsignacionLegado:
    #Envoltorio minimo para que un contrato que todavia usa el Contratos.equipo_id viejo (sin fila en contrato_equipos) se pueda
    #procesar con el mismo bucle que las asignaciones reales, mientras se corre migrar_contratos_multiequipo.py una sola vez. Una vez migrado,
    #ContratoEquipoRepositorio.obtener_por_contrato() ya trae resultados y esta clase deja de usarse para ese contrato.

    def __init__(self, equipo_id, equipo):
        self.equipo_id = equipo_id
        self.contador_inicial_bn = equipo.contador_inicial_bn or 0 if equipo else 0
        self.contador_inicial_color = equipo.contador_inicial_color or 0 if equipo else 0


def _lectura_actual_y_anterior(equipo_id, contrato_id, periodo):

    #Lectura del periodo pedido y la ultima lectura anterior a ese periodo, para UN equipo especifico
    #dentro de un contrato. Se filtra por equipo_id y contrato_id (una lectura ya trae ambos, ver
    #Modulos/Lecturas.py) porque con multiequipo cada equipo del contrato tiene su propio historial
    #de contadores y no se pueden mezclar entre si.

    mes, anio = _parse_periodo(periodo)
    lecturas_equipo = LecturasRepositorio.obtener_por_equipo(equipo_id)
    lecturas_contrato = [l for l in lecturas_equipo if l.contrato_id == contrato_id]

    lecturas_periodo = [l for l in lecturas_contrato if l.periodo == periodo]
    anteriores = [
        l for l in lecturas_contrato
        if l.fecha_lectura and (l.fecha_lectura.year, l.fecha_lectura.month) < (anio, mes)
    ]

    lectura_actual = lecturas_periodo[-1] if lecturas_periodo else None
    lectura_anterior = anteriores[-1] if anteriores else None
    return lectura_actual, lectura_anterior


def _contador_anterior(lectura_anterior, asignacion):

    #Punto de partida para calcular consumo de un equipo dentro de un contrato:
    #  - si hay lectura anterior de ESE equipo en ESE contrato, se usa su contador (caso normal).
    #  - si NO hay lectura anterior (primera factura del equipo en este contrato), se usa el
    #    contador_inicial_bn/color de la ASIGNACION (contrato_equipos), que es mas preciso que el
    #    contador_inicial del equipo en si -- el equipo pudo haber servido otros contratos antes,
    #    y lo que importa aqui es el punto de partida de ESTE contrato con ESTE equipo.

    if lectura_anterior:
        return lectura_anterior.contador_bn or 0, lectura_anterior.contador_color or 0

    return asignacion.contador_inicial_bn or 0, asignacion.contador_inicial_color or 0


def _asignaciones_del_contrato(contrato):
    #Equipos activos del contrato segun la tabla contrato_equipos. Si todavia no tiene ninguna fila ahi (contrato no migrado) y el contrato
    #tiene el Contratos.equipo_id viejo poblado, cae al modo de compatibilidad de un solo equipo para no romper la facturacion mientras se migra.

    asignaciones = ContratoEquipoRepositorio.obtener_por_contrato(contrato.id, solo_activos=True)
    if asignaciones:
        return asignaciones

    if contrato.equipo_id:
        equipo_legado = EquiposRepositorio.obtener_por_id(contrato.equipo_id)
        return [_AsignacionLegado(contrato.equipo_id, equipo_legado)]

    return []


def calcular_facturacion(contrato_id, periodo):
    #Calcula consumo, paginas adicionales, valor adicional y subtotal/total (sin IVA) para un
    #contrato en un periodo, sumando el consumo de TODOS sus equipos activos. SIN guardar nada.
    #Devuelve None si:
    #- el contrato no existe.
    #- el contrato no tiene ningun equipo activo asignado (ni en contrato_equipos ni en el
    #  Contratos.equipo_id legado).
    #- ninguno de sus equipos activos tiene lectura registrada para ese periodo.
    #Incluye "inconsistencias" (equipos asignados que ya no existen en Equipos) y
    #"equipos_sin_lectura" (equipos activos del contrato sin lectura de este periodo). Ninguna de
    #las dos bloquea el calculo aqui, pero generar_facturacion() si las revisa antes de guardar.

    contrato = ContratosRepositorio.obtener_por_id(contrato_id)
    if not contrato:
        return None

    asignaciones = _asignaciones_del_contrato(contrato)
    if not asignaciones:
        return None

    consumo_total_bn = 0
    consumo_total_color = 0
    detalle_equipos = []
    equipos_sin_lectura = []
    inconsistencias = []

    for asignacion in asignaciones:
        equipo = EquiposRepositorio.obtener_por_id(asignacion.equipo_id)
        if not equipo:
            inconsistencias.append(
                f"El equipo {asignacion.equipo_id} asignado al contrato {contrato_id} "
                "no existe en Equipos."
            )
            continue

        lectura_actual, lectura_anterior = _lectura_actual_y_anterior(
            asignacion.equipo_id, contrato_id, periodo
        )

        if not lectura_actual:
            equipos_sin_lectura.append(asignacion.equipo_id)
            continue

        contador_anterior_bn, contador_anterior_color = _contador_anterior(lectura_anterior, asignacion)
        consumo_bn = max(0, (lectura_actual.contador_bn or 0) - contador_anterior_bn)
        consumo_color = max(0, (lectura_actual.contador_color or 0) - contador_anterior_color)

        consumo_total_bn += consumo_bn
        consumo_total_color += consumo_color

        detalle_equipos.append({
            "equipo_id": asignacion.equipo_id,
            "lectura_id": lectura_actual.id,
            "origen_contador_anterior": "lectura_anterior" if lectura_anterior else "contador_inicial_asignacion",
            "contador_anterior_bn": contador_anterior_bn,
            "contador_actual_bn": lectura_actual.contador_bn,
            "consumo_bn": consumo_bn,
            "contador_anterior_color": contador_anterior_color,
            "contador_actual_color": lectura_actual.contador_color,
            "consumo_color": consumo_color,
        })

    if not detalle_equipos:
        # Ningun equipo del contrato tiene lectura de este periodo (o ninguno existe ya en Equipos).
        return None

    paginas_bn_incluidas = contrato.paginas_bn_incluidas or 0
    paginas_color_incluidas = contrato.paginas_color_incluidas or 0

    # Las paginas incluidas son una condicion economica del CONTRATO,no de cada equipo por separado: se comparan contra el consumo TOTAL sumado de todos los
    # equipos activos, igual que ya se hacia (de forma implicita) cuando solo habia un equipo.
    adicionales_bn = max(0, consumo_total_bn - paginas_bn_incluidas)
    adicionales_color = max(0, consumo_total_color - paginas_color_incluidas)

    valor_adicional_bn = adicionales_bn * (contrato.valor_pagina_adicional_bn or 0)
    valor_adicional_color = adicionales_color * (contrato.valor_pagina_adicional_color or 0)

    valor_mensual_base = contrato.valor_mensual_base or 0
    subtotal = valor_mensual_base + valor_adicional_bn + valor_adicional_color

    return {
        "contrato_id": contrato_id,
        "cliente_id": contrato.cliente_id,
        "periodo": periodo,

        "equipos": detalle_equipos,
        "equipos_sin_lectura": equipos_sin_lectura,

        "consumo_bn": consumo_total_bn,
        "paginas_bn_incluidas": paginas_bn_incluidas,
        "paginas_adicionales_bn": adicionales_bn,
        "valor_adicional_bn": valor_adicional_bn,

        "consumo_color": consumo_total_color,
        "paginas_color_incluidas": paginas_color_incluidas,
        "paginas_adicionales_color": adicionales_color,
        "valor_adicional_color": valor_adicional_color,

        "valor_mensual_base": valor_mensual_base,

        # Sin IVA por ahora: subtotal y total_facturado son el mismo valor.
        "subtotal": subtotal,
        "total_facturado": subtotal,

        "inconsistencias": inconsistencias,
    }


def generar_facturacion(
    contrato_id, periodo, numero_factura, fecha_factura,
    estado_factura, empresa_factura=None, fecha_vencimiento=None,
    forzar=False,
):
    #Calcula la facturacion del contrato/periodo (sumando todos sus equipos activos) y crea el
    #registro en Facturacion. Devuelve None (sin crear nada) si calcular_facturacion() no pudo
    #calcular por falta de contrato, equipos o lecturas.
    #Bloquea la creacion (ValueError) si:
    #  - ya existe una factura de este contrato+periodo (evita duplicados).
    #  - se detectaron inconsistencias (equipo asignado que ya no existe en Equipos).
    #  - falta la lectura de este periodo para alguno de los equipos activos del contrato (evita
    #    facturar un consumo incompleto sin que el usuario lo sepa).
    #Los tres bloqueos se pueden saltar con forzar=True, para cuando el usuario ya vio la
    #advertencia y decide facturar de todas formas solo con los equipos que si tienen lectura.

    calculo = calcular_facturacion(contrato_id, periodo)
    if calculo is None:
        return None

    if not forzar:
        ya_facturado = FacturacionRepositorio.obtener_por_contrato(contrato_id, periodo)
        if ya_facturado:
            raise ValueError(
                f"El contrato {contrato_id} ya tiene {len(ya_facturado)} factura(s) registrada(s) "
                f"para el periodo {periodo}. Usa forzar=True para crear otra de todos modos."
            )

        if calculo["inconsistencias"]:
            raise ValueError(
                "No se genero la factura por inconsistencias en los equipos del contrato: "
                + " | ".join(calculo["inconsistencias"])
            )

        if calculo["equipos_sin_lectura"]:
            raise ValueError(
                "No se genero la factura: faltan lecturas de este periodo para los equipos "
                + ", ".join(str(e) for e in calculo["equipos_sin_lectura"])
                + " del contrato. Usa forzar=True para facturar solo con los equipos que si "
                "tienen lectura."
            )

    return FacturacionRepositorio.agregar(
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