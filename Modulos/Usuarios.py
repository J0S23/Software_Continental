from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine
from Modulos.enums import RolUsuario


class Usuarios(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String)
    email = Column(String)
    rol = Column(SQLEnum(RolUsuario))
    estado = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(nombre_usuario, email, rol, estado):
        """Agrega un usuario a la BD"""
        db = SessionLocal()
        try:
            nuevo_usuario = Usuarios(nombre_usuario=nombre_usuario, email=email, rol=rol, estado=estado)
            db.add(nuevo_usuario)
            db.commit()
            db.refresh(nuevo_usuario)
            return nuevo_usuario
        finally:
            db.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todos los usuarios"""
        db = SessionLocal()
        try:
            return db.query(Usuarios).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(usuario_id):
        """Obtiene un usuario por ID"""
        db = SessionLocal()
        try:
            return db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
        finally:
            db.close()

    @staticmethod
    def eliminar(usuario_id):
        """Elimina un usuario por ID"""
        db = SessionLocal()
        try:
            usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
            if usuario:
                db.delete(usuario)
                db.commit()
        finally:
            db.close()
