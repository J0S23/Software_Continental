from sqlalchemy import Column, Integer, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class ValorFacturado(Base):
    __tablename__ = "valor_facturado"
    
    id = Column(Integer, primary_key=True, index=True)
    facturado = Column(Float)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(facturado):
        """Agrega un valor facturado a la BD"""
        db = SessionLocal()
        nuevo_valor = ValorFacturado(facturado=facturado)
        db.add(nuevo_valor)
        db.commit()
        db.refresh(nuevo_valor)
        db.close()
        return nuevo_valor
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los valores facturados"""
        db = SessionLocal()
        valores = db.query(ValorFacturado).all()
        db.close()
        return valores
    
    @staticmethod
    def obtener_por_id(valor_id):
        """Obtiene un valor facturado por ID"""
        db = SessionLocal()
        valor = db.query(ValorFacturado).filter(ValorFacturado.id == valor_id).first()
        db.close()
        return valor
    
    @staticmethod
    def eliminar(valor_id):
        """Elimina un valor facturado por ID"""
        db = SessionLocal()
        valor = db.query(ValorFacturado).filter(ValorFacturado.id == valor_id).first()
        if valor:
            db.delete(valor)
            db.commit()
        db.close()


Maquinas = ValorFacturado
