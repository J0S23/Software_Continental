from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Costos(Base):
    __tablename__ = "costos"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_costo = Column(String)
    monto = Column(Float, default=0)
    descripcion = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(tipo_costo, monto=0, descripcion=""):
        """Agrega un costo a la BD"""
        db = SessionLocal()
        nuevo_costo = Costos(tipo_costo=tipo_costo, monto=monto, descripcion=descripcion)
        db.add(nuevo_costo)
        db.commit()
        db.refresh(nuevo_costo)
        db.close()
        return nuevo_costo
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los costos"""
        db = SessionLocal()
        costos = db.query(Costos).all()
        db.close()
        return costos
    
    @staticmethod
    def obtener_por_id(costo_id):
        """Obtiene un costo por ID"""
        db = SessionLocal()
        costo = db.query(Costos).filter(Costos.id == costo_id).first()
        db.close()
        return costo
    
    @staticmethod
    def eliminar(costo_id):
        """Elimina un costo por ID"""
        db = SessionLocal()
        costo = db.query(Costos).filter(Costos.id == costo_id).first()
        if costo:
            db.delete(costo)
            db.commit()
        db.close()
