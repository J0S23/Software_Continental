from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class Equipos(Base):

    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True)
    numero_serie = Column(String)
    tipo_equipo = Column(String)
    tecnologia = Column(String)
    color = Column(String)
    estado_equipo = Column(String)
    estado_tecnico = Column(String)
    recomendacion_tecnica = Column(String, nullable=True)
    modelo = Column(String, nullable=True)
    toner = Column(String, nullable=True)
    rend_orig = Column(Float, nullable=True)
    rend_gen = Column(Float, nullable=True)
    contador_inicial_bn = Column(Integer, default=0)
    contador_inicial_color = Column(Integer, default=0)
    cliente_id = Column(Integer, nullable=True)
    contrato_id = Column(Integer, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)