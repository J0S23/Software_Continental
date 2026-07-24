from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Poliza(Base):
    __tablename__ = "polizas"
    
    id = Column(Integer, primary_key=True, index=True)
    seriedad = Column(String)
    contrato = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(seriedad, contrato):
        """Agrega una póliza a la BD"""
        db = SessionLocal()
        nueva_poliza = Poliza(seriedad=seriedad, contrato=contrato)
        db.add(nueva_poliza)
        db.commit()
        db.refresh(nueva_poliza)
        db.close()
        return nueva_poliza
    
    @staticmethod
    def obtener_todos():
        """Obtiene todas las pólizas"""
        db = SessionLocal()
        polizas = db.query(Poliza).all()
        db.close()
        return polizas
    
    @staticmethod
    def obtener_por_id(poliza_id):
        """Obtiene una póliza por ID"""
        db = SessionLocal()
        poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()
        db.close()
        return poliza
    
    @staticmethod
    def eliminar(poliza_id):
        """Elimina una póliza por ID"""
        db = SessionLocal()
        poliza = db.query(Poliza).filter(Poliza.id == poliza_id).first()
        if poliza:
            db.delete(poliza)
            db.commit()
        db.close()


Maquinas = Poliza
