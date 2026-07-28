from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class Sedes(Base):
    """Solo define columnas. Acceso a datos en Repositorios/SedesRepositorio.py."""

    __tablename__ = "sedes"

    id = Column(Integer, primary_key=True, index=True)
    nombre_sede = Column(String)
    ciudad = Column(String)
    direccion = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    gerente = Column(String, nullable=True)
    estado_sede = Column(String, default="Activa")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)