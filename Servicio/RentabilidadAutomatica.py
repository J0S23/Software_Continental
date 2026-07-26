
from Modulos import Costos
from Modulos.Facturacion import Facturacion
from base_de_datos import SessionLocal


def calcular_rentabilidad(contrato_id, periodo):
    #Suma facturas y costos del contrato en el periodo y calcula ingreso, costo total, utilidad y margen. SIN guardar nada. (Luego si se guarda con genera_rentabilidad)
    #No devuelve None si no hay facturas/costos: en ese caso ingreso y costos simplemente quedan en 0
    #(a diferencia de la facturacion, aqui no hay un dato "obligatorio" sin el cual no se pueda calcular).

    db = SessionLocal()
    try:
        facturas = (
            db.query(Facturacion)
            .filter(Facturacion.contrato_id == contrato_id, Facturacion.periodo == periodo)
            .all()
        )
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