from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Modelo(Base):
    __tablename__ = "modelos"
    
    id = Column(Integer, primary_key=True, index=True)
    modelo = Column(String)
    toner = Column(String)
    rend_orig = Column(Float)
    rend_gen = Column(Float)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(modelo, toner, rend_orig, rend_gen):
        """Agrega un modelo a la BD"""
        db = SessionLocal()
        nuevo_modelo = Modelo(
            modelo=modelo,
            toner=toner,
            rend_orig=rend_orig,
            rend_gen=rend_gen
        )
        db.add(nuevo_modelo)
        db.commit()
        db.refresh(nuevo_modelo)
        db.close()
        return nuevo_modelo
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los modelos"""
        db = SessionLocal()
        modelos = db.query(Modelo).all()
        db.close()
        return modelos
    
    @staticmethod
    def obtener_por_id(modelo_id):
        """Obtiene un modelo por ID"""
        db = SessionLocal()
        modelo = db.query(Modelo).filter(Modelo.id == modelo_id).first()
        db.close()
        return modelo
    
    @staticmethod
    def eliminar(modelo_id):
        """Elimina un modelo por ID"""
        db = SessionLocal()
        modelo = db.query(Modelo).filter(Modelo.id == modelo_id).first()
        if modelo:
            db.delete(modelo)
            db.commit()
        db.close()


Maquinas = Modelo
