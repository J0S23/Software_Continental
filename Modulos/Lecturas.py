from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Lecturas(Base):
    __tablename__ = "lecturas"
    
    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer)
    medio_lectura = Column(String)
    estado_lectura = Column(String)
    contador = Column(Integer, default=0)
    fecha_lectura = Column(DateTime, default=datetime.utcnow)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(equipo_id, medio_lectura, estado_lectura, contador=0, fecha_lectura=None):
        """Agrega una lectura a la BD"""
        db = SessionLocal()
        nueva_lectura = Lecturas(
            equipo_id=equipo_id,
            medio_lectura=medio_lectura,
            estado_lectura=estado_lectura,
            contador=contador,
            fecha_lectura=fecha_lectura or datetime.utcnow()
        )
        db.add(nueva_lectura)
        db.commit()
        db.refresh(nueva_lectura)
        db.close()
        return nueva_lectura
    
    @staticmethod
    def obtener_todos():
        """Obtiene todas las lecturas"""
        db = SessionLocal()
        lecturas = db.query(Lecturas).all()
        db.close()
        return lecturas
    
    @staticmethod
    def obtener_por_id(lectura_id):
        """Obtiene una lectura por ID"""
        db = SessionLocal()
        lectura = db.query(Lecturas).filter(Lecturas.id == lectura_id).first()
        db.close()
        return lectura
    
    @staticmethod
    def eliminar(lectura_id):
        """Elimina una lectura por ID"""
        db = SessionLocal()
        lectura = db.query(Lecturas).filter(Lecturas.id == lectura_id).first()
        if lectura:
            db.delete(lectura)
            db.commit()
        db.close()
