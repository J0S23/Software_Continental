from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Insumo(Base):
    __tablename__ = "insumos"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_insumo = Column(String)
    color = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(tipo_insumo, color="", estado=""):
        """Agrega un insumo a la BD"""
        db = SessionLocal()
        nuevo_insumo = Insumo(tipo_insumo=tipo_insumo, color=color, estado=estado)
        db.add(nuevo_insumo)
        db.commit()
        db.refresh(nuevo_insumo)
        db.close()
        return nuevo_insumo
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los insumos"""
        db = SessionLocal()
        insumos = db.query(Insumo).all()
        db.close()
        return insumos
    
    @staticmethod
    def obtener_por_id(insumo_id):
        """Obtiene un insumo por ID"""
        db = SessionLocal()
        insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
        db.close()
        return insumo
    
    @staticmethod
    def eliminar(insumo_id):
        """Elimina un insumo por ID"""
        db = SessionLocal()
        insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
        if insumo:
            db.delete(insumo)
            db.commit()
        db.close()


Maquinas = Insumo
