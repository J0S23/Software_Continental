"""Informes mensuales (seccion 16 del documento de requerimientos).

Este modulo no tiene tabla propia: cada funcion lee los modelos que ya
existen (Facturacion, Cartera, Contratos, Equipos, Costos, Rentabilidad,
Lecturas, Clientes) y devuelve un diccionario simple listo para
convertir a JSON.

Datos que el documento pide pero que hoy NO se pueden calcular porque
ningun modelo tiene el campo necesario (se devuelven como None con un
comentario en el punto donde se generan; no se inventan ni se aproximan):

  1. Paginas producidas por B/N y color, y "adicionales": Lecturas.contador
     es un solo numero sin desglose por tipo, y no existe un valor de
     "paginas incluidas en el plan" contra el cual calcular adicionales.
  2. Toneres entregados (cantidad + fecha): Insumos/Consumibles son
     catalogos (tipo/color/estado), no hay un registro transaccional de
     entrega con cantidad y fecha.
  3. Equipos instalados / consumo por cliente: Equipos no tiene cliente_id
     ni contrato_id, asi que no hay forma de vincular un equipo a un
     cliente.
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
from Modulos.Cartera import Cartera
from Modulos.Clientes import Clientes
from Modulos.Contratos import Contratos
from Modulos.Costos import Costos
from Modulos.enums import EstadoFactura, TipoCosto
from Modulos.Equipos import Equipos
from Modulos.Facturacion import Facturacion
from Modulos.Lecturas import Lecturas
from Modulos.Rentabilidad import Rentabilidad

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
    db = SessionLocal()
    try:
        contratos = db.query(Contratos).all()
        clientes = db.query(Clientes).all()
        equipos = db.query(Equipos).all()
        costos = db.query(Costos).filter(Costos.periodo == periodo).all()
        facturas = db.query(Facturacion).filter(Facturacion.periodo == periodo).all()
        cartera = db.query(Cartera).all()

        facturado_mes = sum(f.total_facturado or 0 for f in facturas)
        recaudado_mes = sum(
            f.total_facturado or 0 for f in facturas if f.estado_factura == EstadoFactura.PAGADA
        )
        costos_mes = sum(c.valor_total or 0 for c in costos)

        # Si ya existe un registro de Rentabilidad para este periodo se usa
        # como fuente autoritativa; si no, se calcula directo de
        # facturado/costos del mes.
        rentabilidad_periodo = (
            db.query(Rentabilidad)
            .filter(Rentabilidad.periodo == periodo)
            .order_by(Rentabilidad.id.desc())
            .first()
        )
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
        # Contratos cuya fecha_fin cae dentro de los proximos 60 dias.
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
            # Bloqueado: Lecturas.contador no distingue B/N vs color y no
            # existe una linea base de "paginas incluidas" para calcular
            # adicionales (ver punto 1 del docstring del modulo).
            "paginas_bn": None,
            "paginas_color": None,
            "paginas_adicionales": None,
            # Bloqueado: no hay registro transaccional de entrega de toner
            # con cantidad y fecha (punto 2 del docstring).
            "toneres_entregados": None,
            # Bloqueado: el proyecto no tiene modelo de mantenimiento
            # preventivo/correctivo (punto 8 del docstring del modulo).
            "preventivos_del_mes": None,
            "correctivos_del_mes": None,
            "contratos_por_vencer": len(contratos_por_vencer),
            # Bloqueado: Rentabilidad no tiene contrato_id (punto 6).
            "contratos_baja_rentabilidad": None,
            "clientes_en_mora": len(clientes_en_mora_ids),
            # Bloqueado: depende de mantenimientos correctivos (punto 8).
            "equipos_fallas_recurrentes": None,
            "recomendaciones": recomendaciones,
        }
    finally:
        db.close()


def informe_por_cliente(periodo, cliente_id):
    """Contratos, facturacion, costos, utilidad y margen de un cliente en el periodo."""
    db = SessionLocal()
    try:
        cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()
        contratos_cliente = db.query(Contratos).filter(Contratos.cliente_id == cliente_id).all()
        contratos_activos = [
            c for c in contratos_cliente if (c.estado_contrato or "").strip().lower() == "activo"
        ]
        facturas = (
            db.query(Facturacion)
            .filter(Facturacion.cliente_id == cliente_id, Facturacion.periodo == periodo)
            .all()
        )
        costos = db.query(Costos).filter(Costos.cliente_id == cliente_id, Costos.periodo == periodo).all()

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
            # Bloqueado: Equipos no tiene cliente_id ni contrato_id (punto 3).
            "equipos_instalados": None,
            "valor_mensual_contratado": valor_mensual_contratado,
            # Bloqueado: depende de Lecturas -> equipo -> cliente, y ese
            # vinculo no existe (punto 3).
            "consumo": None,
            # Bloqueado: mismo motivo que paginas_* en informe_general (punto 1).
            "paginas_incluidas": None,
            "paginas_adicionales": None,
            "facturado": facturado,
            "pagado": pagado,
            "saldo": saldo,
            "costos": costos_total,
            "utilidad": utilidad,
            "margen": margen,
        }
    finally:
        db.close()


def informe_por_equipo(periodo, equipo_id):
    """Datos tecnicos, consumo, costos y fallas de un equipo en el periodo."""
    mes, anio = _parse_periodo(periodo)
    db = SessionLocal()
    try:
        equipo = db.query(Equipos).filter(Equipos.id == equipo_id).first()
        if not equipo:
            return None

        lecturas_equipo = (
            db.query(Lecturas)
            .filter(Lecturas.equipo_id == equipo_id)
            .order_by(Lecturas.fecha_lectura)
            .all()
        )
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

        costos = db.query(Costos).filter(Costos.equipo_id == equipo_id, Costos.periodo == periodo).all()
        costos_total = sum(c.valor_total or 0 for c in costos)

        return {
            "periodo": periodo,
            "equipo_id": equipo_id,
            # Bloqueado: Equipos no tiene columnas 'codigo' ni 'marca' (punto 4).
            "codigo": None,
            "marca": None,
            "numero_serie": equipo.numero_serie,
            # Bloqueado: Equipos no tiene cliente_id ni contrato_id (punto 3).
            "cliente_id": None,
            "contrato_id": None,
            "contador_actual_bn": contador_actual_bn,
            "contador_actual_color": contador_actual_color,
            "consumo_mensual_bn": consumo_mensual_bn,
            "consumo_mensual_color": consumo_mensual_color,
            # Bloqueado: Facturacion no tiene equipo_id (punto 5).
            "ingreso_generado": None,
            "costos": costos_total,
            # Bloqueado: depende de ingreso_generado, que esta bloqueado.
            "rentabilidad": None,
            # Bloqueado: el proyecto no tiene modelo de mantenimiento
            # preventivo/correctivo (punto 8 del docstring del modulo).
            "numero_fallas": None,
            "mantenimientos_preventivos": None,
            "mantenimientos_correctivos": None,
            "estado_tecnico": equipo.estado_tecnico,
        }
    finally:
        db.close()


def informe_cartera(periodo):
    """Facturas emitidas/pagadas/vencidas, saldo y dias de mora por cliente en el periodo."""
    db = SessionLocal()
    try:
        facturas = db.query(Facturacion).filter(Facturacion.periodo == periodo).all()
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
                    # Bloqueado: ningun modelo registra compromisos de pago (punto 7).
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
    finally:
        db.close()


def informe_tecnico(periodo):
    """Equipos/repuestos mas frecuentes y costos tecnicos del periodo.

    Bloqueado: el proyecto no tiene modelo de mantenimiento preventivo/
    correctivo (punto 8 del docstring del modulo), asi que no se pueden
    calcular correctivos, preventivos, fallas por equipo ni tiempos de
    respuesta/solucion.
    """
    db = SessionLocal()
    try:
        costos_repuesto = (
            db.query(Costos)
            .filter(Costos.tipo_costo == TipoCosto.REPUESTO, Costos.periodo == periodo)
            .all()
        )
        conteo_repuestos = {}
        for c in costos_repuesto:
            clave = (c.descripcion or "sin_descripcion").strip()
            conteo_repuestos[clave] = conteo_repuestos.get(clave, 0) + (c.cantidad or 0)
        repuestos_mas_usados = sorted(conteo_repuestos.items(), key=lambda item: item[1], reverse=True)[:5]

        costos_tecnicos = (
            db.query(Costos)
            .filter(Costos.periodo == periodo, Costos.tipo_costo.in_(TIPOS_COSTO_TECNICOS))
            .all()
        )
        costos_tecnicos_por_contrato = {}
        for c in costos_tecnicos:
            costos_tecnicos_por_contrato[c.contrato_id] = costos_tecnicos_por_contrato.get(
                c.contrato_id, 0
            ) + (c.valor_total or 0)

        return {
            "periodo": periodo,
            # Bloqueado: ver nota de la funcion (punto 8 del docstring del modulo).
            "correctivos_del_mes": None,
            "preventivos_por_estado": None,
            "tiempo_promedio_respuesta": None,
            "tiempo_promedio_solucion": None,
            "equipos_con_mas_fallas": None,
            "repuestos_mas_usados": [{"descripcion": desc, "cantidad": cant} for desc, cant in repuestos_mas_usados],
            "costos_tecnicos_por_contrato": costos_tecnicos_por_contrato,
        }
    finally:
        db.close()