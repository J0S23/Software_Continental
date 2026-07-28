from Modulos.enums import TipoMantenimiento
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, engine


class Servicio(Base):
    """Solo define columnas. Acceso a datos en Persistencia/ServicioRepositorio.py."""

    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer)
    equipo_id = Column(Integer, nullable=True)
    nombre_servicio = Column(String)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, default=0)
    mantenimiento = Column(SQLEnum(TipoMantenimiento), default=TipoMantenimiento.CORRECTIVO, nullable=False)
    descripcion_mantenimiento = Column(String, nullable=True)
    repuestos_incluidos = Column(String, default="No")
    toner_incluido = Column(String, default="No")
    toner_respaldo_sitio = Column(String, default="No")
    equipo_respaldo_incluido = Column(String, default="No")
    estado = Column(String, default="Activo")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)