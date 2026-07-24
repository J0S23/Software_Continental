from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine
from Modulos.enums import EstadoFactura


class Facturacion(Base):
    """Facturacion por cliente/contrato/periodo (seccion 9 del documento).

    Valor_facturado e Impuestos se fusionaron aqui: Valor_facturado era un
    campo suelto que duplicaba lo que ya cubre total_facturado, e Impuestos
    (municipal, departamental, pro_deporte) son insumos del calculo de la
    factura junto con el IVA (seccion 24.6), no un modulo aparte.
    """

    __tablename__ = "facturacion"

    id = Column(Integer, primary_key=True, index=True)

    # A que periodo/cliente/contrato corresponde la factura.
    periodo = Column(String)
    cliente_id = Column(Integer)
    contrato_id = Column(Integer)

    numero_factura = Column(String)
    fecha_factura = Column(DateTime)
    fecha_vencimiento = Column(DateTime, nullable=True)

    # Valor mensual base del contrato + adicionales por tipo de pagina +
    # otros cargos. subtotal se calcula automaticamente en agregar() si no
    # se envia explicito (suma de estos cinco valores).
    valor_mensual_base = Column(Float, default=0)
    valor_adicionales_bn = Column(Float, default=0)
    valor_adicionales_color = Column(Float, default=0)
    valor_adicionales_escaneo = Column(Float, default=0)
    otros_cargos = Column(Float, default=0)
    subtotal = Column(Float, default=0)

    # IVA (seccion 24.6): incluye_iva indica si subtotal ya trae el IVA
    # incluido o si hay que sumarlo aparte; valor_iva se calcula en
    # agregar() segun ese flag y porcentaje_iva.
    incluye_iva = Column(Boolean, default=False)
    porcentaje_iva = Column(Float, default=0)
    valor_iva = Column(Float, default=0)

    # Impuestos adicionales (antes Variables/Impuestos.py) que se restan o
    # suman al calcular total_facturado.
    impuesto_municipal = Column(Float, default=0)
    impuesto_departamental = Column(Float, default=0)
    impuesto_pro_deporte = Column(Float, default=0)

    retenciones = Column(Float, default=0)

    # Total final de la factura (reemplaza el antiguo Valor_facturado.facturado).
    total_facturado = Column(Float, default=0)

    estado_factura = Column(SQLEnum(EstadoFactura))
    fecha_envio = Column(DateTime, nullable=True)
    medio_envio = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def agregar(periodo,
        cliente_id,
        contrato_id,
        numero_factura,
        fecha_factura,
        estado_factura,
        fecha_vencimiento=None,
        valor_mensual_base=0,
        valor_adicionales_bn=0,
        valor_adicionales_color=0,
        valor_adicionales_escaneo=0,
        otros_cargos=0,
        subtotal=None,
        incluye_iva=False,
        porcentaje_iva=0,
        valor_iva=None,
        impuesto_municipal=0,
        impuesto_departamental=0,
        impuesto_pro_deporte=0,
        retenciones=0,
        total_facturado=None,
        fecha_envio=None,
        medio_envio=None,
        observaciones=None
        
    ):
        """Agrega una factura a la BD"""
        # subtotal automatico si no viene explicito.
        if subtotal is None:
            subtotal = (
                valor_mensual_base
                + valor_adicionales_bn
                + valor_adicionales_color
                + valor_adicionales_escaneo
                + otros_cargos
            )

        if valor_iva is None:
            if incluye_iva:
                # el subtotal ya trae el IVA incluido: se calcula el IVA
                # implicito solo para mostrarlo, no se vuelve a sumar.
                valor_iva = subtotal - (subtotal / (1 + porcentaje_iva / 100)) if porcentaje_iva else 0
            else:
                # el IVA no esta incluido: se suma aparte al total.
                valor_iva = subtotal * (porcentaje_iva / 100) if porcentaje_iva else 0

        if total_facturado is None:
            base_con_iva = subtotal if incluye_iva else subtotal + valor_iva
            total_facturado = (
                base_con_iva
                + impuesto_municipal
                + impuesto_departamental
                + impuesto_pro_deporte
                - retenciones
            )

        db = SessionLocal()
        nueva_factura = Facturacion(
            periodo=periodo,
            cliente_id=cliente_id,
            contrato_id=contrato_id,
            numero_factura=numero_factura,
            fecha_factura=fecha_factura,
            fecha_vencimiento=fecha_vencimiento,
            valor_mensual_base=valor_mensual_base,
            valor_adicionales_bn=valor_adicionales_bn,
            valor_adicionales_color=valor_adicionales_color,
            valor_adicionales_escaneo=valor_adicionales_escaneo,
            otros_cargos=otros_cargos,
            subtotal=subtotal,
            incluye_iva=incluye_iva,
            porcentaje_iva=porcentaje_iva,
            valor_iva=valor_iva,
            impuesto_municipal=impuesto_municipal,
            impuesto_departamental=impuesto_departamental,
            impuesto_pro_deporte=impuesto_pro_deporte,
            retenciones=retenciones,
            total_facturado=total_facturado,
            estado_factura=estado_factura,
            fecha_envio=fecha_envio,
            medio_envio=medio_envio,
            observaciones=observaciones,
        )
        db.add(nueva_factura)
        db.commit()
        db.refresh(nueva_factura)
        db.close()
        return nueva_factura

    @staticmethod
    def obtener_todos():
        """Obtiene todas las facturas"""
        db = SessionLocal()
        facturas = db.query(Facturacion).all()
        db.close()
        return facturas

    @staticmethod
    def obtener_por_id(factura_id):
        """Obtiene una factura por ID"""
        db = SessionLocal()
        factura = db.query(Facturacion).filter(Facturacion.id == factura_id).first()
        db.close()
        return factura

    @staticmethod
    def eliminar(factura_id):
        """Elimina una factura por ID"""
        db = SessionLocal()
        factura = db.query(Facturacion).filter(Facturacion.id == factura_id).first()
        if factura:
            db.delete(factura)
            db.commit()
        db.close()