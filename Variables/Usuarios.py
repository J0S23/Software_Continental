from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Usuarios(Base):
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String)
    email = Column(String)
    rol = Column(String)
    estado = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(nombre_usuario, email, rol, estado):
        """Agrega un usuario a la BD"""
        db = SessionLocal()
        nuevo_usuario = Usuarios(nombre_usuario=nombre_usuario, email=email, rol=rol, estado=estado)
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        db.close()
        return nuevo_usuario
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los usuarios"""
        db = SessionLocal()
        usuarios = db.query(Usuarios).all()
        db.close()
        return usuarios
    
    @staticmethod
    def obtener_por_id(usuario_id):
        """Obtiene un usuario por ID"""
        db = SessionLocal()
        usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
        db.close()
        return usuario
    
    @staticmethod
    def eliminar(usuario_id):
        """Elimina un usuario por ID"""
        db = SessionLocal()
        usuario = db.query(Usuarios).filter(Usuarios.id == usuario_id).first()
        if usuario:
            db.delete(usuario)
            db.commit()
        db.close()
