from base_de_datos import SessionLocal
from Modulos.Repuestos import Repuesto


class RepuestosRepositorio:
    """CRUD del catalogo de repuestos (nombre + precio de referencia)."""

    @staticmethod
    def agregar(nombre, precio=0, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            nuevo_repuesto = Repuesto(nombre=nombre, precio=precio)
            db.add(nuevo_repuesto)
            if sesion is None:
                db.commit()
                db.refresh(nuevo_repuesto)
            else:
                db.flush()
            return nuevo_repuesto
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Repuesto).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(repuesto_id):
        db = SessionLocal()
        try:
            return db.query(Repuesto).filter(Repuesto.id == repuesto_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_nombre(nombre):
        db = SessionLocal()
        try:
            return db.query(Repuesto).filter(Repuesto.nombre == nombre).first()
        finally:
            db.close()

    @staticmethod
    def actualizar(repuesto_id, sesion=None, **campos):
        db = sesion if sesion is not None else SessionLocal()
        try:
            repuesto = db.query(Repuesto).filter(Repuesto.id == repuesto_id).first()
            if not repuesto:
                return None
            for nombre_campo, valor in campos.items():
                setattr(repuesto, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(repuesto)
            else:
                db.flush()
            return repuesto
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(repuesto_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            repuesto = db.query(Repuesto).filter(Repuesto.id == repuesto_id).first()
            if repuesto:
                db.delete(repuesto)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()