from base_de_datos import SessionLocal
from Modulos.TiposInsumo import TipoInsumo


class TiposInsumoRepositorio:

    @staticmethod
    def agregar(nombre, precio=0):
        db = SessionLocal()
        try:
            nuevo_tipo = TipoInsumo(nombre=nombre, precio=precio)
            db.add(nuevo_tipo)
            db.commit()
            db.refresh(nuevo_tipo)
            return nuevo_tipo
        finally:
            db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(TipoInsumo).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(tipo_insumo_id):
        db = SessionLocal()
        try:
            return db.query(TipoInsumo).filter(TipoInsumo.id == tipo_insumo_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_nombre(nombre):
        db = SessionLocal()
        try:
            return db.query(TipoInsumo).filter(TipoInsumo.nombre == nombre).first()
        finally:
            db.close()

    @staticmethod
    def actualizar(tipo_insumo_id, **campos):
        db = SessionLocal()
        try:
            tipo = db.query(TipoInsumo).filter(TipoInsumo.id == tipo_insumo_id).first()
            if not tipo:
                return None
            for nombre_campo, valor in campos.items():
                setattr(tipo, nombre_campo, valor)
            db.commit()
            db.refresh(tipo)
            return tipo
        finally:
            db.close()

    @staticmethod
    def eliminar(tipo_insumo_id):
        db = SessionLocal()
        try:
            tipo = db.query(TipoInsumo).filter(TipoInsumo.id == tipo_insumo_id).first()
            if tipo:
                db.delete(tipo)
                db.commit()
                return True
            return False
        finally:
            db.close()