from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class Historial(Base):
    """Registro transversal de auditoria para crear/actualizar/eliminar sobre
    cualquier tipo_entidad del catalogo (clientes, contratos, etc).
    Solo define columnas; acceso a datos en Persistencia/HistorialRepositorio.py."""

    __tablename__ = "historial"

    id = Column(Integer, primary_key=True, index=True)
    tipo_entidad = Column(String)
    entidad_id = Column(Integer)
    accion = Column(String)
    campo = Column(String, nullable=True)
    valor_anterior = Column(String, nullable=True)
    valor_nuevo = Column(String, nullable=True)
    usuario_id = Column(Integer)
    fecha = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
