from Modulos.enums import TipoMantenimiento
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Contratos(Base):
    __tablename__ = "contratos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_contrato = Column(String)
    cliente_id = Column(Integer)
    estado_contrato = Column(String)
    tipo_contrato = Column(String)
    forma_legalizacion = Column(String)
    poliza_contrato = Column(String, nullable=True)
    poliza_seriedad = Column(String, nullable=True)
    #Al ser un solo id por equipo por lo que no se puede tener multiequipos en el contrato
    #En un futuro se añadira una tabla intermediaria contratos y equipos
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
    #Los escaneos se dejan opcionales
    escaneos_incluidos = Column(Integer, nullable=True, default=0)
    valor_escaneo_adicional = Column(Float, nullable=True, default=0)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(numero_contrato, cliente_id, estado_contrato, tipo_contrato, forma_legalizacion,
        fecha_inicio, fecha_fin=None, poliza_contrato="", poliza_seriedad="", equipo_id=None,
        valor_mensual_base=0, paginas_bn_incluidas=0, paginas_color_incluidas=0,
        valor_pagina_adicional_bn=0, valor_pagina_adicional_color=0,
        escaneos_incluidos=0, valor_escaneo_adicional=0,):
        """Agrega un contrato a la BD"""
        db = SessionLocal()
        nuevo_contrato = Contratos(
            numero_contrato=numero_contrato,
            cliente_id=cliente_id,
            estado_contrato=estado_contrato,
            tipo_contrato=tipo_contrato,
            forma_legalizacion=forma_legalizacion,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            poliza_contrato=poliza_contrato,
            poliza_seriedad=poliza_seriedad,
            equipo_id=equipo_id,
            valor_mensual_base=valor_mensual_base,
            paginas_bn_incluidas=paginas_bn_incluidas,
            paginas_color_incluidas=paginas_color_incluidas,
            valor_pagina_adicional_bn=valor_pagina_adicional_bn,
            valor_pagina_adicional_color=valor_pagina_adicional_color,
            escaneos_incluidos=escaneos_incluidos,
            valor_escaneo_adicional=valor_escaneo_adicional,
        )
        db.add(nuevo_contrato)
        db.commit()
        db.refresh(nuevo_contrato)
        db.close()
        return nuevo_contrato
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los contratos"""
        db = SessionLocal()
        contratos = db.query(Contratos).all()
        db.close()
        return contratos
    
    @staticmethod
    def obtener_por_id(contrato_id):
        """Obtiene un contrato por ID"""
        db = SessionLocal()
        contrato = db.query(Contratos).filter(Contratos.id == contrato_id).first()
        db.close()
        return contrato
    
    @staticmethod
    def eliminar(contrato_id):
        """Elimina un contrato por ID"""
        db = SessionLocal()
        contrato = db.query(Contratos).filter(Contratos.id == contrato_id).first()
        if contrato:
            db.delete(contrato)
            db.commit()
        db.close()
