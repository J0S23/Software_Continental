from base_de_datos import SessionLocal
from Modulos.Cartera import Cartera


class CarteraRepositorio:

    @staticmethod
    def agregar(cliente_id, monto, estado):
        db = SessionLocal()
        try:
            nueva_cartera = Cartera(cliente_id=cliente_id, monto=monto, estado=estado)
            db.add(nueva_cartera)
            db.commit()
            db.refresh(nueva_cartera)
            return nueva_cartera
        finally:
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
    def actualizar(cartera_id, **campos):
        db = SessionLocal()
        try:
            cartera = db.query(Cartera).filter(Cartera.id == cartera_id).first()
            if not cartera:
                return None
            for nombre_campo, valor in campos.items():
                setattr(cartera, nombre_campo, valor)
            db.commit()
            db.refresh(cartera)
            return cartera
        finally:
            db.close()

    @staticmethod
    def eliminar(cartera_id):
        db = SessionLocal()
        try:
            cartera = db.query(Cartera).filter(Cartera.id == cartera_id).first()
            if cartera:
                db.delete(cartera)
                db.commit()
                return True
            return False
        finally:
            db.close()