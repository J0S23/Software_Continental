from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Transporte(Base):
    __tablename__ = "transporte"
    
    id = Column(Integer, primary_key=True, index=True)
    placa_vehiculo = Column(String)
    tipo_vehiculo = Column(String)
    capacidad = Column(Integer, default=0)
    conductor = Column(String, nullable=True)
    costo = Column(Float, default=0)
    estado = Column(String, default="Disponible")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(placa_vehiculo, tipo_vehiculo, capacidad=0, conductor="", costo=0, estado="Disponible"):
        """Agrega un vehículo de transporte a la BD"""
        db = SessionLocal()
        nuevo_transporte = Transporte(
            placa_vehiculo=placa_vehiculo,
            tipo_vehiculo=tipo_vehiculo,
            capacidad=capacidad,
            conductor=conductor,
            costo=costo,
            estado=estado
        )
        db.add(nuevo_transporte)
        db.commit()
        db.refresh(nuevo_transporte)
        db.close()
        return nuevo_transporte
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los vehículos de transporte"""
        db = SessionLocal()
        transportes = db.query(Transporte).all()
        db.close()
        return transportes
    
    @staticmethod
    def obtener_por_id(transporte_id):
        """Obtiene un vehículo de transporte por ID"""
        db = SessionLocal()
        transporte = db.query(Transporte).filter(Transporte.id == transporte_id).first()
        db.close()
        return transporte
    
    @staticmethod
    def eliminar(transporte_id):
        """Elimina un vehículo de transporte por ID"""
        db = SessionLocal()
        transporte = db.query(Transporte).filter(Transporte.id == transporte_id).first()
        if transporte:
            db.delete(transporte)
            db.commit()
        db.close()
            
