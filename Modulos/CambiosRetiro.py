from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class CambioRetiro(Base):
    """Historial de cambios de equipo o retiros definitivos (tipo_evento: 'cambio' | 'retiro').
    Solo define columnas; acceso a datos en Persistencia/CambiosRetiroRepositorio.py."""

    __tablename__ = "cambios_retiros"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer)
    tipo_evento = Column(String)
    equipo_reemplazo_id = Column(Integer, nullable=True)
    cliente_id = Column(Integer, nullable=True)
    contrato_id = Column(Integer, nullable=True)
    contador_final = Column(Integer, nullable=True)
    motivo = Column(String)
    tecnico_responsable = Column(String)
    persona_recibe = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)
    fecha_evento = Column(DateTime, default=datetime.utcnow)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)