from base_de_datos import SessionLocal
from Modulos.Cartera import Cartera


class CarteraRepositorio:
    """CRUD de cuentas por cobrar (cartera) por cliente."""

    @staticmethod
    def agregar(cliente_id, monto, estado, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            nueva_cartera = Cartera(cliente_id=cliente_id, monto=monto, estado=estado)
            db.add(nueva_cartera)
            if sesion is None:
                db.commit()
                db.refresh(nueva_cartera)
            else:
                db.flush()
            return nueva_cartera
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Cartera).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(cartera_id):
        db = SessionLocal()
        try:
            return db.query(Cartera).filter(Cartera.id == cartera_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_cliente(cliente_id):
        #No existia en el Modulos/Cartera.py original, pero tanto Informes_mensuales como Alertas filtran cartera por cliente en
        #Python despues de traer todo; se deja disponible para cuando se quiera mover ese filtro a SQL.
        db = SessionLocal()
        try:
            return db.query(Cartera).filter(Cartera.cliente_id == cliente_id).all()
        finally:
            db.close()

    @staticmethod
    def actualizar(cartera_id, sesion=None, **campos):
        db = sesion if sesion is not None else SessionLocal()
        try:
            cartera = db.query(Cartera).filter(Cartera.id == cartera_id).first()
            if not cartera:
                return None
            for nombre_campo, valor in campos.items():
                setattr(cartera, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(cartera)
            else:
                db.flush()
            return cartera
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(cartera_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            cartera = db.query(Cartera).filter(Cartera.id == cartera_id).first()
            if cartera:
                db.delete(cartera)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()