from base_de_datos import SessionLocal
from Modulos.Sedes import Sedes


class SedesRepositorio:
    """CRUD de sedes (sucursales/ubicaciones de la empresa)."""

    @staticmethod
    def agregar(nombre_sede, ciudad, direccion="", telefono="", gerente="", estado_sede="Activa", sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            nueva_sede = Sedes(
                nombre_sede=nombre_sede, ciudad=ciudad, direccion=direccion,
                telefono=telefono, gerente=gerente, estado_sede=estado_sede,
            )
            db.add(nueva_sede)
            if sesion is None:
                db.commit()
                db.refresh(nueva_sede)
            else:
                db.flush()
            return nueva_sede
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Sedes).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(sede_id):
        db = SessionLocal()
        try:
            return db.query(Sedes).filter(Sedes.id == sede_id).first()
        finally:
            db.close()

    @staticmethod
    def actualizar(sede_id, sesion=None, **campos):
        db = sesion if sesion is not None else SessionLocal()
        try:
            sede = db.query(Sedes).filter(Sedes.id == sede_id).first()
            if not sede:
                return None
            for nombre_campo, valor in campos.items():
                setattr(sede, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(sede)
            else:
                db.flush()
            return sede
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(sede_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            sede = db.query(Sedes).filter(Sedes.id == sede_id).first()
            if sede:
                db.delete(sede)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()