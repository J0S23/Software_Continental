from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Sedes(Base):
    __tablename__ = "sedes"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_sede = Column(String)
    ciudad = Column(String)
    direccion = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    gerente = Column(String, nullable=True)
    estado_sede = Column(String, default="Activa")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(nombre_sede, ciudad, direccion="", telefono="", gerente="", estado_sede="Activa"):
        """Agrega una sede a la BD"""
        db = SessionLocal()
        nueva_sede = Sedes(
            nombre_sede=nombre_sede,
            ciudad=ciudad,
            direccion=direccion,
            telefono=telefono,
            gerente=gerente,
            estado_sede=estado_sede
        )
        db.add(nueva_sede)
        db.commit()
        db.refresh(nueva_sede)
        db.close()
        return nueva_sede
    
    @staticmethod
    def obtener_todos():
        """Obtiene todas las sedes"""
        db = SessionLocal()
        sedes = db.query(Sedes).all()
        db.close()
        return sedes
    
    @staticmethod
    def obtener_por_id(sede_id):
        """Obtiene una sede por ID"""
        db = SessionLocal()
        sede = db.query(Sedes).filter(Sedes.id == sede_id).first()
        db.close()
        return sede
    
    @staticmethod
    def eliminar(sede_id):
        """Elimina una sede por ID"""
        db = SessionLocal()
        sede = db.query(Sedes).filter(Sedes.id == sede_id).first()
        if sede:
            db.delete(sede)
            db.commit()
        db.close()
