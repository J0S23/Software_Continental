from base_de_datos import SessionLocal
from Modulos.Sedes import Sedes


class SedesRepositorio:

    @staticmethod
    def agregar(nombre_sede, ciudad, direccion="", telefono="", gerente="", estado_sede="Activa"):
        db = SessionLocal()
        try:
            nueva_sede = Sedes(
                nombre_sede=nombre_sede, ciudad=ciudad, direccion=direccion,
                telefono=telefono, gerente=gerente, estado_sede=estado_sede,
            )
            db.add(nueva_sede)
            db.commit()
            db.refresh(nueva_sede)
            return nueva_sede
        finally:
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
    def actualizar(sede_id, **campos):
        db = SessionLocal()
        try:
            sede = db.query(Sedes).filter(Sedes.id == sede_id).first()
            if not sede:
                return None
            for nombre_campo, valor in campos.items():
                setattr(sede, nombre_campo, valor)
            db.commit()
            db.refresh(sede)
            return sede
        finally:
            db.close()

    @staticmethod
    def eliminar(sede_id):
        db = SessionLocal()
        try:
            sede = db.query(Sedes).filter(Sedes.id == sede_id).first()
            if sede:
                db.delete(sede)
                db.commit()
                return True
            return False
        finally:
            db.close()