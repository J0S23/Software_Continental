from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class MantenimientoPreventivo(Base):
    __tablename__ = "mantenimiento_preventivo"
    
    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer)
    tipo_mantenimiento = Column(String)
    estado = Column(String)
    descripcion = Column(String, nullable=True)
    fecha_programada = Column(DateTime)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(equipo_id, tipo_mantenimiento, estado, fecha_programada, descripcion=""):
        """Agrega un mantenimiento preventivo a la BD"""
        db = SessionLocal()
        nuevo_mantenimiento = MantenimientoPreventivo(
            equipo_id=equipo_id,
            tipo_mantenimiento=tipo_mantenimiento,
            estado=estado,
            fecha_programada=fecha_programada,
            descripcion=descripcion
        )
        db.add(nuevo_mantenimiento)
        db.commit()
        db.refresh(nuevo_mantenimiento)
        db.close()
        return nuevo_mantenimiento
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los mantenimientos preventivos"""
        db = SessionLocal()
        mantenimientos = db.query(MantenimientoPreventivo).all()
        db.close()
        return mantenimientos
    
    @staticmethod
    def obtener_por_id(mantenimiento_id):
        """Obtiene un mantenimiento preventivo por ID"""
        db = SessionLocal()
        mantenimiento = db.query(MantenimientoPreventivo).filter(MantenimientoPreventivo.id == mantenimiento_id).first()
        db.close()
        return mantenimiento
    
    @staticmethod
    def eliminar(mantenimiento_id):
        """Elimina un mantenimiento preventivo por ID"""
        db = SessionLocal()
        mantenimiento = db.query(MantenimientoPreventivo).filter(MantenimientoPreventivo.id == mantenimiento_id).first()
        if mantenimiento:
            db.delete(mantenimiento)
            db.commit()
        db.close()

