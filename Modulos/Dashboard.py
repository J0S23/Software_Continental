"""Dashboard gerencial (seccion 18 del documento de requerimientos).

Este modulo no tiene tabla propia: reutiliza las funciones de calculo de
Modulos/Informes_mensuales.py (facturado, recaudado, cartera, costos,
utilidad, margen, mantenimientos) en vez de repetir esa logica, y solo
agrega aqui lo que Informes_mensuales no cubre:

  - Indicadores puntuales del mes actual que informe_general() no calcula:
    contratos activos, equipos instalados/disponibles/en reparacion.
  - Series de tiempo (varios periodos hacia atras) para graficas:
    facturacion/recaudo/utilidad/margen, costos por tipo, ingresos por
    cliente, rentabilidad por cliente, cartera por edad y correctivos por
    equipo.

Bloqueado, por los mismos motivos ya documentados en el docstring de
Informes_mensuales.py (no se inventan ni se aproximan):

  - Consumo de paginas por cliente: depende de Lecturas -> equipo ->
    cliente, y Equipos no tiene cliente_id ni contrato_id (punto 3 de
    Informes_mensuales).
  - Toneres por cliente: no existe un registro transaccional de entrega
    de toner con cantidad, fecha y cliente (punto 2 de Informes_mensuales).
  - Contratos con baja rentabilidad: Rentabilidad no tiene contrato_id
    (punto 6 de Informes_mensuales); se expone tal cual lo devuelve
    informe_general().
"""

from datetime import datetime

from base_de_datos import SessionLocal
from Modulos.Clientes import Clientes
from Modulos.Contratos import Contratos
from Modulos.Costos import Costos
from Modulos.enums import EstadoFactura
from Modulos.Equipos import Equipos
from Modulos.Facturacion import Facturacion
from Modulos.Informes_mensuales import _en_periodo, _parse_periodo, informe_general, informe_por_cliente
from Modulos.Mantenimiento_correctivo import MantenimientoCorrectivo

# Limites de dias de mora para agrupar cartera por antiguedad.
RANGOS_ANTIGUEDAD_CARTERA = (
    (30, "1_30"),
    (60, "31_60"),
    (90, "61_90"),
)


def _periodos_hacia_atras(periodo_final, meses):
    """Genera 'meses' periodos 'MM-YYYY' terminando en periodo_final, del mas antiguo al mas reciente."""
    mes, anio = _parse_periodo(periodo_final)
    periodos = []

    for i in range(meses - 1, -1, -1):
        m, a = mes - i, anio
        while m <= 0:
            m += 12
            a -= 1
        periodos.append(f"{m:02d}-{a}")

    return periodos


def dashboard_snapshot(periodo):
    """Indicadores puntuales del mes actual.

    Reutiliza informe_general() para lo que ya calcula (facturado,
    recaudado, cartera, costos, utilidad, margen, contratos por vencer,
    contratos con baja rentabilidad, clientes en mora, equipos con fallas
    recurrentes) y agrega contratos activos y equipos por estado.
    """
    general = informe_general(periodo)

    db = SessionLocal()
    try:
        contratos = db.query(Contratos).all()
        equipos = db.query(Equipos).all()
    finally:
        db.close()

    contratos_activos = sum(
        1 for c in contratos if (c.estado_contrato or "").strip().lower() == "activo"
    )
    equipos_instalados = sum(
        1 for e in equipos if (e.estado_equipo or "").strip().lower() == "instalado"
    )
    equipos_disponibles = sum(
        1 for e in equipos if (e.estado_equipo or "").strip().lower() == "disponible"
    )
    equipos_en_reparacion = sum(
        1 for e in equipos if (e.estado_equipo or "").strip().lower() == "en_reparacion"
    )

    return {
        "periodo": periodo,
        "facturado_mes": general["facturado_mes"],
        "recaudado_mes": general["recaudado_mes"],
        "cartera_pendiente": general["cartera_pendiente"],
        "costos_mes": general["costos_mes"],
        "utilidad_bruta": general["utilidad_bruta"],
        "margen_promedio": general["margen_promedio"],
        "contratos_activos": contratos_activos,
        "equipos_instalados": equipos_instalados,
        "equipos_disponibles": equipos_disponibles,
        "equipos_en_reparacion": equipos_en_reparacion,
        "contratos_por_vencer": general["contratos_por_vencer"],
        # Bloqueado: ver docstring del modulo y punto 6 de Informes_mensuales.
        "contratos_baja_rentabilidad": general["contratos_baja_rentabilidad"],
        "clientes_en_mora": general["clientes_en_mora"],
        "equipos_fallas_recurrentes": general["equipos_fallas_recurrentes"],
    }


def serie_financiera(periodo_final, meses=6):
    """Facturado, recaudado, utilidad y margen mes a mes.

    Cubre las series de "facturacion", "utilidad" y "margen de
    rentabilidad" pedidas para el dashboard en una sola llamada por
    periodo, reutilizando informe_general().
    """
    serie = []

    for periodo in _periodos_hacia_atras(periodo_final, meses):
        general = informe_general(periodo)
        serie.append(
            {
                "periodo": periodo,
                "facturado": general["facturado_mes"],
                "recaudado": general["recaudado_mes"],
                "utilidad": general["utilidad_bruta"],
                "margen": general["margen_promedio"],
            }
        )

    return serie


def serie_costos_por_tipo(periodo_final, meses=6):
    """Costos agrupados por tipo_costo, mes a mes."""
    periodos = _periodos_hacia_atras(periodo_final, meses)

    db = SessionLocal()
    try:
        serie = []
        for periodo in periodos:
            costos = db.query(Costos).filter(Costos.periodo == periodo).all()
            por_tipo = {}
            for c in costos:
                clave = c.tipo_costo.value if c.tipo_costo else "sin_tipo"
                por_tipo[clave] = por_tipo.get(clave, 0) + (c.valor_total or 0)
            serie.append({"periodo": periodo, "costos_por_tipo": por_tipo})
        return serie
    finally:
        db.close()


def _serie_por_cliente(periodo_final, meses, campo):
    """Helper comun a serie_ingresos_por_cliente y serie_rentabilidad_por_cliente.

    Reutiliza informe_por_cliente() por cliente y periodo en vez de
    recalcular facturado/utilidad/margen aqui.
    """
    periodos = _periodos_hacia_atras(periodo_final, meses)

    db = SessionLocal()
    try:
        clientes_ids = [c.id for c in db.query(Clientes).all()]
    finally:
        db.close()

    serie = []
    for periodo in periodos:
        valores_por_cliente = {
            cliente_id: informe_por_cliente(periodo, cliente_id)[campo]
            for cliente_id in clientes_ids
        }
        serie.append({"periodo": periodo, "valores_por_cliente": valores_por_cliente})

    return serie


def serie_ingresos_por_cliente(periodo_final, meses=6):
    """Facturado por cliente, mes a mes."""
    return _serie_por_cliente(periodo_final, meses, campo="facturado")


def serie_rentabilidad_por_cliente(periodo_final, meses=6):
    """Margen (%) por cliente, mes a mes."""
    return _serie_por_cliente(periodo_final, meses, campo="margen")


def serie_cartera_por_edad(periodo_final, meses=6):
    """Saldo pendiente de facturas agrupado por antiguedad de mora, mes a mes.

    Usa Facturacion.fecha_vencimiento igual que
    Informes_mensuales.informe_cartera, pero agrupado en rangos de dias en
    vez de por cliente.
    """
    periodos = _periodos_hacia_atras(periodo_final, meses)
    hoy = datetime.utcnow()

    db = SessionLocal()
    try:
        serie = []
        for periodo in periodos:
            facturas = db.query(Facturacion).filter(Facturacion.periodo == periodo).all()
            rangos = {"al_dia": 0, "1_30": 0, "31_60": 0, "61_90": 0, "mas_90": 0}

            for f in facturas:
                if f.estado_factura == EstadoFactura.PAGADA:
                    continue

                saldo = f.total_facturado or 0

                if not f.fecha_vencimiento or f.fecha_vencimiento >= hoy:
                    rangos["al_dia"] += saldo
                    continue

                dias_mora = (hoy - f.fecha_vencimiento).days
                clave = "mas_90"
                for limite, nombre_rango in RANGOS_ANTIGUEDAD_CARTERA:
                    if dias_mora <= limite:
                        clave = nombre_rango
                        break
                rangos[clave] += saldo

            serie.append({"periodo": periodo, "cartera_por_edad": rangos})

        return serie
    finally:
        db.close()


def serie_correctivos_por_equipo(periodo_final, meses=6):
    """Cantidad de mantenimientos correctivos por equipo, mes a mes."""
    periodos = _periodos_hacia_atras(periodo_final, meses)

    db = SessionLocal()
    try:
        correctivos = db.query(MantenimientoCorrectivo).all()
    finally:
        db.close()

    serie = []
    for periodo in periodos:
        mes, anio = _parse_periodo(periodo)
        conteo = {}
        for c in correctivos:
            if _en_periodo(c.fecha_mantenimiento, mes, anio):
                conteo[c.equipo_id] = conteo.get(c.equipo_id, 0) + 1
        serie.append({"periodo": periodo, "correctivos_por_equipo": conteo})

    return serie


def serie_consumo_paginas_por_cliente(periodo_final, meses=6):
    """Bloqueado: Equipos no tiene cliente_id ni contrato_id, y Lecturas.contador
    no distingue B/N vs color (puntos 1 y 3 de Informes_mensuales). No hay
    forma de vincular una lectura de contador con un cliente."""
    return [
        {"periodo": periodo, "consumo_por_cliente": None}
        for periodo in _periodos_hacia_atras(periodo_final, meses)
    ]


def serie_toneres_por_cliente(periodo_final, meses=6):
    """Bloqueado: no existe un registro transaccional de entrega de toner con
    cantidad, fecha y cliente asociado (punto 2 de Informes_mensuales).
    Insumos es un catalogo (tipo/color/estado), no un historial de entregas."""
    return [
        {"periodo": periodo, "toneres_por_cliente": None}
        for periodo in _periodos_hacia_atras(periodo_final, meses)
    ]
