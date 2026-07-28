from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class EntregaToner(Base):
    
    __tablename__ = "entregas_toner"

    id = Column(Integer, primary_key=True, index=True)
    fecha_entrega = Column(DateTime, default=datetime.utcnow)
    periodo = Column(String)
    cliente_id = Column(Integer)
    contrato_id = Column(Integer, nullable=True)
    equipo_id = Column(Integer)
    tipo_insumo_id = Column(Integer)
    cantidad = Column(Float, default=1)
    costo_unitario = Column(Float, default=0)
    costo_total = Column(Float, default=0)
    persona_entrega = Column(String)
    persona_recibe = Column(String, nullable=True)
    motivo = Column(String, nullable=True)
    contador_bn = Column(Integer, nullable=True)
    contador_color = Column(Integer, nullable=True)
    observaciones = Column(String, nullable=True)
    evidencia_recibido = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        # Se deja por consistencia con el resto de Modulos/*.py, aunque crear_tablas() en base_de_datos.py
        # ya crea todas las tablas registradas en Base.metadata (esta incluida por herencia).
        Base.metadata.create_all(bind=engine)