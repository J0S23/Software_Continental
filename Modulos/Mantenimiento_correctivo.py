from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class MantenimientoCorrectivo(Base):
    __tablename__ = "mantenimiento_correctivo"
    
    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer)
    prioridad = Column(String)
    requiere_equipo_respaldo = Column(String)
    estado_caso = Column(String)
    descripcion = Column(String, nullable=True)
    fecha_mantenimiento = Column(DateTime, default=datetime.utcnow)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(equipo_id, prioridad, requiere_equipo_respaldo, estado_caso, descripcion="", fecha_mantenimiento=None):
        """Agrega un mantenimiento correctivo a la BD"""
        db = SessionLocal()
        nuevo_mantenimiento = MantenimientoCorrectivo(
            equipo_id=equipo_id,
            prioridad=prioridad,
            requiere_equipo_respaldo=requiere_equipo_respaldo,
            estado_caso=estado_caso,
            descripcion=descripcion,
            fecha_mantenimiento=fecha_mantenimiento or datetime.utcnow()
        )
        db.add(nuevo_mantenimiento)
        db.commit()
        db.refresh(nuevo_mantenimiento)
        db.close()
        return nuevo_mantenimiento
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los mantenimientos correctivos"""
        db = SessionLocal()
        mantenimientos = db.query(MantenimientoCorrectivo).all()
        db.close()
        return mantenimientos
    
    @staticmethod
    def obtener_por_id(mantenimiento_id):
        """Obtiene un mantenimiento correctivo por ID"""
        db = SessionLocal()
        mantenimiento = db.query(MantenimientoCorrectivo).filter(MantenimientoCorrectivo.id == mantenimiento_id).first()
        db.close()
        return mantenimiento
    
    @staticmethod
    def eliminar(mantenimiento_id):
        """Elimina un mantenimiento correctivo por ID"""
        db = SessionLocal()
        mantenimiento = db.query(MantenimientoCorrectivo).filter(MantenimientoCorrectivo.id == mantenimiento_id).first()
        if mantenimiento:
            db.delete(mantenimiento)
            db.commit()
        db.close()
