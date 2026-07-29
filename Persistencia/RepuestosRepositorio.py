from base_de_datos import SessionLocal
from Modulos.Repuestos import Repuesto


class RepuestosRepositorio:
    """CRUD del catalogo de repuestos (nombre + precio de referencia)."""

    @staticmethod
    def agregar(nombre, precio=0):
        db = SessionLocal()
        try:
            nuevo_repuesto = Repuesto(nombre=nombre, precio=precio)
            db.add(nuevo_repuesto)
            db.commit()
            db.refresh(nuevo_repuesto)
            return nuevo_repuesto
        finally:
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
    def actualizar(repuesto_id, **campos):
        db = SessionLocal()
        try:
            repuesto = db.query(Repuesto).filter(Repuesto.id == repuesto_id).first()
            if not repuesto:
                return None
            for nombre_campo, valor in campos.items():
                setattr(repuesto, nombre_campo, valor)
            db.commit()
            db.refresh(repuesto)
            return repuesto
        finally:
            db.close()

    @staticmethod
    def eliminar(repuesto_id):
        db = SessionLocal()
        try:
            repuesto = db.query(Repuesto).filter(Repuesto.id == repuesto_id).first()
            if repuesto:
                db.delete(repuesto)
                db.commit()
                return True
            return False
        finally:
            db.close()