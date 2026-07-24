from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Consumibles(Base):
    __tablename__ = "consumibles"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_consumible = Column(String)
    color_consumible = Column(String)
    estado_consumible = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(tipo_consumible, color_consumible, estado_consumible):
        """Agrega un consumible a la BD"""
        db = SessionLocal()
        nuevo_consumible = Consumibles(tipo_consumible=tipo_consumible, color_consumible=color_consumible, estado_consumible=estado_consumible)
        db.add(nuevo_consumible)
        db.commit()
        db.refresh(nuevo_consumible)
        db.close()
        return nuevo_consumible
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los consumibles"""
        db = SessionLocal()
        consumibles = db.query(Consumibles).all()
        db.close()
        return consumibles
    
    @staticmethod
    def obtener_por_id(consumible_id):
        """Obtiene un consumible por ID"""
        db = SessionLocal()
        consumible = db.query(Consumibles).filter(Consumibles.id == consumible_id).first()
        db.close()
        return consumible
    
    @staticmethod
    def eliminar(consumible_id):
        """Elimina un consumible por ID"""
        db = SessionLocal()
        consumible = db.query(Consumibles).filter(Consumibles.id == consumible_id).first()
        if consumible:
            db.delete(consumible)
            db.commit()
        db.close()

