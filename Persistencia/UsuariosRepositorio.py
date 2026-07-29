from base_de_datos import SessionLocal
from Modulos.Usuarios import Usuarios
from Modulos.enums import EstadoAprobacion


class UsuariosRepositorio:

    @staticmethod
    def agregar(nombre_usuario, email, rol, estado, password_hash=None, estado_aprobacion=EstadoAprobacion.PENDIENTE):
        db = SessionLocal()
        try:
            nuevo_usuario = Usuarios(
                nombre_usuario=nombre_usuario,
                email=email,
                rol=rol,
                estado=estado,
                password_hash=password_hash,
                estado_aprobacion=estado_aprobacion,
            )
            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)
            return nuevo_usuario
        finally:
            db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Usuarios).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_email(email):
        db = SessionLocal()
        try:
            return db.query(Usuarios).filter(Usuarios.email == email).first()
        finally:
            db.close()

    @staticmethod
    def obtener_pendientes():
        db = SessionLocal()
        try:
            return db.query(Usuarios).filter(Usuarios.estado_aprobacion == EstadoAprobacion.PENDIENTE).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(usuario_id):
        db = SessionLocal()
        try:
            return db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
        finally:
            db.close()

    @staticmethod
    def actualizar(usuario_id, **campos):
        """No existia en el Modulos/Usuarios.py original -- mismo motivo
        que en ServicioRepositorio."""
        db = SessionLocal()
        try:
            usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
            if not usuario:
                return None
            for nombre_campo, valor in campos.items():
                setattr(usuario, nombre_campo, valor)
            db.commit()
            db.refresh(usuario)
            return usuario
        finally:
            db.close()

    @staticmethod
    def eliminar(usuario_id):
        db = SessionLocal()
        try:
            usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
            if usuario:
                db.delete(usuario)
                db.commit()
                return True
            return False
        finally:
            db.close()