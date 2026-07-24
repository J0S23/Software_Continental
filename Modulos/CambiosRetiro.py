from Modulos import Equipos
from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine

class CambioRetiro(Base):
    __tablename__ = "cambios_retiros"

    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer)
    tipo_evento = Column(String)
    equipo_reemplazo_id = Column(Integer, nullable=True)
    motivo = Column(String)
    responsable = Column(String)
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
    
        #Actualizar_estado_equipo=True (por defecto) hace que, ademas de
        #crear el registro historico, se actualice Equipos.estado_equipo
        #del equipo afectado. Esto evita el error comun de "quedo el
        #registro del movimiento pero el inventario sigue diciendo que el
        #equipo esta instalado". Se puede desactivar si se prefiere hacer
        #esa actualizacion manualmente desde el frontend.

        db = SessionLocal()
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
        db.close()
 
        if actualizar_estado_equipo:
            nuevo_estado = "retirado" if tipo_evento == "retiro" else "en_mantenimiento"
            Equipos.actualizar(equipo_id, estado_equipo=nuevo_estado)
            # Si fue un cambio, el equipo de reemplazo pasa a "instalado".
            if tipo_evento == "cambio" and equipo_reemplazo_id:
                Equipos.actualizar(equipo_reemplazo_id, estado_equipo="instalado")
 
        return nuevo_evento
 
    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        eventos = db.query(CambioRetiro).all()
        db.close()
        return eventos
 
    @staticmethod
    def obtener_por_id(evento_id):
        db = SessionLocal()
        evento = db.query(CambioRetiro).filter(CambioRetiro.id == evento_id).first()
        db.close()
        return evento
 
    @staticmethod
    def obtener_por_equipo(equipo_id):
        """Historial completo de movimientos de un equipo especifico."""
        db = SessionLocal()
        eventos = (
            db.query(CambioRetiro)
            .filter(CambioRetiro.equipo_id == equipo_id)
            .order_by(CambioRetiro.fecha_evento)
            .all()
        )
        db.close()
        return eventos
 
    @staticmethod
    def eliminar(evento_id):
        db = SessionLocal()
        evento = db.query(CambioRetiro).filter(CambioRetiro.id == evento_id).first()
        if evento:
            db.delete(evento)
            db.commit()
        db.close()