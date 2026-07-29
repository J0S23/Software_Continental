from base_de_datos import SessionLocal
from Modulos.Costos import Costos
from Modulos.enums import TipoCosto


class CostosRepositorio:
    """CRUD de costos asociados a clientes/contratos/equipos, usado para
    calcular rentabilidad (Servicio/RentabilidadAutomatica.py) e informes."""

    # Costos automaticos sugeridos (seccion 11.3): valores estandar de
    # referencia para agilizar el registro de un costo nuevo. Hoy son
    # placeholders en 0; se ajustan cuando se definan los valores reales.
    COSTOS_SUGERIDOS = {
        "visita_tecnica": 0,
        "desplazamiento_local": 0,
        "desplazamiento_fuera_ciudad": 0,
        "depreciacion_mensual_equipo": 0,
        "costo_por_pagina": 0,
        "toner_por_referencia": 0,
    }

    @staticmethod
    def obtener_costos_sugeridos():
        return CostosRepositorio.COSTOS_SUGERIDOS

    @staticmethod
    def agregar(
        fecha_costo, periodo, cliente_id, contrato_id, equipo_id,
        tipo_costo, descripcion, responsable,
        cantidad=1, valor_unitario=0, valor_total=None,
        soporte=None, observaciones=None, repuesto_id=None,
    ):
        if valor_total is None:
            valor_total = cantidad * valor_unitario  # se calcula solo si no lo mandan explicito

        db = SessionLocal()
        try:
            nuevo_costo = Costos(
                fecha_costo=fecha_costo, periodo=periodo, cliente_id=cliente_id,
                contrato_id=contrato_id, equipo_id=equipo_id, tipo_costo=tipo_costo,
                descripcion=descripcion, cantidad=cantidad, valor_unitario=valor_unitario,
                valor_total=valor_total, responsable=responsable, soporte=soporte,
                observaciones=observaciones, repuesto_id=repuesto_id,
            )
            db.add(nuevo_costo)
            db.commit()
            db.refresh(nuevo_costo)
            return nuevo_costo
        finally:
            db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Costos).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_cliente(cliente_id, periodo=None):
        """La necesita Informes_mensuales.informe_por_cliente."""
        db = SessionLocal()
        try:
            query = db.query(Costos).filter(Costos.cliente_id == cliente_id)
            if periodo:
                query = query.filter(Costos.periodo == periodo)
            return query.all()
        finally:
            db.close()
    
    @staticmethod
    def obtener_por_id(costo_id):
        db = SessionLocal()
        try:
            return db.query(Costos).filter(Costos.id == costo_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_periodo(periodo):
        """La necesita Informes_mensuales.informe_general y
        Dashboard.serie_costos_por_tipo."""
        db = SessionLocal()
        try:
            return db.query(Costos).filter(Costos.periodo == periodo).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_contrato(contrato_id, periodo=None):
        """La necesita RentabilidadAutomatica.calcular_rentabilidad."""
        db = SessionLocal()
        try:
            query = db.query(Costos).filter(Costos.contrato_id == contrato_id)
            if periodo:
                query = query.filter(Costos.periodo == periodo)
            return query.all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_equipo(equipo_id, periodo=None):
        """La necesita Informes_mensuales.informe_por_equipo."""
        db = SessionLocal()
        try:
            query = db.query(Costos).filter(Costos.equipo_id == equipo_id)
            if periodo:
                query = query.filter(Costos.periodo == periodo)
            return query.all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_periodo_y_tipo(periodo, tipo_costo):
        """La necesita Informes_mensuales.informe_tecnico para
        repuestos_mas_usados (tipo_costo=TipoCosto.REPUESTO)."""
        db = SessionLocal()
        try:
            return (
                db.query(Costos)
                .filter(Costos.tipo_costo == tipo_costo, Costos.periodo == periodo)
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def obtener_por_periodo_y_tipos(periodo, tipos_costo):
        """La necesita Informes_mensuales.informe_tecnico para
        costos_tecnicos_por_contrato (TIPOS_COSTO_TECNICOS, una lista)."""
        db = SessionLocal()
        try:
            return (
                db.query(Costos)
                .filter(Costos.periodo == periodo, Costos.tipo_costo.in_(tipos_costo))
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def actualizar(costo_id, **campos):
        db = SessionLocal()
        try:
            costo = db.query(Costos).filter(Costos.id == costo_id).first()
            if not costo:
                return None
            for nombre_campo, valor in campos.items():
                setattr(costo, nombre_campo, valor)
            db.commit()
            db.refresh(costo)
            return costo
        finally:
            db.close()

    @staticmethod
    def eliminar(costo_id):
        db = SessionLocal()
        try:
            costo = db.query(Costos).filter(Costos.id == costo_id).first()
            if costo:
                db.delete(costo)
                db.commit()
                return True
            return False
        finally:
            db.close()