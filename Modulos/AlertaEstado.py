from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint
from datetime import datetime
from base_de_datos import Base, engine


class AlertaEstado(Base):

    #Las alertas en si no tienen tabla propia (Servicio/Alertas.py las calcula al vuelo). Esta tabla solo guarda,
    # por alerta (tipo + referencia_id), que accion tomo el usuario sobre ella, mas un snapshot de mensaje/nivel para
    #que una alerta "guardada" se pueda seguir mostrando aunque la condicion que la genero ya no se cumpla.

    __tablename__ = "alertas_estado"
    __table_args__ = (UniqueConstraint("tipo", "referencia_id", name="uq_alerta_tipo_referencia"),)

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)
    referencia_id = Column(Integer, nullable=True)
    mensaje = Column(String, nullable=True)
    nivel = Column(String, nullable=True)
    leida = Column(Boolean, default=False, nullable=False)
    guardada = Column(Boolean, default=False, nullable=False)
    descartada = Column(Boolean, default=False, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)