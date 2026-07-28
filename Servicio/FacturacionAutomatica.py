#Requiere un contrato con condiciones económicas configuradas y una lectura del período a facturar; de lo contrario, devuelve None

from Persistencia.ContratosRepositorio import ContratosRepositorio
from Persistencia.EquiposRepositorio import EquiposRepositorio
from Persistencia.FacturacionRepositorio import FacturacionRepositorio
from Persistencia.LecturasRepositorio import LecturasRepositorio
from Servicio.Informes_mensuales import _parse_periodo


def _lectura_actual_y_anterior(contrato_id, periodo):

    #Lectura del periodo pedido y la ultima lectura anterior a ese periodo, ambas del mismo contrato. 
    #Se usa contrato_id (no equipo_id) porque un contrato puede haber cambiado de equipo (CambiosRetiro) y
    #lo que importa para facturar es el historial del contrato.

    mes, anio = _parse_periodo(periodo)
    lecturas = LecturasRepositorio.obtener_por_contrato(contrato_id)

    lecturas_periodo = [l for l in lecturas if l.periodo == periodo]
    anteriores = [
        l for l in lecturas
        if l.fecha_lectura and (l.fecha_lectura.year, l.fecha_lectura.month) < (anio, mes)
    ]

    lectura_actual = lecturas_periodo[-1] if lecturas_periodo else None
    lectura_anterior = anteriores[-1] if anteriores else None
    return lectura_actual, lectura_anterior


def _validar_consistencia_equipo(contrato, lectura):

    #Cruza el equipo de la lectura contra el equipo esperado del contrato, usando DOS fuentes independientes
    #para no confiar en un solo punto de verdad:
    #  - Contratos.equipo_id  (que dice el contrato que tiene instalado)
    #  - Equipos.contrato_id  (que dice el equipo en que contrato esta)
    #Si un lado se actualizo y el otro no (por ejemplo, se hizo un CambiosRetiro y no se actualizo el
    #contrato, o viceversa), esta funcion lo detecta en vez de asumir que un solo campo es la verdad.
    #Devuelve una lista de strings con las inconsistencias encontradas (vacia si todo cuadra). No lanza
    #excepcion aqui: quien llama (generar_facturacion) decide si eso bloquea la generacion.

    inconsistencias = []

    equipo = EquiposRepositorio.obtener_por_id(lectura.equipo_id)
    if not equipo:
        inconsistencias.append(
            f"La lectura {lectura.id} referencia el equipo {lectura.equipo_id}, que no existe en Equipos."
        )
        return inconsistencias

    # Fuente 1: el contrato dice cual es su equipo.
    if contrato.equipo_id and contrato.equipo_id != lectura.equipo_id:
        inconsistencias.append(
            f"El contrato {contrato.id} tiene asignado el equipo {contrato.equipo_id}, "
            f"pero la lectura es del equipo {lectura.equipo_id}."
        )

    # Fuente 2: el equipo dice en que contrato esta instalado.
    if equipo.contrato_id and equipo.contrato_id != contrato.id:
        inconsistencias.append(
            f"El equipo {lectura.equipo_id} figura instalado en el contrato {equipo.contrato_id}, "
            f"no en el contrato {contrato.id}."
        )

    return inconsistencias


def _contador_anterior(lectura_anterior, equipo):

    #Punto de partida para calcular consumo:
    #  - si hay lectura anterior, se usa su contador (caso normal, mes a mes).
    #  - si NO hay lectura anterior (primera factura del contrato), se usa el contador_inicial_bn/color del equipo en vez
    #    de asumir 0, que disparaba un consumo falso e inflado en la primera factura si el equipo ya traia contador
    #    de fabrica o de un cliente anterior.
    #  - si tampoco hay equipo (no deberia pasar si ya se valido consistencia, pero por seguridad), se cae a 0 como ultimo recurso.

    if lectura_anterior:
        return lectura_anterior.contador_bn or 0, lectura_anterior.contador_color or 0

    if equipo:
        return equipo.contador_inicial_bn or 0, equipo.contador_inicial_color or 0

    return 0, 0


def calcular_facturacion(contrato_id, periodo):
    #Calcula consumo, paginas adicionales, valor adicional y subtotal/total (sin IVA) para un contrato en un periodo, SIN guardar nada.
    #Devuelve None si:
    #- el contrato no existe.
    #- no hay lectura registrada para ese periodo (no se puede facturar a ciegas).
    #Incluye "inconsistencias": lista de problemas equipo-contrato detectados (vacia si todo esta bien).
    #No bloquea el calculo aqui, pero generar_facturacion() si la revisa antes de guardar.

    contrato = ContratosRepositorio.obtener_por_id(contrato_id)
    if not contrato:
        return None

    lectura_actual, lectura_anterior = _lectura_actual_y_anterior(contrato_id, periodo)
    if not lectura_actual:
        return None

    inconsistencias = _validar_consistencia_equipo(contrato, lectura_actual)

    equipo = EquiposRepositorio.obtener_por_id(lectura_actual.equipo_id)
    contador_anterior_bn, contador_anterior_color = _contador_anterior(lectura_anterior, equipo)

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

        # util para saber si el contador anterior vino de una lectura previa o del contador inicial del equipo (primera factura del contrato).
        "origen_contador_anterior": "lectura_anterior" if lectura_anterior else "contador_inicial_equipo",

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

        "inconsistencias": inconsistencias,
    }


def generar_facturacion(
    contrato_id, periodo, numero_factura, fecha_factura,
    estado_factura, empresa_factura=None, fecha_vencimiento=None,
    forzar=False,
):
    #Calcula la facturacion del contrato/periodo y crea el registro en Facturacion. 
    #Devuelve None (sin crear nada) si calcular_facturacion() no pudo calcular por falta de contrato o de lectura.
    #Bloquea la creacion (ValueError) si:
    #  - ya existe una factura de este contrato+periodo (evita duplicados).
    #  - se detectaron inconsistencias equipo-contrato (evita facturar con datos de un equipo
    #    que ya no corresponde a este contrato).
    #Ambos bloqueos se pueden saltar con forzar=True, para cuando el usuario ya vio la advertencia
    #y decide seguir de todas formas (por ejemplo desde un modal de confirmacion en el frontend).

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
                "No se genero la factura por inconsistencias equipo-contrato: "
                + " | ".join(calculo["inconsistencias"])
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