from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine
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

    @staticmethod
    def agregar(
        tipo_cliente, estado_cliente, condicion_pago, estado_cartera_cliente,
        nombre, cliente_id, telefono=None, celular=None, nit=None, ciudad=None,
        departamento=None, direccion_principal=None, correo=None,
        vendedor_comercial=None, multiempresa=None,
    ):
        """Agrega un cliente a la BD"""
        db = SessionLocal()
        nuevo_cliente = Clientes(
            tipo_cliente=tipo_cliente,
            estado_cliente=estado_cliente,
            condicion_pago=condicion_pago,
            estado_cartera_cliente=estado_cartera_cliente,
            multiempresa=multiempresa,
            nombre=nombre,
            cliente_id=cliente_id,
            telefono=telefono,
            celular=celular,
            nit=nit,
            ciudad=ciudad,
            departamento=departamento,
            direccion_principal=direccion_principal,
            correo=correo,
            vendedor_comercial=vendedor_comercial,
        )
        db.add(nuevo_cliente)
        db.commit()
        db.refresh(nuevo_cliente)
        db.close()
        return nuevo_cliente
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los clientes"""
        db = SessionLocal()
        clientes = db.query(Clientes).all()
        db.close()
        return clientes
    
    @staticmethod
    def obtener_por_id(cliente_id):
        """Obtiene un cliente por ID"""
        db = SessionLocal()
        cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()
        db.close()
        return cliente

    @staticmethod
    def actualizar(cliente_id, **valores):
        """Actualiza un cliente por ID"""
        db = SessionLocal()
        cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()

        if not cliente:
            db.close()
            return None

        for campo, valor in valores.items():
            setattr(cliente, campo, valor)

        db.commit()
        db.refresh(cliente)
        db.close()
        return cliente
    
    @staticmethod
    def eliminar(cliente_id):
        """Elimina un cliente por ID"""
        db = SessionLocal()
        cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()
        if cliente:
            db.delete(cliente)
            db.commit()
        db.close()

