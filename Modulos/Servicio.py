from Modulos.enums import TipoMantenimiento
from sqlalchemy import Column, Integer, String, Float, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, engine


class Servicio(Base):

    #Cuando mantenimiento=CORRECTIVO, esta fila funciona ademas como el registro de una falla atendida los campos fecha_solicitud..
    #estado_caso solo aplican en ese caso y quedan en NULL para el resto de usos de Servicio (venta de servicios generales, etc).
    #Es la fuente que usa Informes_mensuales.informe_tecnico / Servicio/Alertas.py para calcular 'equipos con fallas recurrentes'.

    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer)
    equipo_id = Column(Integer, nullable=True)
    nombre_servicio = Column(String)
    descripcion = Column(String, nullable=True)
    precio = Column(Float, default=0)
    mantenimiento = Column(SQLEnum(TipoMantenimiento), default=TipoMantenimiento.CORRECTIVO, nullable=False)
    descripcion_mantenimiento = Column(String, nullable=True)
    repuestos_incluidos = Column(String, default="No")
    toner_incluido = Column(String, default="No")
    toner_respaldo_sitio = Column(String, default="No")
    equipo_respaldo_incluido = Column(String, default="No")
    estado = Column(String, default="Activo")
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    #Campos de mantenimiento correctivo, solo aplican si mantenimiento=CORRECTIVO
    contrato_id = Column(Integer, nullable=True)
    fecha_solicitud = Column(DateTime, nullable=True)
    falla_reportada = Column(String, nullable=True)
    prioridad = Column(String, nullable=True)  # alta | media | baja
    fecha_atencion = Column(DateTime, nullable=True)
    fecha_solucion = Column(DateTime, nullable=True)
    diagnostico = Column(String, nullable=True)
    costo_repuestos = Column(Float, nullable=True, default=0)
    costo_mano_obra = Column(Float, nullable=True, default=0)
    costo_desplazamiento = Column(Float, nullable=True, default=0)
    requiere_respaldo = Column(String, nullable=True, default="No")
    # abierto | en_proceso | cerrado | pendiente_repuesto | pendiente_autorizacion
    estado_caso = Column(String, nullable=True)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)