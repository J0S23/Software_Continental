from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class Rentabilidad(Base):

    __tablename__ = "rentabilidad"

    id = Column(Integer, primary_key=True, index=True)
    periodo = Column(String)
    contrato_id = Column(Integer, nullable=True)
    cliente_id = Column(Integer, nullable=True)
    ingresos = Column(Float, default=0)
    costos = Column(Float, default=0)
    ganancia = Column(Float, default=0)
    porcentaje_rentabilidad = Column(Float, default=0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)