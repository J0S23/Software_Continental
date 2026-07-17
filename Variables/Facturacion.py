from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Facturacion(Base):
    __tablename__ = "facturacion"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_factura = Column(String)
    cliente_id = Column(Integer)
    monto = Column(Float)
    estado_factura = Column(String)
    fecha_emision = Column(DateTime, default=datetime.utcnow)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(numero_factura, cliente_id, monto, estado_factura, fecha_emision=None):
        """Agrega una factura a la BD"""
        db = SessionLocal()
        nueva_factura = Facturacion(
            numero_factura=numero_factura,
            cliente_id=cliente_id,
            monto=monto,
            estado_factura=estado_factura,
            fecha_emision=fecha_emision or datetime.utcnow()
        )
        db.add(nueva_factura)
        db.commit()
        db.refresh(nueva_factura)
        db.close()
        return nueva_factura
    
    @staticmethod
    def obtener_todos():
        """Obtiene todas las facturas"""
        db = SessionLocal()
        facturas = db.query(Facturacion).all()
        db.close()
        return facturas
    
    @staticmethod
    def obtener_por_id(factura_id):
        """Obtiene una factura por ID"""
        db = SessionLocal()
        factura = db.query(Facturacion).filter(Facturacion.id == factura_id).first()
        db.close()
        return factura
    
    @staticmethod
    def eliminar(factura_id):
        """Elimina una factura por ID"""
        db = SessionLocal()
        factura = db.query(Facturacion).filter(Facturacion.id == factura_id).first()
        if factura:
            db.delete(factura)
            db.commit()
        db.close()
