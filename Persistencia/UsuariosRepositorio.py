from base_de_datos import SessionLocal
from Modulos.Usuarios import Usuarios
from Modulos.enums import EstadoAprobacion


class UsuariosRepositorio:
    """CRUD de usuarios, usado por el flujo de registro/login (routers/auth.py)
    y por crear_admin_inicial.py."""

    @staticmethod
    def agregar(nombre_usuario, email, rol, estado, password_hash=None, estado_aprobacion=EstadoAprobacion.PENDIENTE, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
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
            if sesion is None:
                db.commit()
                db.refresh(nuevo_usuario)
            else:
                db.flush()
            return nuevo_usuario
        finally:
            if sesion is None:
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
    def actualizar(usuario_id, sesion=None, **campos):
        """No existia en el Modulos/Usuarios.py original -- mismo motivo
        que en ServicioRepositorio."""
        db = sesion if sesion is not None else SessionLocal()
        try:
            usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
            if not usuario:
                return None
            for nombre_campo, valor in campos.items():
                setattr(usuario, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(usuario)
            else:
                db.flush()
            return usuario
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(usuario_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
            if usuario:
                db.delete(usuario)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()