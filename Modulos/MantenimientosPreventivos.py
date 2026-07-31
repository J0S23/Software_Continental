from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class MantenimientoPreventivo(Base):

    #Distinto de Contratos.mantenimiento (que solo indica si el CONTRATO incluye preventivo, un flag fijo, sin historial).
    #Esta tabla es el registro real de cada visita: uno por evento, no uno por contrato. Solo define columnas

    __tablename__ = "mantenimientos_preventivos"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer, nullable=False)
    cliente_id = Column(Integer, nullable=True)
    contrato_id = Column(Integer, nullable=True)
    periodo = Column(String, nullable=True)  # "MM-YYYY", igual patron que EntregaToner
    fecha_programada = Column(DateTime, nullable=False)
    fecha_realizada = Column(DateTime, nullable=True)
    tecnico_asignado = Column(String, nullable=True)
    actividades_realizadas = Column(String, nullable=True)
    repuestos_utilizados = Column(String, nullable=True)
    contador_bn = Column(Integer, nullable=True)
    contador_color = Column(Integer, nullable=True)
    frecuencia_preventivo = Column(String, nullable=True)
    # programado | realizado | pendiente | reprogramado | cancelado
    estado = Column(String, default="programado")
    observaciones = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)