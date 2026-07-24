from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine

class CambioRetiro(Base):
    __tablename__ = "cambios_retiros"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer)
    tipo_evento = Column(String)
    equipo_reemplazo_id = Column(Integer, nullable=True)
    motivo = Column(String)
    responsable = Column(String)
    fecha_evento = Column(DateTime, default=datetime.utcnow)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)