#Requiere Facturacion y Costos ya cargados por contrato/periodo; si no hay ninguno de los dos, ingreso y costos quedan en 0

from Modulos.Costos import Costos
from Persistencia.FacturacionRepositorio import FacturacionRepositorio
from Modulos.Rentabilidad import Rentabilidad
from base_de_datos import SessionLocal


def calcular_rentabilidad(contrato_id, periodo):
    #Suma facturas y costos del contrato en el periodo y calcula ingreso, costo total, utilidad y margen. SIN guardar nada. (Luego si se guarda con genera_rentabilidad)
    #No devuelve None si no hay facturas/costos: en ese caso ingreso y costos simplemente quedan en 0
    #(a diferencia de la facturacion, aqui no hay un dato "obligatorio" sin el cual no se pueda calcular).

    facturas = FacturacionRepositorio.obtener_por_contrato(contrato_id, periodo)

    db = SessionLocal()
    try:
        costos = (
            db.query(Costos)
            .filter(Costos.contrato_id == contrato_id, Costos.periodo == periodo)
            .all()
        )
    finally:
        db.close()

    ingreso_total = sum(f.total_facturado or 0 for f in facturas)
    costo_total = sum(c.valor_total or 0 for c in costos)
    utilidad_bruta = ingreso_total - costo_total
    margen = (utilidad_bruta / ingreso_total * 100) if ingreso_total else 0

    cliente_id = facturas[0].cliente_id if facturas else (costos[0].cliente_id if costos else None)

    return {
        "contrato_id": contrato_id,
        "cliente_id": cliente_id,
        "periodo": periodo,
        "ingreso_total": ingreso_total,
        "costo_total": costo_total,
        "utilidad_bruta": utilidad_bruta,
        "margen": margen,
        "total_facturas": len(facturas),
        "total_costos": len(costos),
    }


def generar_rentabilidad(contrato_id, periodo, forzar=False):
    #Calcula la rentabilidad del contrato/periodo y crea el registro en Rentabilidad.
    #Bloquea la creacion (ValueError) si ya existe un registro de rentabilidad para este contrato+periodo,
    #para evitar duplicados (Rentabilidad.obtener_por_contrato sirve para esa validacion).
    #Se puede saltar con forzar=True si de verdad se quiere otro registro para el mismo contrato+periodo.

    calculo = calcular_rentabilidad(contrato_id, periodo)

    if not forzar:
        ya_calculado = Rentabilidad.obtener_por_contrato(contrato_id, periodo)
        if ya_calculado:
            raise ValueError(
                f"El contrato {contrato_id} ya tiene {len(ya_calculado)} registro(s) de rentabilidad "
                f"para el periodo {periodo}. Usa forzar=True para crear otro de todos modos."
            )

    return Rentabilidad.agregar(
        periodo=periodo,
        contrato_id=contrato_id,
        cliente_id=calculo["cliente_id"],
        ingresos=calculo["ingreso_total"],
        costos=calculo["costo_total"],
        ganancia=calculo["utilidad_bruta"],
        porcentaje_rentabilidad=calculo["margen"],
    )