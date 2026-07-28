from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class Repuesto(Base):
    #Solo define columnas. Acceso a datos en Repositorios/RepuestosRepositorio.py.

    #Costos.repuesto_id guarda el id de aqui (sin ForeignKey, igual que cliente_id/contrato_id/equipo_id/tipo_insumo_id
    #en el resto del proyecto) para relacionar un costo de tipo "repuesto" con su precio.
    

    __tablename__ = "repuestos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, unique=True, index=True)
    precio = Column(Float, default=0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)