from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine
from Modulos.Equipos import Equipos


class EquipoRespaldo(Base):

    #Asignaciones temporales de equipos de respaldo (seccion 14 del
    #documento de requerimientos).

    # Por que un modelo aparte y no solo un estado en Equipos.py:
    # Equipos.estado_equipo ya tiene el valor "de_respaldo" (ver
    # Modulos/enums.py -> EstadoEquipo.DE_RESPALDO), pero ese campo solo
    # dice "este equipo ES de tipo respaldo en el inventario", no dice
    # A QUIEN esta prestado ahora mismo, desde cuando, ni por que.
    # El documento pide poder responder "que equipo de respaldo esta en
    # que cliente" y calcular el "costo asociado al respaldo" (usado
    # luego en Costos.py / Rentabilidad.py como TipoCosto.EQUIPO_RESPALDO).
    # Eso requiere una relacion equipo_principal <-> equipo_respaldo con
    # fechas, y un registro simple de estado no alcanza.

    __tablename__ = "equipos_respaldo"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer)
    contrato_id = Column(Integer, nullable=True)

    # Equipo que fallo y necesita el respaldo mientras se repara.
    equipo_principal_id = Column(Integer)

    # Equipo que se presta temporalmente.
    equipo_respaldo_id = Column(Integer)

    motivo = Column(String)
    tecnico_responsable = Column(String)
    contador_inicial_respaldo = Column(Integer, nullable=True)
    contador_final_respaldo = Column(Integer, nullable=True)
    fecha_instalacion = Column(DateTime, default=datetime.utcnow)
    fecha_estimada_retiro = Column(DateTime, nullable=True)
    fecha_real_retiro = Column(DateTime, nullable=True)

    # estado_asignacion sigue el ciclo de vida de la asignacion, no del
    # equipo fisico (el equipo fisico usa Equipos.estado_equipo).
    # Valores esperados: "activo" | "devuelto"
    estado_asignacion = Column(String, default="activo")

    # Costo asociado al respaldo (seccion 14 y 11.1: TipoCosto.EQUIPO_RESPALDO).
    # Se deja aqui como referencia rapida, pero el registro contable real
    # del costo debe crearse tambien en Costos.py para que
    # Informes_mensuales / Rentabilidad lo tengan en cuenta -- ver nota en
    # el metodo agregar() mas abajo.
    costo_asociado = Column(Float, default=0)

    observaciones = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
