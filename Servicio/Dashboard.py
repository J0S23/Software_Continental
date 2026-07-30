"""Dashboard gerencial (seccion 18 del documento de requerimientos).

Este modulo no tiene tabla propia: reutiliza las funciones de calculo de
Modulos/Informes_mensuales.py (facturado, recaudado, cartera, costos,
utilidad, margen) en vez de repetir esa logica, y solo agrega aqui lo
que Informes_mensuales no cubre:

  - Indicadores puntuales del mes actual que informe_general() no calcula:
    contratos activos, equipos instalados/disponibles/en reparacion.
  - Series de tiempo (varios periodos hacia atras) para graficas:
    facturacion/recaudo/utilidad/margen, costos por tipo, ingresos por
    cliente, rentabilidad por cliente y cartera por edad.

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
  - Correctivos por equipo: el proyecto no tiene modelo de mantenimiento
    (punto 8 de Informes_mensuales).
"""

from datetime import datetime

from base_de_datos import SessionLocal
from Persistencia.ClientesRepositorio import ClientesRepositorio
from Persistencia.ContratosRepositorio import ContratosRepositorio
from Persistencia.CostosRepositorio import CostosRepositorio
from Modulos.enums import EstadoFactura
from Persistencia.EquiposRepositorio import EquiposRepositorio
from Persistencia.FacturacionRepositorio import FacturacionRepositorio
from Persistencia.EntregasTonerRepositorio import EntregasTonerRepositorio
from Servicio.Informes_mensuales import _parse_periodo, informe_general, informe_por_cliente
from Persistencia.ServicioRepositorio import ServicioRepositorio
from Modulos.enums import TipoMantenimiento

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

    contratos = ContratosRepositorio.obtener_todos()
    equipos = EquiposRepositorio.obtener_todos()

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
        "toneres_entregados_mes": general["toneres_entregados"],
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
    serie = []
    for periodo in _periodos_hacia_atras(periodo_final, meses):
        costos = CostosRepositorio.obtener_por_periodo(periodo)
        por_tipo = {}
        for c in costos:
            clave = c.tipo_costo.value if c.tipo_costo else "sin_tipo"
            por_tipo[clave] = por_tipo.get(clave, 0) + (c.valor_total or 0)
        serie.append({"periodo": periodo, "costos_por_tipo": por_tipo})
    return serie


def _serie_por_cliente(periodo_final, meses, campo):
    """Helper comun a serie_ingresos_por_cliente y serie_rentabilidad_por_cliente."""
    periodos = _periodos_hacia_atras(periodo_final, meses)
    clientes_ids = [c.id for c in ClientesRepositorio.obtener_todos()]

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
    """Saldo pendiente de facturas agrupado por antiguedad de mora, mes a mes."""
    periodos = _periodos_hacia_atras(periodo_final, meses)
    hoy = datetime.utcnow()

    serie = []
    for periodo in periodos:
        facturas = FacturacionRepositorio.obtener_por_periodo(periodo)
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


def serie_correctivos_por_equipo(periodo_final, meses=6):
    """Correctivos agrupados por equipo, mes a mes."""
    from datetime import datetime as _dt
    serie = []
    for periodo in _periodos_hacia_atras(periodo_final, meses):
        mes, anio = _parse_periodo(periodo)
        correctivos = [
            s for s in ServicioRepositorio.obtener_todos()
            if s.mantenimiento == TipoMantenimiento.CORRECTIVO
            and s.equipo_id
            and (s.fecha_solicitud or s.fecha_creacion)
            and (s.fecha_solicitud or s.fecha_creacion).month == mes
            and (s.fecha_solicitud or s.fecha_creacion).year == anio
        ]
        por_equipo = {}
        for c in correctivos:
            por_equipo[c.equipo_id] = por_equipo.get(c.equipo_id, 0) + 1
        serie.append({"periodo": periodo, "correctivos_por_equipo": por_equipo})
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
    """Cantidad de toner entregado por cliente, mes a mes."""
    serie = []
    for periodo in _periodos_hacia_atras(periodo_final, meses):
        entregas = EntregasTonerRepositorio.obtener_por_periodo(periodo)
        por_cliente = {}
        for e in entregas:
            por_cliente[e.cliente_id] = por_cliente.get(e.cliente_id, 0) + (e.cantidad or 0)
        serie.append({"periodo": periodo, "toneres_por_cliente": por_cliente})
    return serie
