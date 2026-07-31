"""Informes mensuales (seccion 16 del documento de requerimientos).

Este modulo no tiene tabla propia: cada funcion lee los modelos que ya
existen (Facturacion, Cartera, Contratos, Equipos, Costos, Rentabilidad,
Lecturas, Clientes) y devuelve un diccionario simple listo para
convertir a JSON.

Datos que el documento pide pero que hoy NO se pueden calcular porque
ningun modelo tiene el campo necesario (se devuelven como None con un
comentario en el punto donde se generan; no se inventan ni se aproximan):

  1. 1. Paginas adicionales por B/N y color: Lecturas ya separa el consumo
     en contador_bn/contador_color, pero calcular "adicionales" requiere
     cruzar con Contratos.paginas_bn_incluidas/paginas_color_incluidas
     del contrato correspondiente (ver Modulos/Contratos.py). Se deja
     pendiente hasta que informe_por_equipo/informe_general reciban el
     contrato asociado.
  3. 3. [Resuelto] Equipos instalados / consumo por cliente: se calculan en
     informe_por_cliente reutilizando informe_por_equipo. Sigue pendiente
     el aggregate a nivel de informe_general (paginas_bn/paginas_color del
     punto 1) y la precision cuando Contratos soporte multiequipo.
  4. Equipos.codigo y Equipos.marca: no existen esas columnas (solo
     numero_serie, tipo_equipo, tecnologia, color). Modelos.py tiene un
     catalogo de modelos pero sin FK desde Equipos.
  5. Ingreso generado por equipo: Facturacion no tiene equipo_id.
  6. Contratos con baja rentabilidad: Rentabilidad es un agregado global
     por periodo, no tiene contrato_id.
  7. Compromisos de pago: ningun modelo tiene ese campo.
  8. Mantenimientos preventivos/correctivos (cantidad, estado, fallas por
     equipo, tiempo de respuesta/solucion): el proyecto no tiene modelo
     de mantenimiento.
"""

from datetime import datetime, timedelta

from base_de_datos import SessionLocal
from Persistencia.CarteraRepositorio import CarteraRepositorio
from Persistencia.ClientesRepositorio import ClientesRepositorio
from Persistencia.ContratosRepositorio import ContratosRepositorio
from Persistencia.CostosRepositorio import CostosRepositorio
from Modulos.enums import EstadoFactura, TipoCosto
from Persistencia.EquiposRepositorio import EquiposRepositorio
from Persistencia.FacturacionRepositorio import FacturacionRepositorio
from Persistencia.LecturasRepositorio import LecturasRepositorio
from Persistencia.RentabilidadRepositorio import RentabilidadRepositorio
from Persistencia.EntregasTonerRepositorio import EntregasTonerRepositorio
from Persistencia.ServicioRepositorio import ServicioRepositorio
from Persistencia.MantenimientosPreventivosRepositorio import MantenimientosPreventivosRepositorio
from Modulos.enums import TipoMantenimiento

# Que tipos de costo cuentan como "costos tecnicos" para el informe tecnico.
TIPOS_COSTO_TECNICOS = [
    TipoCosto.MANO_OBRA,
    TipoCosto.DESPLAZAMIENTO,
    TipoCosto.REPUESTO,
    TipoCosto.MANTENIMIENTO_PREVENTIVO,
    TipoCosto.MANTENIMIENTO_CORRECTIVO,
    TipoCosto.REPARACION_MAYOR,
]


def _parse_periodo(periodo):
    """Convierte 'MM-YYYY' (o 'YYYY-MM') en (mes, anio) como enteros."""
    partes = periodo.replace("/", "-").split("-")
    if len(partes) != 2:
        raise ValueError(f"Periodo invalido: '{periodo}'. Se espera formato 'MM-YYYY'.")

    primero, segundo = int(partes[0]), int(partes[1])
    if primero > 12:
        return segundo, primero  # vino como YYYY-MM
    return primero, segundo  # MM-YYYY


def _en_periodo(fecha, mes, anio):
    return bool(fecha) and fecha.month == mes and fecha.year == anio


def informe_general(periodo):
    """Totales del mes: contratos/clientes/equipos, facturacion, cartera,
    costos, utilidad, margen, mantenimientos, alertas y recomendaciones."""
    mes, anio = _parse_periodo(periodo)

    contratos = ContratosRepositorio.obtener_todos()
    clientes = ClientesRepositorio.obtener_todos()
    equipos = EquiposRepositorio.obtener_todos()
    costos = CostosRepositorio.obtener_por_periodo(periodo)
    facturas = FacturacionRepositorio.obtener_por_periodo(periodo)
    cartera = CarteraRepositorio.obtener_todos()
    entregas_toner = EntregasTonerRepositorio.obtener_por_periodo(periodo)

    facturado_mes = sum(f.total_facturado or 0 for f in facturas)
    recaudado_mes = sum(
        f.total_facturado or 0 for f in facturas if f.estado_factura == EstadoFactura.PAGADA
    )
    costos_mes = sum(c.valor_total or 0 for c in costos)
    toneres_entregados = sum(e.cantidad or 0 for e in entregas_toner)

    rentabilidad_periodo = RentabilidadRepositorio.obtener_ultimo_por_periodo(periodo)

    if rentabilidad_periodo:
        utilidad_bruta = rentabilidad_periodo.ganancia
        margen_promedio = rentabilidad_periodo.porcentaje_rentabilidad
    else:
        utilidad_bruta = facturado_mes - costos_mes
        margen_promedio = (utilidad_bruta / facturado_mes * 100) if facturado_mes else 0

    cartera_pendiente = sum(
        c.monto or 0 for c in cartera if (c.estado or "").strip().lower() != "pagada"
    )

    hoy = datetime.utcnow()
    limite = hoy + timedelta(days=60)
    contratos_por_vencer = [c for c in contratos if c.fecha_fin and hoy <= c.fecha_fin <= limite]

    clientes_en_mora_ids = {
        c.cliente_id for c in cartera if "mora" in (c.estado or "").strip().lower()
    }

    recomendaciones = []
    if facturado_mes and margen_promedio < 15:
        recomendaciones.append("Margen del mes por debajo del 15%: revisar costos del periodo.")
    if clientes_en_mora_ids:
        recomendaciones.append(f"{len(clientes_en_mora_ids)} cliente(s) en mora: priorizar gestion de cobro.")
    if contratos_por_vencer:
        recomendaciones.append(f"{len(contratos_por_vencer)} contrato(s) vencen en los proximos 60 dias.")

    correctivos_mes = [
        s for s in ServicioRepositorio.obtener_todos()
        if s.mantenimiento == TipoMantenimiento.CORRECTIVO
        and _en_periodo(s.fecha_solicitud or s.fecha_creacion, mes, anio)
    ]
    conteo_fallas_equipo_general = {}
    for c in correctivos_mes:
        if c.equipo_id:
            conteo_fallas_equipo_general[c.equipo_id] = conteo_fallas_equipo_general.get(c.equipo_id, 0) + 1
    equipos_fallas_recurrentes = [
        eid for eid, n in conteo_fallas_equipo_general.items() if n >= 3
    ]

    return {
        "periodo": periodo,
        "total_contratos": len(contratos),
        "total_clientes": len(clientes),
        "total_equipos": len(equipos),
        "facturado_mes": facturado_mes,
        "recaudado_mes": recaudado_mes,
        "cartera_pendiente": cartera_pendiente,
        "costos_mes": costos_mes,
        "utilidad_bruta": utilidad_bruta,
        "margen_promedio": margen_promedio,
        "paginas_bn": None,
        "paginas_color": None,
        "paginas_adicionales": None,
        "toneres_entregados": toneres_entregados,
        "preventivos_del_mes": len(MantenimientosPreventivosRepositorio.obtener_por_periodo(periodo)),
        "correctivos_del_mes": len(correctivos_mes),
        "contratos_por_vencer": len(contratos_por_vencer),
        "contratos_baja_rentabilidad": None,
        "clientes_en_mora": len(clientes_en_mora_ids),
        "equipos_fallas_recurrentes": len(equipos_fallas_recurrentes),
        "recomendaciones": recomendaciones,
    }


def informe_por_cliente(periodo, cliente_id):
    """Contratos, facturacion, costos, utilidad y margen de un cliente en el periodo."""
    cliente = ClientesRepositorio.obtener_por_id(cliente_id)
    contratos_cliente = ContratosRepositorio.obtener_por_cliente(cliente_id)
    contratos_activos = [
        c for c in contratos_cliente if (c.estado_contrato or "").strip().lower() == "activo"
    ]
    facturas = FacturacionRepositorio.obtener_por_cliente(cliente_id, periodo)
    costos = CostosRepositorio.obtener_por_cliente(cliente_id, periodo)

    equipos_cliente = EquiposRepositorio.obtener_por_cliente(cliente_id)
    equipos_instalados = sum(
        1 for e in equipos_cliente if (e.estado_equipo or "").strip().lower() == "instalado"
    )

    # Consumo del cliente = suma del consumo de cada uno de sus equipos, reutilizando el mismo calculo que ya hace informe_por_equipo.
    consumo_bn = 0
    consumo_color = 0
    for equipo in equipos_cliente:
        datos_equipo = informe_por_equipo(periodo, equipo.id)
        if datos_equipo:
            consumo_bn += datos_equipo["consumo_mensual_bn"] or 0
            consumo_color += datos_equipo["consumo_mensual_color"] or 0
    consumo = consumo_bn + consumo_color

    # Aproximado: se suman las paginas incluidas de todos los contratos activos del cliente. Mientras Contratos no soporte multiequipo
    # (pendiente ya conocido, ver Modulos/Contratos.py), esto asume 1 contrato ~ 1 equipo, igual que el resto del sistema hoy.
    paginas_incluidas = sum(
        (c.paginas_bn_incluidas or 0) + (c.paginas_color_incluidas or 0) for c in contratos_activos
    )
    paginas_adicionales = max(0, consumo - paginas_incluidas)

    facturado = sum(f.total_facturado or 0 for f in facturas)
    pagado = sum(f.total_facturado or 0 for f in facturas if f.estado_factura == EstadoFactura.PAGADA)
    saldo = facturado - pagado
    costos_total = sum(c.valor_total or 0 for c in costos)
    utilidad = facturado - costos_total
    margen = (utilidad / facturado * 100) if facturado else 0

    valor_mensual_contratado = facturas[-1].valor_mensual_base if facturas else None

    return {
        "periodo": periodo,
        "cliente_id": cliente_id,
        "estado_general": cliente.estado_cliente.value if cliente and cliente.estado_cliente else None,
        "contratos_activos": len(contratos_activos),
        "equipos_instalados": equipos_instalados,
        "valor_mensual_contratado": valor_mensual_contratado,
        "consumo": consumo,
        "paginas_incluidas": paginas_incluidas,
        "paginas_adicionales": paginas_adicionales,
        "facturado": facturado,
        "pagado": pagado,
        "saldo": saldo,
        "costos": costos_total,
        "utilidad": utilidad,
        "margen": margen,
    }


def informe_por_equipo(periodo, equipo_id):
    #Datos tecnicos, consumo, costos y fallas de un equipo en el periodo.
    mes, anio = _parse_periodo(periodo)
    equipo = EquiposRepositorio.obtener_por_id(equipo_id)
    if not equipo:
        return None

    lecturas_equipo = LecturasRepositorio.obtener_por_equipo(equipo_id)
    lecturas_periodo = [l for l in lecturas_equipo if _en_periodo(l.fecha_lectura, mes, anio)]
    anteriores = [
        l for l in lecturas_equipo if (l.fecha_lectura.year, l.fecha_lectura.month) < (anio, mes)
    ]

    contador_actual_bn = None
    contador_actual_color = None
    if lecturas_periodo:
        contador_actual_bn = lecturas_periodo[-1].contador_bn
        contador_actual_color = lecturas_periodo[-1].contador_color
    elif lecturas_equipo:
        contador_actual_bn = lecturas_equipo[-1].contador_bn
        contador_actual_color = lecturas_equipo[-1].contador_color

    consumo_mensual_bn = None
    consumo_mensual_color = None
    if lecturas_periodo and anteriores:
        consumo_mensual_bn = lecturas_periodo[-1].contador_bn - anteriores[-1].contador_bn
        consumo_mensual_color = lecturas_periodo[-1].contador_color - anteriores[-1].contador_color

    costos = CostosRepositorio.obtener_por_equipo(equipo_id, periodo)
    costos_total = sum(c.valor_total or 0 for c in costos)

    return {
        "periodo": periodo,
        "equipo_id": equipo_id,
        # Bloqueado: Equipos no tiene columnas 'codigo' ni 'marca'.
        "codigo": None,
        "marca": None,
        "numero_serie": equipo.numero_serie,
        # Desbloqueado: Equipos.cliente_id/contrato_id ya existen en el modelo.
        "cliente_id": equipo.cliente_id,
        "contrato_id": equipo.contrato_id,
        "contador_actual_bn": contador_actual_bn,
        "contador_actual_color": contador_actual_color,
        "consumo_mensual_bn": consumo_mensual_bn,
        "consumo_mensual_color": consumo_mensual_color,
        # Bloqueado: Facturacion no tiene equipo_id.
        "ingreso_generado": None,
        "costos": costos_total,
        "rentabilidad": None,
        "numero_fallas": None,
        "mantenimientos_preventivos": None,
        "mantenimientos_correctivos": None,
        "estado_tecnico": equipo.estado_tecnico,
    }


def informe_cartera(periodo):
    """Facturas emitidas/pagadas/vencidas, saldo y dias de mora por cliente en el periodo."""
    facturas = FacturacionRepositorio.obtener_por_periodo(periodo)
    hoy = datetime.utcnow()

    por_cliente = {}
    for f in facturas:
        datos = por_cliente.setdefault(
            f.cliente_id,
            {
                "cliente_id": f.cliente_id,
                "facturas_emitidas": 0,
                "facturas_pagadas": 0,
                "facturas_vencidas": 0,
                "saldo_pendiente": 0,
                "dias_mora_max": 0,
                "estado": "al_dia",
                "compromisos_pago": None,
            },
        )
        datos["facturas_emitidas"] += 1

        if f.estado_factura == EstadoFactura.PAGADA:
            datos["facturas_pagadas"] += 1
            continue

        datos["saldo_pendiente"] += f.total_facturado or 0
        vencida = f.estado_factura == EstadoFactura.VENCIDA or (
            f.fecha_vencimiento and f.fecha_vencimiento < hoy
        )
        if vencida:
            datos["facturas_vencidas"] += 1
            datos["estado"] = "en_mora"
            if f.fecha_vencimiento:
                dias_mora = (hoy - f.fecha_vencimiento).days
                datos["dias_mora_max"] = max(datos["dias_mora_max"], dias_mora)

    return {
        "periodo": periodo,
        "clientes": list(por_cliente.values()),
    }


def informe_tecnico(periodo):
    #Correctivos/preventivos del periodo, tiempos promedio, equipos con mas fallas, repuestos mas usados y costos tecnicos del periodo.
    mes, anio = _parse_periodo(periodo)

    correctivos = [
        s for s in ServicioRepositorio.obtener_todos()
        if s.mantenimiento == TipoMantenimiento.CORRECTIVO
        and _en_periodo(s.fecha_solicitud or s.fecha_creacion, mes, anio)
    ]

    tiempos_respuesta = [
        (c.fecha_atencion - c.fecha_solicitud).days
        for c in correctivos if c.fecha_atencion and c.fecha_solicitud
    ]
    tiempos_solucion = [
        (c.fecha_solucion - c.fecha_solicitud).days
        for c in correctivos if c.fecha_solucion and c.fecha_solicitud
    ]

    conteo_fallas_equipo = {}
    for c in correctivos:
        if c.equipo_id:
            conteo_fallas_equipo[c.equipo_id] = conteo_fallas_equipo.get(c.equipo_id, 0) + 1
    equipos_con_mas_fallas = sorted(
        conteo_fallas_equipo.items(), key=lambda item: item[1], reverse=True
    )[:5]

    preventivos = MantenimientosPreventivosRepositorio.obtener_por_periodo(periodo)
    preventivos_por_estado = {}
    for p in preventivos:
        preventivos_por_estado[p.estado] = preventivos_por_estado.get(p.estado, 0) + 1

    costos_repuesto = CostosRepositorio.obtener_por_periodo_y_tipo(periodo, TipoCosto.REPUESTO)
    conteo_repuestos = {}
    for c in costos_repuesto:
        clave = (c.descripcion or "sin_descripcion").strip()
        conteo_repuestos[clave] = conteo_repuestos.get(clave, 0) + (c.cantidad or 0)
    repuestos_mas_usados = sorted(conteo_repuestos.items(), key=lambda item: item[1], reverse=True)[:5]

    costos_tecnicos = CostosRepositorio.obtener_por_periodo_y_tipos(periodo, TIPOS_COSTO_TECNICOS)
    costos_tecnicos_por_contrato = {}
    for c in costos_tecnicos:
        costos_tecnicos_por_contrato[c.contrato_id] = costos_tecnicos_por_contrato.get(
            c.contrato_id, 0
        ) + (c.valor_total or 0)

    return {
        "periodo": periodo,
        "correctivos_del_mes": len(correctivos),
        "preventivos_por_estado": preventivos_por_estado,
        "tiempo_promedio_respuesta": (sum(tiempos_respuesta) / len(tiempos_respuesta)) if tiempos_respuesta else None,
        "tiempo_promedio_solucion": (sum(tiempos_solucion) / len(tiempos_solucion)) if tiempos_solucion else None,
        "equipos_con_mas_fallas": [{"equipo_id": eid, "fallas": n} for eid, n in equipos_con_mas_fallas],
        "repuestos_mas_usados": [{"descripcion": desc, "cantidad": cant} for desc, cant in repuestos_mas_usados],
        "costos_tecnicos_por_contrato": costos_tecnicos_por_contrato,
    }