from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine
from Modulos.TiposInsumo import TipoInsumo


class Insumo(Base):
    __tablename__ = "insumos"

    id = Column(Integer, primary_key=True, index=True)
    tipo_insumo_id = Column(Integer)
    color = Column(String, nullable=True)
    estado = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @property
    def tipo(self):
        """Tipo de insumo relacionado (con su nombre y precio)."""
        if self.tipo_insumo_id is None:
            return None
        return TipoInsumo.obtener_por_id(self.tipo_insumo_id)

    @property
    def precio(self):
        """Precio relacionado directamente segun el tipo de insumo."""
        tipo = self.tipo
        return tipo.precio if tipo else None

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def agregar(tipo_insumo_id, color="", estado=""):
        """Agrega un insumo a la BD"""
        db = SessionLocal()
        nuevo_insumo = Insumo(tipo_insumo_id=tipo_insumo_id, color=color, estado=estado)
        db.add(nuevo_insumo)
        db.commit()
        db.refresh(nuevo_insumo)
        db.close()
        return nuevo_insumo

    @staticmethod
    def obtener_todos():
        """Obtiene todos los insumos"""
        db = SessionLocal()
        insumos = db.query(Insumo).all()
        db.close()
        return insumos

    @staticmethod
    def obtener_por_id(insumo_id):
        """Obtiene un insumo por ID"""
        db = SessionLocal()
        insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
        db.close()
        return insumo

    @staticmethod
    def eliminar(insumo_id):
        """Elimina un insumo por ID"""
        db = SessionLocal()
        insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
        if insumo:
            db.delete(insumo)
            db.commit()
        db.close()


Maquinas = Insumo
