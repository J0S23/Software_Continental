from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class Cartera(Base):
    """Registro de cartera (cuentas por cobrar) de un cliente. Solo define columnas;
    acceso a datos en Persistencia/CarteraRepositorio.py."""

    __tablename__ = "cartera"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer)
    monto = Column(Float)
    estado = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)