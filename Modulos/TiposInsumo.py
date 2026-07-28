from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class TipoInsumo(Base):
    """Solo define columnas. Acceso a datos en Repositorios/TiposInsumoRepositorio.py.

    Insumo.tipo_insumo_id guarda el id de aqui (sin ForeignKey, igual que
    en el resto del proyecto) para relacionar cada insumo con su precio
    sin acoplar los modulos.
    """

    __tablename__ = "tipos_insumo"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    precio = Column(Float, default=0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)