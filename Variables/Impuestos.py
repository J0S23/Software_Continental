from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Impuesto(Base):
    __tablename__ = "impuestos"
    
    id = Column(Integer, primary_key=True, index=True)
    municipal = Column(Float)
    departamental = Column(Float)
    pro_deporte = Column(Float)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(municipal, departamental, pro_deporte):
        """Agrega un impuesto a la BD"""
        db = SessionLocal()
        nuevo_impuesto = Impuesto(
            municipal=municipal,
            departamental=departamental,
            pro_deporte=pro_deporte
        )
        db.add(nuevo_impuesto)
        db.commit()
        db.refresh(nuevo_impuesto)
        db.close()
        return nuevo_impuesto
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los impuestos"""
        db = SessionLocal()
        impuestos = db.query(Impuesto).all()
        db.close()
        return impuestos
    
    @staticmethod
    def obtener_por_id(impuesto_id):
        """Obtiene un impuesto por ID"""
        db = SessionLocal()
        impuesto = db.query(Impuesto).filter(Impuesto.id == impuesto_id).first()
        db.close()
        return impuesto
    
    @staticmethod
    def eliminar(impuesto_id):
        """Elimina un impuesto por ID"""
        db = SessionLocal()
        impuesto = db.query(Impuesto).filter(Impuesto.id == impuesto_id).first()
        if impuesto:
            db.delete(impuesto)
            db.commit()
        db.close()


Maquinas = Impuesto
