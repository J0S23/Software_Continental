from Modulos.enums import TipoMantenimiento
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, engine


class Contratos(Base):
    """Contrato comercial con un cliente (condiciones, valores base y paginas incluidas).
    Solo define columnas; acceso a datos en Persistencia/ContratosRepositorio.py."""

    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, index=True)
    numero_contrato = Column(String)
    cliente_id = Column(Integer)
    estado_contrato = Column(String)
    tipo_contrato = Column(String)
    forma_legalizacion = Column(String)
    poliza_contrato = Column(String, nullable=True)
    poliza_seriedad = Column(String, nullable=True)
    # Un solo id por equipo: no se pueden tener multiequipos en el contrato
    # todavia (pendiente: tabla intermediaria contrato_equipos).
    equipo_id = Column(Integer, nullable=True)
    mantenimiento = Column(SQLEnum(TipoMantenimiento), default=TipoMantenimiento.PREVENTIVO, nullable=False)
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    valor_mensual_base = Column(Float, default=0)
    paginas_bn_incluidas = Column(Integer, default=0)
    paginas_color_incluidas = Column(Integer, default=0)
    valor_pagina_adicional_bn = Column(Float, default=0)
    valor_pagina_adicional_color = Column(Float, default=0)
    escaneos_incluidos = Column(Integer, nullable=True, default=0)
    valor_escaneo_adicional = Column(Float, nullable=True, default=0)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)