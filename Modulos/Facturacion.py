from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, engine
from Modulos.enums import EstadoFactura
from .enums import EmpresaFacturadora


class Facturacion(Base):
    """Factura emitida a un cliente por un periodo/contrato, con el desglose de
    valores base, adicionales, impuestos y total. Solo define columnas; acceso
    a datos en Persistencia/FacturacionRepositorio.py."""

    __tablename__ = "facturacion"

    id = Column(Integer, primary_key=True, index=True)
    periodo = Column(String)
    cliente_id = Column(Integer)
    contrato_id = Column(Integer)
    empresa_factura = Column(SQLEnum(EmpresaFacturadora))
    multiempresa = Column(SQLEnum(EmpresaFacturadora), nullable=True)
    es_multiempresa = Column(Boolean, default=False)
    numero_factura = Column(String)
    fecha_factura = Column(DateTime)
    fecha_vencimiento = Column(DateTime, nullable=True)
    valor_mensual_base = Column(Float, default=0)
    valor_adicionales_bn = Column(Float, default=0)
    valor_adicionales_color = Column(Float, default=0)
    valor_adicionales_escaneo = Column(Float, default=0)
    otros_cargos = Column(Float, default=0)
    subtotal = Column(Float, default=0)
    incluye_iva = Column(Boolean, default=False)
    porcentaje_iva = Column(Float, default=0)
    valor_iva = Column(Float, default=0)
    impuesto_municipal = Column(Float, default=0)
    impuesto_departamental = Column(Float, default=0)
    impuesto_pro_deporte = Column(Float, default=0)
    retenciones = Column(Float, default=0)
    total_facturado = Column(Float, default=0)
    estado_factura = Column(SQLEnum(EstadoFactura))
    fecha_envio = Column(DateTime, nullable=True)
    medio_envio = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)