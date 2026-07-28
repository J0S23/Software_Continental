from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, engine
from Modulos.enums import TipoCosto
from Persistencia.RepuestosRepositorio import RepuestosRepositorio


class Costos(Base):
    
    __tablename__ = "costos"

    id = Column(Integer, primary_key=True, index=True)
    fecha_costo = Column(DateTime)
    periodo = Column(String)
    cliente_id = Column(Integer)
    contrato_id = Column(Integer)
    equipo_id = Column(Integer)
    tipo_costo = Column(SQLEnum(TipoCosto))
    descripcion = Column(String)
    repuesto_id = Column(Integer, nullable=True)
    cantidad = Column(Float, default=1)
    valor_unitario = Column(Float, default=0)
    valor_total = Column(Float, default=0)
    responsable = Column(String)
    soporte = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @property
    def repuesto(self):
        """Repuesto relacionado (con su nombre y precio), si aplica."""
        if self.repuesto_id is None:
            return None
        return RepuestosRepositorio.obtener_por_id(self.repuesto_id)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)