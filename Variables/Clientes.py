from sqlalchemy import Column, Integer, String, DateTime, Enum
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine
from .enums import TipoCliente, EstadoCliente


class Clientes(Base):
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    tipo_cliente = Column(Enum(TipoCliente))
    estado_cliente = Column(Enum(EstadoCliente))
    tipo_contacto = Column(String)
    condicion_pago = Column(String)
    estado_cartera_cliente = Column(String)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(tipo_cliente, estado_cliente, tipo_contacto, condicion_pago, estado_cartera_cliente):
        """Agrega un cliente a la BD"""
        db = SessionLocal()
        nuevo_cliente = Clientes(
            tipo_cliente=tipo_cliente,
            estado_cliente=estado_cliente,
            tipo_contacto=tipo_contacto,
            condicion_pago=condicion_pago,
            estado_cartera_cliente=estado_cartera_cliente
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

