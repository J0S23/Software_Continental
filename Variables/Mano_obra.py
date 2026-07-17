from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class ManoObra(Base):
    __tablename__ = "mano_obra"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String)
    pago = Column(Float)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(nombre, pago):
        """Agrega mano de obra a la BD"""
        db = SessionLocal()
        nueva_mano_obra = ManoObra(nombre=nombre, pago=pago)
        db.add(nueva_mano_obra)
        db.commit()
        db.refresh(nueva_mano_obra)
        db.close()
        return nueva_mano_obra
    
    @staticmethod
    def obtener_todos():
        """Obtiene toda la mano de obra"""
        db = SessionLocal()
        mano_obra = db.query(ManoObra).all()
        db.close()
        return mano_obra
    
    @staticmethod
    def obtener_por_id(mano_obra_id):
        """Obtiene mano de obra por ID"""
        db = SessionLocal()
        mano_obra = db.query(ManoObra).filter(ManoObra.id == mano_obra_id).first()
        db.close()
        return mano_obra
    
    @staticmethod
    def eliminar(mano_obra_id):
        """Elimina mano de obra por ID"""
        db = SessionLocal()
        mano_obra = db.query(ManoObra).filter(ManoObra.id == mano_obra_id).first()
        if mano_obra:
            db.delete(mano_obra)
            db.commit()
        db.close()


Maquinas = ManoObra
