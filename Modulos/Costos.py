from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine
from Modulos.enums import TipoCosto


class Costos(Base):
    """Costos por cliente/contrato/equipo/periodo (seccion 11 del documento).

    Transporte (desplazamientos) y Mano_obra se fusionaron aqui como
    valores de TipoCosto en vez de modulos propios: el documento los pide
    como *tipos de costo*, no como flota vehicular ni nomina de personal.
    """

    __tablename__ = "costos"

    id = Column(Integer, primary_key=True, index=True)

    # Cuándo y a qué periodo de facturación corresponde el costo.
    fecha_costo = Column(DateTime)
    periodo = Column(String)

    # A qué cliente/contrato/equipo se le imputa el costo (sin ForeignKey,
    # igual que en el resto del proyecto, para no acoplar los modulos).
    cliente_id = Column(Integer)
    contrato_id = Column(Integer)
    equipo_id = Column(Integer)

    # Que tipo de costo es (toner, repuesto, mano_obra, desplazamiento,
    # flete, mantenimiento preventivo/correctivo, equipo de respaldo,
    # reparacion mayor, accesorio, depreciacion, otro).
    tipo_costo = Column(SQLEnum(TipoCosto))
    descripcion = Column(String)

    # cantidad x valor_unitario = valor_total (ver agregar()).
    cantidad = Column(Float, default=1)
    valor_unitario = Column(Float, default=0)
    valor_total = Column(Float, default=0)

    responsable = Column(String)
    soporte = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)

    # Marca de tiempo de creacion del registro, distinta de fecha_costo.
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    # Costos automaticos sugeridos (seccion 11.3): valores estandar de
    # referencia para agilizar el registro de un costo nuevo. Hoy son
    # placeholders en 0; se ajustan cuando se definan los valores reales.
    COSTOS_SUGERIDOS = {
        "visita_tecnica": 0,
        "desplazamiento_local": 0,
        "desplazamiento_fuera_ciudad": 0,
        "depreciacion_mensual_equipo": 0,
        "costo_por_pagina": 0,
        "toner_por_referencia": 0,
    }

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def obtener_costos_sugeridos():
        """Valores estandar de referencia para agilizar el registro de un costo"""
        return Costos.COSTOS_SUGERIDOS

    @staticmethod
    def agregar(
        fecha_costo,
        periodo,
        cliente_id,
        contrato_id,
        equipo_id,
        tipo_costo,
        descripcion,
        responsable,
        cantidad=1,
        valor_unitario=0,
        valor_total=None,
        soporte=None,
        observaciones=None,
    ):
        """Agrega un costo a la BD"""
        # Si no viene valor_total explicito, se calcula automaticamente.
        if valor_total is None:
            valor_total = cantidad * valor_unitario

        db = SessionLocal()
        nuevo_costo = Costos(
            fecha_costo=fecha_costo,
            periodo=periodo,
            cliente_id=cliente_id,
            contrato_id=contrato_id,
            equipo_id=equipo_id,
            tipo_costo=tipo_costo,
            descripcion=descripcion,
            cantidad=cantidad,
            valor_unitario=valor_unitario,
            valor_total=valor_total,
            responsable=responsable,
            soporte=soporte,
            observaciones=observaciones,
        )
        db.add(nuevo_costo)
        db.commit()
        db.refresh(nuevo_costo)
        db.close()
        return nuevo_costo

    @staticmethod
    def obtener_todos():
        """Obtiene todos los costos"""
        db = SessionLocal()
        costos = db.query(Costos).all()
        db.close()
        return costos

    @staticmethod
    def obtener_por_id(costo_id):
        """Obtiene un costo por ID"""
        db = SessionLocal()
        costo = db.query(Costos).filter(Costos.id == costo_id).first()
        db.close()
        return costo

    @staticmethod
    def eliminar(costo_id):
        """Elimina un costo por ID"""
        db = SessionLocal()
        costo = db.query(Costos).filter(Costos.id == costo_id).first()
        if costo:
            db.delete(costo)
            db.commit()
        db.close()
