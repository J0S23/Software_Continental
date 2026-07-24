from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Repuesto(Base):
    __tablename__ = "repuestos"
    
    id = Column(Integer, primary_key=True, index=True)
    cuchilla_limpieza = Column(String)
    cuchilla_transferencia = Column(String)
    banda_fusora = Column(String)
    rodillo_fusor = Column(String)
    sleeven_fusor = Column(String)
    telilla = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(cuchilla_limpieza, cuchilla_transferencia, banda_fusora, rodillo_fusor, sleeven_fusor, telilla):
        """Agrega un repuesto a la BD"""
        db = SessionLocal()
        nuevo_repuesto = Repuesto(
            cuchilla_limpieza=cuchilla_limpieza,
            cuchilla_transferencia=cuchilla_transferencia,
            banda_fusora=banda_fusora,
            rodillo_fusor=rodillo_fusor,
            sleeven_fusor=sleeven_fusor,
            telilla=telilla
        )
        db.add(nuevo_repuesto)
        db.commit()
        db.refresh(nuevo_repuesto)
        db.close()
        return nuevo_repuesto
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los repuestos"""
        db = SessionLocal()
        repuestos = db.query(Repuesto).all()
        db.close()
        return repuestos
    
    @staticmethod
    def obtener_por_id(repuesto_id):
        """Obtiene un repuesto por ID"""
        db = SessionLocal()
        repuesto = db.query(Repuesto).filter(Repuesto.id == repuesto_id).first()
        db.close()
        return repuesto
    
    @staticmethod
    def eliminar(repuesto_id):
        """Elimina un repuesto por ID"""
        db = SessionLocal()
        repuesto = db.query(Repuesto).filter(Repuesto.id == repuesto_id).first()
        if repuesto:
            db.delete(repuesto)
            db.commit()
        db.close()


Maquinas = Repuesto
