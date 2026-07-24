from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Servicio(Base):
    __tablename__ = "servicios"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_servicio = Column(String)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, default=0)
    mantenimiento_preventivo_incluido = Column(String, default="No")
    mantenimiento_correctivo_incluido = Column(String, default="No")
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
    def agregar(nombre_servicio, descripcion="", precio=0, mantenimiento_preventivo_incluido="No",
                mantenimiento_correctivo_incluido="No", repuestos_incluidos="No", toner_incluido="No",
                toner_respaldo_sitio="No", equipo_respaldo_incluido="No", estado="Activo"):
        """Agrega un servicio a la BD"""
        db = SessionLocal()
        nuevo_servicio = Servicio(
            nombre_servicio=nombre_servicio,
            descripcion=descripcion,
            precio=precio,
            mantenimiento_preventivo_incluido=mantenimiento_preventivo_incluido,
            mantenimiento_correctivo_incluido=mantenimiento_correctivo_incluido,
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
