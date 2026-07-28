from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class EquipoRespaldo(Base):
    
    #Asignaciones temporales de equipos de respaldo

    __tablename__ = "equipos_respaldo"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer)
    contrato_id = Column(Integer, nullable=True)
    equipo_principal_id = Column(Integer)
    equipo_respaldo_id = Column(Integer)
    motivo = Column(String)
    tecnico_responsable = Column(String)
    contador_inicial_respaldo = Column(Integer, nullable=True)
    contador_final_respaldo = Column(Integer, nullable=True)
    fecha_instalacion = Column(DateTime, default=datetime.utcnow)
    fecha_estimada_retiro = Column(DateTime, nullable=True)
    fecha_real_retiro = Column(DateTime, nullable=True)
    # Ciclo de vida de la asignacion, no del equipo fisico (ese usa
    # Equipos.estado_equipo, via EquiposRepositorio). Valores: "activo" | "devuelto"
    estado_asignacion = Column(String, default="activo")
    costo_asociado = Column(Float, default=0)
    observaciones = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)