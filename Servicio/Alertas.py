#Sin tabla propia, igual que Informes_mensuales y Dashboard: lee los
#modelos existentes y devuelve alertas calculadas en el momento.

#Bloqueadas por falta de datos en el modelo actual (no se inventan):
#- Stock bajo de consumibles: Insumos no tiene columna de stock.
#Equipos con fallas recurrentes / mantenimientos: Servicio (correctivo)
#no tiene un contador de fallas por equipo todavia

import unicodedata
from datetime import datetime, timedelta

from base_de_datos import SessionLocal
from Persistencia.AlertaEstadoRepositorio import AlertaEstadoRepositorio
from Persistencia.CarteraRepositorio import CarteraRepositorio
from Persistencia.ContratosRepositorio import ContratosRepositorio
from Persistencia.ContratoEquipoRepositorio import ContratoEquipoRepositorio
from Modulos.enums import EstadoFactura
from Persistencia.EquiposRepositorio import EquiposRepositorio
from Persistencia.FacturacionRepositorio import FacturacionRepositorio
from Persistencia.LecturasRepositorio import LecturasRepositorio
from Persistencia.EntregasTonerRepositorio import EntregasTonerRepositorio
from Persistencia.ServicioRepositorio import ServicioRepositorio
from Persistencia.MantenimientosPreventivosRepositorio import MantenimientosPreventivosRepositorio
from Modulos.enums import TipoMantenimiento

UMBRAL_VENCIMIENTO_DIAS = (90, 60, 30)
UMBRAL_FACTURA_PROXIMA_DIAS = 7
# Dias minimos esperados entre dos entregas de toner al mismo equipo.
# Valor de partida razonable, no un dato del documento de requerimientos, se ajusta si se tiene una referencia real de rendimiento de toner.
UMBRAL_DIAS_ENTREGA_TONER = 20
UMBRAL_FALLAS_RECURRENTES = 3       # correctivos acumulados por equipo para alertar
UMBRAL_FALLAS_CRITICO = 5
UMBRAL_DIAS_SIN_PREVENTIVO = 180    # equipo instalado sin preventivo 'realizado' en este lapso

def _alerta(tipo, nivel, mensaje, referencia_id=None):
    return {
        "id": f"{tipo}:{referencia_id}",
        "tipo": tipo,
        "nivel": nivel,
        "mensaje": mensaje,
        "referencia_id": referencia_id,
    }


# Estados de Cartera.estado que se consideran "sin problema"
# Cualquier otro valor no vacio (vencida 1-30/31-60/61-90, mayor a 90 dias, cobro juridico, o texto libre) se trata como mora.
# Antes esto buscaba la palabra literal "mora" en el texto, pero ninguno de los estados sugeridos en el documento contiene esa palabra -- con ese
# vocabulario la alerta nunca se disparaba. Se corrige invirtiendo el criterio: en vez de listar que SI es mora, se lista que NO lo es.
ESTADOS_CARTERA_AL_DIA = {"al dia", "acuerdo de pago"}


def _normalizar_texto(texto):
    if not texto:
        return ""
    sin_acentos = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sin_acentos.strip().lower()


def _alertas_contratos(hoy):
    alertas = []
    contratos = ContratosRepositorio.obtener_todos()

    for c in contratos:
        if not c.fecha_fin:
            continue

        dias_restantes = (c.fecha_fin - hoy).days
        activo = (c.estado_contrato or "").strip().lower() == "activo"

        if activo and dias_restantes < 0:
            alertas.append(_alerta(
                "contrato_vencido", "critico",
                f"El contrato {c.numero_contrato} esta vencido desde hace {abs(dias_restantes)} dia(s).",
                c.id,
            ))
        elif activo and dias_restantes <= min(UMBRAL_VENCIMIENTO_DIAS):
            alertas.append(_alerta(
                "contrato_por_vencer", "advertencia",
                f"El contrato {c.numero_contrato} vence en {dias_restantes} dia(s).",
                c.id,
            ))

    return alertas


def _alertas_facturacion(hoy):
    alertas = []
    facturas = FacturacionRepositorio.obtener_todos()

    for f in facturas:
        if f.estado_factura == EstadoFactura.PAGADA or f.estado_factura == EstadoFactura.ANULADA:
            continue

        if f.fecha_vencimiento and f.fecha_vencimiento < hoy:
            alertas.append(_alerta(
                "factura_vencida", "critico",
                f"La factura {f.numero_factura} esta vencida.",
                f.id,
            ))
        elif f.fecha_vencimiento and (f.fecha_vencimiento - hoy).days <= UMBRAL_FACTURA_PROXIMA_DIAS:
            alertas.append(_alerta(
                "factura_por_vencer", "advertencia",
                f"La factura {f.numero_factura} vence pronto.",
                f.id,
            ))

    return alertas


def _alertas_cartera():
    alertas = []
    cartera = CarteraRepositorio.obtener_todos()
    clientes_en_mora = {}

    for c in cartera:
        estado_normalizado = _normalizar_texto(c.estado)
        if not estado_normalizado or estado_normalizado in ESTADOS_CARTERA_AL_DIA:
            continue
        clientes_en_mora[c.cliente_id] = clientes_en_mora.get(c.cliente_id, 0) + 1

    for cliente_id, cantidad in clientes_en_mora.items():
        nivel = "critico" if cantidad > 1 else "advertencia"
        alertas.append(_alerta(
            "cliente_en_mora", nivel,
            f"El cliente {cliente_id} tiene {cantidad} registro(s) de cartera en mora.",
            cliente_id,
        ))

    return alertas

def _alertas_toner():
    """Toner entregado con frecuencia inusual: dos entregas al mismo
    equipo separadas por menos de UMBRAL_DIAS_ENTREGA_TONER dias."""
    alertas = []
    entregas = EntregasTonerRepositorio.obtener_todos_ordenado_por_equipo()

    anterior_por_equipo = {}
    for e in entregas:
        anterior = anterior_por_equipo.get(e.equipo_id)

        if anterior and e.fecha_entrega and anterior.fecha_entrega:
            dias = (e.fecha_entrega - anterior.fecha_entrega).days
            if dias < UMBRAL_DIAS_ENTREGA_TONER:
                alertas.append(_alerta(
                    "toner_frecuencia_inusual", "advertencia",
                    f"El equipo {e.equipo_id} recibio dos entregas de toner "
                    f"con solo {dias} dia(s) de diferencia.",
                    e.id,
                ))

        anterior_por_equipo[e.equipo_id] = e

    return alertas

def _alertas_equipos():
    """Equipos instalados sin contrato activo que los referencie, y
    equipos disponibles sin uso (creados hace mas de 90 dias y aun
    'disponible').

    'Con contrato activo' se arma con dos fuentes, para no generar falsos
    positivos mientras se migra a multiequipo (ver migrar_contratos_multiequipo.py):
      - contrato_equipos: la fuente de verdad nueva (multiequipo).
      - Contratos.equipo_id: el campo legado de contratos que aun no se migraron.
    """
    alertas = []
    equipos = EquiposRepositorio.obtener_todos()

    asignaciones_activas = ContratoEquipoRepositorio.obtener_todos_activos()
    equipos_con_contrato = {a.equipo_id for a in asignaciones_activas}

    contratos_activos = ContratosRepositorio.obtener_activos()
    equipos_con_contrato |= {c.equipo_id for c in contratos_activos if c.equipo_id}

    hoy = datetime.utcnow()

    for e in equipos:
        estado = (e.estado_equipo or "").strip().lower()

        if estado == "instalado" and e.id not in equipos_con_contrato:
            alertas.append(_alerta(
                "equipo_sin_contrato", "advertencia",
                f"El equipo {e.numero_serie} figura instalado pero no tiene contrato activo asociado.",
                e.id,
            ))

        if estado == "disponible" and e.fecha_creacion and (hoy - e.fecha_creacion).days > 90:
            alertas.append(_alerta(
                "equipo_sin_uso", "info",
                f"El equipo {e.numero_serie} lleva mas de 90 dias disponible sin asignar.",
                e.id,
            ))

    return alertas


def _alertas_lecturas():
    #Lecturas pendientes y lecturas inconsistentes (contador actual menor al de la lectura anterior del mismo equipo, revisado por
    #separado para blanco y negro y color). Para la primera lectura de un equipo, se compara contra Equipos.contador_inicial_bn/color en vez de
    #saltarse el chequeo -- misma regla que ya usa FacturacionAutomatica._contador_anterior para el primer periodo de un contrato.
    alertas = []
    lecturas = LecturasRepositorio.obtener_todos_ordenado_por_equipo()

    anterior_por_equipo = {}
    for l in lecturas:
        if (l.estado_lectura or "").strip().lower() == "pendiente":
            alertas.append(_alerta(
                "lectura_pendiente", "advertencia",
                f"Lectura pendiente de validar para el equipo {l.equipo_id}.",
                l.id,
            ))

        if l.equipo_id in anterior_por_equipo:
            anterior_bn, anterior_color = anterior_por_equipo[l.equipo_id]
        else:
            equipo = EquiposRepositorio.obtener_por_id(l.equipo_id)
            anterior_bn = equipo.contador_inicial_bn if equipo else None
            anterior_color = equipo.contador_inicial_color if equipo else None

        if anterior_bn is not None and l.contador_bn is not None and l.contador_bn < anterior_bn:
            alertas.append(_alerta(
                "lectura_inconsistente", "critico",
                f"El contador B/N del equipo {l.equipo_id} bajo respecto a la lectura anterior.",
                l.id,
            ))

        if anterior_color is not None and l.contador_color is not None and l.contador_color < anterior_color:
            alertas.append(_alerta(
                "lectura_inconsistente", "critico",
                f"El contador color del equipo {l.equipo_id} bajo respecto a la lectura anterior.",
                l.id,
            ))

        anterior_por_equipo[l.equipo_id] = (l.contador_bn, l.contador_color)

    return alertas

def _alertas_mantenimiento_correctivo():
    """Equipos con fallas recurrentes: cuenta correctivos (Servicio con
    mantenimiento=CORRECTIVO) acumulados por equipo. No filtra por periodo:
    'recurrente' se evalua sobre el historial completo del equipo."""
    alertas = []
    correctivos = ServicioRepositorio.obtener_todos()

    conteo_por_equipo = {}
    for s in correctivos:
        if s.mantenimiento != TipoMantenimiento.CORRECTIVO or not s.equipo_id:
            continue
        conteo_por_equipo[s.equipo_id] = conteo_por_equipo.get(s.equipo_id, 0) + 1

    for equipo_id, cantidad in conteo_por_equipo.items():
        if cantidad < UMBRAL_FALLAS_RECURRENTES:
            continue
        nivel = "critico" if cantidad >= UMBRAL_FALLAS_CRITICO else "advertencia"
        alertas.append(_alerta(
            "equipo_fallas_recurrentes", nivel,
            f"El equipo {equipo_id} acumula {cantidad} correctivo(s) registrados.",
            equipo_id,
        ))

    return alertas


def _alertas_mantenimiento_preventivo(hoy):
    """Preventivos programados que ya vencieron sin marcarse 'realizado' ni
    'cancelado', y equipos instalados sin ningun preventivo 'realizado' en
    los ultimos UMBRAL_DIAS_SIN_PREVENTIVO dias."""
    alertas = []

    vencidos = MantenimientosPreventivosRepositorio.obtener_vencidos_sin_realizar(hoy)
    for m in vencidos:
        alertas.append(_alerta(
            "preventivo_vencido", "advertencia",
            f"El preventivo del equipo {m.equipo_id} programado para "
            f"{m.fecha_programada.strftime('%d/%m/%Y')} no se ha realizado.",
            m.id,
        ))

    equipos = EquiposRepositorio.obtener_todos()
    todos_preventivos = MantenimientosPreventivosRepositorio.obtener_todos()

    ultima_realizada_por_equipo = {}
    for m in todos_preventivos:
        if m.estado != "realizado" or not m.fecha_realizada:
            continue
        actual = ultima_realizada_por_equipo.get(m.equipo_id)
        if not actual or m.fecha_realizada > actual:
            ultima_realizada_por_equipo[m.equipo_id] = m.fecha_realizada

    for e in equipos:
        if (e.estado_equipo or "").strip().lower() != "instalado":
            continue
        ultima = ultima_realizada_por_equipo.get(e.id)
        dias_sin_preventivo = (hoy - ultima).days if ultima else None

        if ultima is None or dias_sin_preventivo > UMBRAL_DIAS_SIN_PREVENTIVO:
            detalle = (
                f"lleva {dias_sin_preventivo} dia(s) sin preventivo" if ultima
                else "no tiene preventivos registrados"
            )
            alertas.append(_alerta(
                "equipo_sin_preventivo", "advertencia",
                f"El equipo {e.numero_serie} esta instalado y {detalle}.",
                e.id,
            ))

    return alertas


def generar_alertas(incluir_descartadas=False):
    hoy = datetime.utcnow()

    alertas = (
        _alertas_contratos(hoy)
        + _alertas_facturacion(hoy)
        + _alertas_cartera()
        + _alertas_equipos()
        + _alertas_lecturas()
        + _alertas_toner()
        + _alertas_mantenimiento_correctivo()
        + _alertas_mantenimiento_preventivo(hoy)
    )

    estados_por_clave = {
        (estado.tipo, estado.referencia_id): estado for estado in AlertaEstadoRepositorio.obtener_todos()
    }

    for a in alertas:
        estado = estados_por_clave.get((a["tipo"], a["referencia_id"]))
        a["leida"] = bool(estado.leida) if estado else False
        a["guardada"] = bool(estado.guardada) if estado else False
        a["descartada"] = bool(estado.descartada) if estado else False

    if not incluir_descartadas:
        alertas = [a for a in alertas if not a["descartada"]]

    orden_nivel = {"critico": 0, "advertencia": 1, "info": 2}
    alertas.sort(key=lambda a: orden_nivel.get(a["nivel"], 3))

    return {
        "generado_en": hoy.isoformat(),
        "total": len(alertas),
        "criticas": sum(1 for a in alertas if a["nivel"] == "critico"),
        "alertas": alertas,
    }