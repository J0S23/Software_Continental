from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Repuesto(Base):
    """Catalogo de tipos de repuesto (cuchilla de limpieza, banda fusora,
    rodillo fusor, etc.) y su precio.

    Costos.repuesto_id guarda el id de aqui (sin ForeignKey, igual que
    cliente_id/contrato_id/equipo_id/tipo_insumo_id en el resto del
    proyecto) para relacionar un costo de tipo "repuesto" con su precio.
    """

    __tablename__ = "repuestos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    precio = Column(Float, default=0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def agregar(nombre, precio=0):
        db = SessionLocal()
        try:
            nuevo_repuesto = Repuesto(nombre=nombre, precio=precio)
            db.add(nuevo_repuesto)
            db.commit()
            db.refresh(nuevo_repuesto)
            return nuevo_repuesto
        finally:
            db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Repuesto).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(repuesto_id):
        db = SessionLocal()
        try:
            return db.query(Repuesto).filter(Repuesto.id == repuesto_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_nombre(nombre):
        db = SessionLocal()
        try:
            return db.query(Repuesto).filter(Repuesto.nombre == nombre).first()
        finally:
            db.close()

    @staticmethod
    def actualizar(repuesto_id, **campos):
        db = SessionLocal()
        try:
            repuesto = db.query(Repuesto).filter(Repuesto.id == repuesto_id).first()
            if not repuesto:
                return None
            for nombre_campo, valor in campos.items():
                setattr(repuesto, nombre_campo, valor)
            db.commit()
            db.refresh(repuesto)
            return repuesto
        finally:
            db.close()

    @staticmethod
    def eliminar(repuesto_id):
        db = SessionLocal()
        try:
            repuesto = db.query(Repuesto).filter(Repuesto.id == repuesto_id).first()
            if repuesto:
                db.delete(repuesto)
                db.commit()
                return True
            return False
        finally:
            db.close()


Maquinas = Repuesto
