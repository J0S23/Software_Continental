from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class Lecturas(Base):
    """Lectura de contadores (blanco/negro y color) de un equipo en un periodo,
    base para calcular paginas adicionales a facturar. Solo define columnas;
    acceso a datos en Persistencia/LecturasRepositorio.py."""

    __tablename__ = "lecturas"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer)
    contrato_id = Column(Integer, nullable=True)
    cliente_id = Column(Integer, nullable=True)
    periodo = Column(String, nullable=True)
    medio_lectura = Column(String)
    estado_lectura = Column(String)
    contador_bn = Column(Integer, default=0)
    contador_color = Column(Integer, default=0)
    fecha_lectura = Column(DateTime, default=datetime.utcnow)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)