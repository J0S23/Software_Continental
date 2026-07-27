from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Cartera(Base):
    __tablename__ = "cartera"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer)
    monto = Column(Float)
    estado = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(cliente_id, monto, estado):
        """Agrega un registro de cartera a la BD"""
        db = SessionLocal()
        try:
            nueva_cartera = Cartera(cliente_id=cliente_id, monto=monto, estado=estado)
            db.add(nueva_cartera)
            db.commit()
            db.refresh(nueva_cartera)
            return nueva_cartera
        finally:
            db.close()

    @staticmethod
    def obtener_todos():
        """Obtiene todos los registros de cartera"""
        db = SessionLocal()
        try:
            return db.query(Cartera).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(cartera_id):
        """Obtiene un registro de cartera por ID"""
        db = SessionLocal()
        try:
            return db.query(Cartera).filter(Cartera.id == cartera_id).first()
        finally:
            db.close()

    @staticmethod
    def eliminar(cartera_id):
        """Elimina un registro de cartera por ID"""
        db = SessionLocal()
        try:
            cartera = db.query(Cartera).filter(Cartera.id == cartera_id).first()
            if cartera:
                db.delete(cartera)
                db.commit()
        finally:
            db.close()
