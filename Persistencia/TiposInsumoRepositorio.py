from base_de_datos import SessionLocal
from Modulos.TiposInsumo import TipoInsumo


class TiposInsumoRepositorio:
    """CRUD del catalogo de tipos de insumo (nombre + precio); cada Insumo
    individual referencia uno de estos por tipo_insumo_id."""

    @staticmethod
    def agregar(nombre, precio=0, stock_minimo=0, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            nuevo_tipo = TipoInsumo(nombre=nombre, precio=precio, stock_minimo=stock_minimo)
            db.add(nuevo_tipo)
            if sesion is None:
                db.commit()
                db.refresh(nuevo_tipo)
            else:
                db.flush()
            return nuevo_tipo
        finally:
            if sesion is None:
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
    def actualizar(tipo_insumo_id, sesion=None, **campos):
        db = sesion if sesion is not None else SessionLocal()
        try:
            tipo = db.query(TipoInsumo).filter(TipoInsumo.id == tipo_insumo_id).first()
            if not tipo:
                return None
            for nombre_campo, valor in campos.items():
                setattr(tipo, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(tipo)
            else:
                db.flush()
            return tipo
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(tipo_insumo_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            tipo = db.query(TipoInsumo).filter(TipoInsumo.id == tipo_insumo_id).first()
            if tipo:
                db.delete(tipo)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()
