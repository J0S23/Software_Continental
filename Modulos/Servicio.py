from Modulos.enums import TipoMantenimiento
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Servicio(Base):
    __tablename__ = "servicios"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer)
    equipo_id = Column(Integer, nullable=True)
    nombre_servicio = Column(String)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, default=0)
    mantenimiento = Column(SQLEnum(TipoMantenimiento), default=TipoMantenimiento.CORRECTIVO, nullable=False)
    descripcion_mantenimiento = Column(String, nullable=True)
    repuestos_incluidos = Column(String, default="No")
    toner_incluido = Column(String, default="No")
    toner_respaldo_sitio = Column(String, default="No")
    equipo_respaldo_incluido = Column(String, default="No")
    estado = Column(String, default="Activo")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(cliente_id, equipo_id, nombre_servicio, descripcion="", precio=0,
                descripcion_mantenimiento="", repuestos_incluidos="No", toner_incluido="No",
                toner_respaldo_sitio="No", equipo_respaldo_incluido="No", estado="Activo"):
        """Agrega un servicio a la BD"""
        db = SessionLocal()
        nuevo_servicio = Servicio(
            cliente_id=cliente_id,
            equipo_id=equipo_id,
            nombre_servicio=nombre_servicio,
            descripcion=descripcion,
            precio=precio,
            descripcion_mantenimiento=descripcion_mantenimiento,
            repuestos_incluidos=repuestos_incluidos,
            toner_incluido=toner_incluido,
            toner_respaldo_sitio=toner_respaldo_sitio,
            equipo_respaldo_incluido=equipo_respaldo_incluido,
            estado=estado
        )
        db.add(nuevo_servicio)
        db.commit()
        db.refresh(nuevo_servicio)
        db.close()
        return nuevo_servicio
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los servicios"""
        db = SessionLocal()
        servicios = db.query(Servicio).all()
        db.close()
        return servicios
    
    @staticmethod
    def obtener_por_id(servicio_id):
        """Obtiene un servicio por ID"""
        db = SessionLocal()
        servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
        db.close()
        return servicio
    
    @staticmethod
    def eliminar(servicio_id):
        """Elimina un servicio por ID"""
        db = SessionLocal()
        servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
        if servicio:
            db.delete(servicio)
            db.commit()
        db.close()
