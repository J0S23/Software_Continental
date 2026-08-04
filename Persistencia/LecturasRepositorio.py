from base_de_datos import SessionLocal
from Modulos.Lecturas import Lecturas


class LecturasRepositorio:
    """CRUD de lecturas de contadores de equipos, base para calcular paginas
    adicionales a facturar (ver Servicio/FacturacionAutomatica.py)."""

    @staticmethod
    def agregar(equipo_id, medio_lectura, estado_lectura,
        contador_bn=0, contador_color=0,
        contrato_id=None, cliente_id=None, periodo=None,
        fecha_lectura=None, sesion=None):
        from datetime import datetime
        db = sesion if sesion is not None else SessionLocal()
        try:
            nueva_lectura = Lecturas(
                equipo_id=equipo_id,
                medio_lectura=medio_lectura,
                estado_lectura=estado_lectura,
                contador_bn=contador_bn,
                contador_color=contador_color,
                contrato_id=contrato_id,
                cliente_id=cliente_id,
                periodo=periodo,
                fecha_lectura=fecha_lectura or datetime.utcnow(),
            )
            db.add(nueva_lectura)
            if sesion is None:
                db.commit()
                db.refresh(nueva_lectura)
            else:
                db.flush()
            return nueva_lectura
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Lecturas).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(lectura_id):
        db = SessionLocal()
        try:
            return db.query(Lecturas).filter(Lecturas.id == lectura_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_contrato(contrato_id, periodo=None):
        """La necesita FacturacionAutomatica para traer las lecturas de un
        contrato, opcionalmente filtradas por periodo."""
        db = SessionLocal()
        try:
            query = db.query(Lecturas).filter(Lecturas.contrato_id == contrato_id)
            if periodo:
                query = query.filter(Lecturas.periodo == periodo)
            return query.order_by(Lecturas.fecha_lectura).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_equipo(equipo_id):
        """La necesita Informes_mensuales.informe_por_equipo, que antes
        hacia esta misma query directo con db.query()."""
        db = SessionLocal()
        try:
            return (
                db.query(Lecturas)
                .filter(Lecturas.equipo_id == equipo_id)
                .order_by(Lecturas.fecha_lectura)
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def obtener_todos_ordenado_por_equipo():
        """La necesita Alertas._alertas_lecturas: recorre todas las
        lecturas agrupadas por equipo y en orden cronologico para
        comparar cada lectura contra la anterior del mismo equipo."""
        db = SessionLocal()
        try:
            return db.query(Lecturas).order_by(Lecturas.equipo_id, Lecturas.fecha_lectura).all()
        finally:
            db.close()

    @staticmethod
    def actualizar(lectura_id, sesion=None, **campos):
        db = sesion if sesion is not None else SessionLocal()
        try:
            lectura = db.query(Lecturas).filter(Lecturas.id == lectura_id).first()
            if not lectura:
                return None
            for nombre_campo, valor in campos.items():
                setattr(lectura, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(lectura)
            else:
                db.flush()
            return lectura
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(lectura_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            lectura = db.query(Lecturas).filter(Lecturas.id == lectura_id).first()
            if lectura:
                db.delete(lectura)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()