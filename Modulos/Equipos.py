from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Equipos(Base):
    __tablename__ = "equipos"
    
    id = Column(Integer, primary_key=True, index=True)
    numero_serie = Column(String)
    tipo_equipo = Column(String)
    tecnologia = Column(String)
    color = Column(String)
    estado_equipo = Column(String)
    estado_tecnico = Column(String)
    recomendacion_tecnica = Column(String, nullable=True)
    modelo = Column(String, nullable=True)
    toner = Column(String, nullable=True)
    rend_orig = Column(Float, nullable=True)
    rend_gen = Column(Float, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(numero_serie, tipo_equipo, tecnologia, color, estado_equipo, estado_tecnico,
                recomendacion_tecnica="", modelo="", toner="", rend_orig=None, rend_gen=None):
        """Agrega un equipo a la BD"""
        db = SessionLocal()
        nuevo_equipo = Equipos(
            numero_serie=numero_serie,
            tipo_equipo=tipo_equipo,
            tecnologia=tecnologia,
            color=color,
            estado_equipo=estado_equipo,
            estado_tecnico=estado_tecnico,
            recomendacion_tecnica=recomendacion_tecnica,
            modelo=modelo,
            toner=toner,
            rend_orig=rend_orig,
            rend_gen=rend_gen,
        )
        db.add(nuevo_equipo)
        db.commit()
        db.refresh(nuevo_equipo)
        db.close()
        return nuevo_equipo
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los equipos"""
        db = SessionLocal()
        equipos = db.query(Equipos).all()
        db.close()
        return equipos
    
    @staticmethod
    def obtener_por_id(equipo_id):
        """Obtiene un equipo por ID"""
        db = SessionLocal()
        equipo = db.query(Equipos).filter(Equipos.id == equipo_id).first()
        db.close()
        return equipo

    @staticmethod
    def actualizar(equipo_id, **valores):
        """Actualiza un equipo por ID"""
        db = SessionLocal()
        equipo = db.query(Equipos).filter(Equipos.id == equipo_id).first()

        if not equipo:
            db.close()
            return None

        for campo, valor in valores.items():
            setattr(equipo, campo, valor)

        db.commit()
        db.refresh(equipo)
        db.close()
        return equipo
    
    @staticmethod
    def eliminar(equipo_id):
        """Elimina un equipo por ID"""
        db = SessionLocal()
        equipo = db.query(Equipos).filter(Equipos.id == equipo_id).first()
        if equipo:
            db.delete(equipo)
            db.commit()
        db.close()
