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
    # Cliente/contrato donde esta instalado actualmente
    # Desbloquea equipos_instalados/consumo en informe_por_cliente y
    # cliente_id/contrato_id en informe_por_equipo.
    cliente_id = Column(Integer, nullable=True)
    contrato_id = Column(Integer, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def agregar(numero_serie, tipo_equipo, tecnologia, color, estado_equipo, estado_tecnico,
                recomendacion_tecnica="", modelo="", toner="", rend_orig=None, rend_gen=None,
                cliente_id=None, contrato_id=None):
        db = SessionLocal()
        try:
            nuevo_equipo = Equipos(
                numero_serie=numero_serie, tipo_equipo=tipo_equipo, tecnologia=tecnologia,
                color=color, estado_equipo=estado_equipo, estado_tecnico=estado_tecnico,
                recomendacion_tecnica=recomendacion_tecnica, modelo=modelo, toner=toner,
                rend_orig=rend_orig, rend_gen=rend_gen,
                cliente_id=cliente_id, contrato_id=contrato_id,
            )
            db.add(nuevo_equipo)
            db.commit()
            db.refresh(nuevo_equipo)
            return nuevo_equipo
        finally:
            db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Equipos).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(equipo_id):
        db = SessionLocal()
        try:
            return db.query(Equipos).filter(Equipos.id == equipo_id).first()
        finally:
            db.close()

    @staticmethod
    def actualizar(equipo_id, **valores):
        db = SessionLocal()
        try:
            equipo = db.query(Equipos).filter(Equipos.id == equipo_id).first()
            if not equipo:
                return None
            for campo, valor in valores.items():
                setattr(equipo, campo, valor)
            db.commit()
            db.refresh(equipo)
            return equipo
        finally:
            db.close()

    @staticmethod
    def eliminar(equipo_id):
        db = SessionLocal()
        try:
            equipo = db.query(Equipos).filter(Equipos.id == equipo_id).first()
            if equipo:
                db.delete(equipo)
                db.commit()
                return True
            return False
        finally:
            db.close()