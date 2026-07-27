"""Persistencia del estado de las alertas (leida/guardada/descartada).

Las alertas en si no tienen tabla propia (Servicio/Alertas.py las calcula al
vuelo a partir de Contratos, Facturacion, Cartera, Equipos y Lecturas). Esta
tabla solo guarda, por alerta (identificada por tipo + referencia_id), que
accion tomo el usuario sobre ella. Se guarda tambien un snapshot de
mensaje/nivel para que una alerta "guardada" se pueda seguir mostrando
aunque la condicion que la genero ya no se cumpla (p. ej. el contrato ya
se renovo).
"""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, UniqueConstraint
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class AlertaEstado(Base):
    __tablename__ = "alertas_estado"
    __table_args__ = (UniqueConstraint("tipo", "referencia_id", name="uq_alerta_tipo_referencia"),)

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)
    referencia_id = Column(Integer, nullable=True)
    mensaje = Column(String, nullable=True)
    nivel = Column(String, nullable=True)
    leida = Column(Boolean, default=False, nullable=False)
    guardada = Column(Boolean, default=False, nullable=False)
    descartada = Column(Boolean, default=False, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)

    @staticmethod
    def obtener_todos():
        """Obtiene el estado guardado de todas las alertas"""
        db = SessionLocal()
        try:
            return db.query(AlertaEstado).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_alerta(tipo, referencia_id):
        """Obtiene el estado guardado de una alerta puntual (tipo + referencia_id)"""
        db = SessionLocal()
        try:
            return (
                db.query(AlertaEstado)
                .filter(AlertaEstado.tipo == tipo, AlertaEstado.referencia_id == referencia_id)
                .first()
            )
        finally:
            db.close()

    @staticmethod
    def obtener_guardadas():
        """Alertas marcadas como guardadas (y no descartadas), para la vista de guardados"""
        db = SessionLocal()
        try:
            return (
                db.query(AlertaEstado)
                .filter(AlertaEstado.guardada.is_(True), AlertaEstado.descartada.is_(False))
                .order_by(AlertaEstado.fecha_actualizacion.desc())
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def marcar(tipo, referencia_id=None, mensaje=None, nivel=None,
               leida=None, guardada=None, descartada=None):
        """Crea o actualiza (upsert) el estado de una alerta. Los campos en
        None no se tocan, para permitir actualizaciones parciales (p. ej.
        solo marcar 'leida' sin afectar 'guardada')."""
        db = SessionLocal()
        try:
            estado = (
                db.query(AlertaEstado)
                .filter(AlertaEstado.tipo == tipo, AlertaEstado.referencia_id == referencia_id)
                .first()
            )

            if not estado:
                estado = AlertaEstado(tipo=tipo, referencia_id=referencia_id)
                db.add(estado)

            if mensaje is not None:
                estado.mensaje = mensaje
            if nivel is not None:
                estado.nivel = nivel
            if leida is not None:
                estado.leida = leida
            if guardada is not None:
                estado.guardada = guardada
            if descartada is not None:
                estado.descartada = descartada
            estado.fecha_actualizacion = datetime.utcnow()

            db.commit()
            db.refresh(estado)
            return estado
        finally:
            db.close()
