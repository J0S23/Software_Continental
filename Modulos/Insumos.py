from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, engine
from Persistencia.TiposInsumoRepositorio import TiposInsumoRepositorio


class Insumo(Base):
    """Solo define columnas. Acceso a datos en Repositorios/InsumosRepositorio.py."""

    __tablename__ = "insumos"

    id = Column(Integer, primary_key=True, index=True)
    tipo_insumo_id = Column(Integer)
    color = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @property
    def tipo(self):
        """Tipo de insumo relacionado (con su nombre y precio)."""
        if self.tipo_insumo_id is None:
            return None
        return TiposInsumoRepositorio.obtener_por_id(self.tipo_insumo_id)

    @property
    def precio(self):
        """Precio relacionado directamente segun el tipo de insumo."""
        tipo = self.tipo
        return tipo.precio if tipo else None

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)