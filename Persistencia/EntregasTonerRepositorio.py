from datetime import datetime

from base_de_datos import SessionLocal
from Modulos.EntregasToner import EntregaToner
from Persistencia.TiposInsumoRepositorio import TiposInsumoRepositorio


class EntregasTonerRepositorio:
    """CRUD de entregas de insumos (toner, etc.) a clientes/equipos."""

    @staticmethod
    def agregar(
        cliente_id, equipo_id, tipo_insumo_id, persona_entrega,
        contrato_id=None, cantidad=1, costo_unitario=None, costo_total=None,
        persona_recibe="", motivo="", contador_bn=None, contador_color=None,
        observaciones="", evidencia_recibido=None,
        fecha_entrega=None, periodo=None, sesion=None,
    ):
        if costo_unitario is None:
            # Si no viene explicito, se toma el precio actual del tipo de insumo.
            tipo = TiposInsumoRepositorio.obtener_por_id(tipo_insumo_id)
            costo_unitario = tipo.precio if tipo else 0

        if costo_total is None:
            costo_total = cantidad * costo_unitario

        fecha_entrega = fecha_entrega or datetime.utcnow()
        periodo = periodo or f"{fecha_entrega.month:02d}-{fecha_entrega.year}"  # "MM-YYYY"

        db = sesion if sesion is not None else SessionLocal()
        try:
            nueva_entrega = EntregaToner(
                fecha_entrega=fecha_entrega, periodo=periodo,
                cliente_id=cliente_id, contrato_id=contrato_id, equipo_id=equipo_id,
                tipo_insumo_id=tipo_insumo_id, cantidad=cantidad,
                costo_unitario=costo_unitario, costo_total=costo_total,
                persona_entrega=persona_entrega, persona_recibe=persona_recibe,
                motivo=motivo, contador_bn=contador_bn, contador_color=contador_color,
                observaciones=observaciones, evidencia_recibido=evidencia_recibido,
            )
            db.add(nueva_entrega)
            if sesion is None:
                db.commit()
                db.refresh(nueva_entrega)
            else:
                db.flush()
            return nueva_entrega
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(EntregaToner).all()
        finally:
            db.close()

    @staticmethod
    def obtener_todos_ordenado_por_equipo():
        #La necesita Alertas._alertas_toner: recorre todas las entregas agrupadas por equipo y en orden cronologico para comparar cada
        #entrega contra la anterior del mismo equipo.
        db = SessionLocal()
        try:
            return db.query(EntregaToner).order_by(EntregaToner.equipo_id, EntregaToner.fecha_entrega).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(entrega_id):
        db = SessionLocal()
        try:
            return db.query(EntregaToner).filter(EntregaToner.id == entrega_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_periodo(periodo):
        """La usan Informes_mensuales y Dashboard: filtrar en SQL, no
        traer todo a Python y filtrar despues."""
        db = SessionLocal()
        try:
            return db.query(EntregaToner).filter(EntregaToner.periodo == periodo).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_cliente(cliente_id, periodo=None):
        db = SessionLocal()
        try:
            query = db.query(EntregaToner).filter(EntregaToner.cliente_id == cliente_id)
            if periodo:
                query = query.filter(EntregaToner.periodo == periodo)
            return query.order_by(EntregaToner.fecha_entrega).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_equipo(equipo_id):
        db = SessionLocal()
        try:
            return (
                db.query(EntregaToner)
                .filter(EntregaToner.equipo_id == equipo_id)
                .order_by(EntregaToner.fecha_entrega)
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def obtener_ultima_entrega(equipo_id, antes_de=None):
        #Sirve para 'ultima entrega anterior' y para que Alertas compare frecuencia entre entregas mas adelante.
        db = SessionLocal()
        try:
            query = db.query(EntregaToner).filter(EntregaToner.equipo_id == equipo_id)
            if antes_de:
                query = query.filter(EntregaToner.fecha_entrega < antes_de)
            return query.order_by(EntregaToner.fecha_entrega.desc()).first()
        finally:
            db.close()

    @staticmethod
    def actualizar(entrega_id, sesion=None, **campos):
        db = sesion if sesion is not None else SessionLocal()
        try:
            entrega = db.query(EntregaToner).filter(EntregaToner.id == entrega_id).first()
            if not entrega:
                return None
            for nombre_campo, valor in campos.items():
                setattr(entrega, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(entrega)
            else:
                db.flush()
            return entrega
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(entrega_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            entrega = db.query(EntregaToner).filter(EntregaToner.id == entrega_id).first()
            if entrega:
                db.delete(entrega)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()