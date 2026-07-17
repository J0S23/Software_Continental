from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Contratos(Base):
    __tablename__ = "contratos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_contrato = Column(String)
    cliente_id = Column(Integer)
    estado_contrato = Column(String)
    tipo_contrato = Column(String)
    forma_legalizacion = Column(String)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(numero_contrato, cliente_id, estado_contrato, tipo_contrato, forma_legalizacion, fecha_inicio, fecha_fin=None):
        """Agrega un contrato a la BD"""
        db = SessionLocal()
        nuevo_contrato = Contratos(
            numero_contrato=numero_contrato,
            cliente_id=cliente_id,
            estado_contrato=estado_contrato,
            tipo_contrato=tipo_contrato,
            forma_legalizacion=forma_legalizacion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        db.add(nuevo_contrato)
        db.commit()
        db.refresh(nuevo_contrato)
        db.close()
        return nuevo_contrato
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los contratos"""
        db = SessionLocal()
        contratos = db.query(Contratos).all()
        db.close()
        return contratos
    
    @staticmethod
    def obtener_por_id(contrato_id):
        """Obtiene un contrato por ID"""
        db = SessionLocal()
        contrato = db.query(Contratos).filter(Contratos.id == contrato_id).first()
        db.close()
        return contrato
    
    @staticmethod
    def eliminar(contrato_id):
        """Elimina un contrato por ID"""
        db = SessionLocal()
        contrato = db.query(Contratos).filter(Contratos.id == contrato_id).first()
        if contrato:
            db.delete(contrato)
            db.commit()
        db.close()
