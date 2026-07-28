from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from base_de_datos import Base, engine
from .enums import TipoCliente, EstadoCliente, EmpresaFacturadora


class Clientes(Base):

    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    tipo_cliente = Column(Enum(TipoCliente))
    estado_cliente = Column(Enum(EstadoCliente))
    condicion_pago = Column(String)
    estado_cartera_cliente = Column(String)
    multiempresa = Column(Enum(EmpresaFacturadora), nullable=True)
    nombre = Column(String)
    cliente_id = Column(String)
    telefono = Column(String, nullable=True)
    celular = Column(String, nullable=True)
    nit = Column(String, nullable=True)
    ciudad = Column(String, nullable=True)
    departamento = Column(String, nullable=True)
    direccion_principal = Column(String, nullable=True)
    correo = Column(String, nullable=True)
    vendedor_comercial = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)