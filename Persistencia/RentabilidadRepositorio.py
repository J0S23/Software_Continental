from base_de_datos import SessionLocal
from Modulos.Rentabilidad import Rentabilidad


class RentabilidadRepositorio:
    """CRUD de los resultados de rentabilidad calculados por
    Servicio/RentabilidadAutomatica.py (no calcula nada aqui, solo persiste)."""

    @staticmethod
    def agregar(periodo, ingresos=0, costos=0, ganancia=0, porcentaje_rentabilidad=0,
                contrato_id=None, cliente_id=None, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            nuevo_registro = Rentabilidad(
                periodo=periodo, contrato_id=contrato_id, cliente_id=cliente_id,
                ingresos=ingresos, costos=costos, ganancia=ganancia,
                porcentaje_rentabilidad=porcentaje_rentabilidad,
            )
            db.add(nuevo_registro)
            if sesion is None:
                db.commit()
                db.refresh(nuevo_registro)
            else:
                db.flush()
            return nuevo_registro
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Rentabilidad).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(rentabilidad_id):
        db = SessionLocal()
        try:
            return db.query(Rentabilidad).filter(Rentabilidad.id == rentabilidad_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_contrato(contrato_id, periodo=None):
        db = SessionLocal()
        try:
            query = db.query(Rentabilidad).filter(Rentabilidad.contrato_id == contrato_id)
            if periodo:
                query = query.filter(Rentabilidad.periodo == periodo)
            return query.all()
        finally:
            db.close()

    @staticmethod
    def obtener_ultimo_por_periodo(periodo):
        """La necesita Informes_mensuales.informe_general: el registro de
        Rentabilidad mas reciente de un periodo, si existe."""
        db = SessionLocal()
        try:
            return (
                db.query(Rentabilidad)
                .filter(Rentabilidad.periodo == periodo)
                .order_by(Rentabilidad.id.desc())
                .first()
            )
        finally:
            db.close()

    @staticmethod
    def eliminar(rentabilidad_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            registro = db.query(Rentabilidad).filter(Rentabilidad.id == rentabilidad_id).first()
            if registro:
                db.delete(registro)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()