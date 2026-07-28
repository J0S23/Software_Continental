from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine
from Persistencia.EquiposRepositorio import EquiposRepositorio


class CambioRetiro(Base):
    __tablename__ = "cambios_retiros"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer)
    tipo_evento = Column(String)
    equipo_reemplazo_id = Column(Integer, nullable=True)
    cliente_id = Column(Integer, nullable=True)
    contrato_id = Column(Integer, nullable=True)
    contador_final = Column(Integer, nullable=True)
    motivo = Column(String)
    tecnico_responsable = Column(String)
    persona_recibe = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)
    fecha_evento = Column(DateTime, default=datetime.utcnow)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def agregar(
        equipo_id,
        tipo_evento,
        motivo,
        tecnico_responsable,
        equipo_reemplazo_id=None,
        cliente_id=None,
        contrato_id=None,
        contador_final=None,
        persona_recibe="",
        observaciones="",
        fecha_evento=None,
        actualizar_estado_equipo=True,
    ):
        db = SessionLocal()
        try:
            nuevo_evento = CambioRetiro(
                equipo_id=equipo_id,
                tipo_evento=tipo_evento,
                equipo_reemplazo_id=equipo_reemplazo_id,
                cliente_id=cliente_id,
                contrato_id=contrato_id,
                contador_final=contador_final,
                motivo=motivo,
                tecnico_responsable=tecnico_responsable,
                persona_recibe=persona_recibe,
                observaciones=observaciones,
                fecha_evento=fecha_evento or datetime.utcnow(),
            )
            db.add(nuevo_evento)
            db.commit()
            db.refresh(nuevo_evento)
        finally:
            db.close()

        if actualizar_estado_equipo:
            nuevo_estado = "retirado" if tipo_evento == "retiro" else "en_mantenimiento"
            EquiposRepositorio.actualizar(equipo_id, estado_equipo=nuevo_estado)
            if tipo_evento == "cambio" and equipo_reemplazo_id:
                EquiposRepositorio.actualizar(equipo_reemplazo_id, estado_equipo="instalado")

        return nuevo_evento

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(CambioRetiro).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(evento_id):
        db = SessionLocal()
        try:
            return db.query(CambioRetiro).filter(CambioRetiro.id == evento_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_equipo(equipo_id):
        db = SessionLocal()
        try:
            return (
                db.query(CambioRetiro)
                .filter(CambioRetiro.equipo_id == equipo_id)
                .order_by(CambioRetiro.fecha_evento)
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def eliminar(evento_id):
        db = SessionLocal()
        try:
            evento = db.query(CambioRetiro).filter(CambioRetiro.id == evento_id).first()
            if evento:
                db.delete(evento)
                db.commit()
        finally:
            db.close()