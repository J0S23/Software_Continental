from datetime import datetime

from base_de_datos import SessionLocal
from Modulos.AlertaEstado import AlertaEstado


class AlertaEstadoRepositorio:
    """Guarda el estado (leida/guardada/descartada) de las alertas que
    Servicio/Alertas.py calcula al vuelo, ya que las alertas en si no
    tienen tabla propia. Ver Modulos/AlertaEstado.py para el detalle."""

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(AlertaEstado).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_alerta(tipo, referencia_id):
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

    @staticmethod
    def actualizar(alerta_estado_id, sesion=None, **campos):
        """No existia en el Modulos/AlertaEstado.py original -- 'marcar' es
        el camino de negocio (upsert por tipo+referencia_id), pero se agrega
        este generico por id para que servicios_datos.py tenga a donde caer
        si este modulo llega a exponerse alguna vez en el CRUD generico del
        frontend (hoy no esta en catalogo_modelos.py, igual que Servicio y
        Usuarios)."""
        db = sesion if sesion is not None else SessionLocal()
        try:
            estado = db.query(AlertaEstado).filter(AlertaEstado.id == alerta_estado_id).first()
            if not estado:
                return None
            for nombre_campo, valor in campos.items():
                setattr(estado, nombre_campo, valor)
            estado.fecha_actualizacion = datetime.utcnow()
            if sesion is None:
                db.commit()
                db.refresh(estado)
            else:
                db.flush()
            return estado
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(alerta_estado_id, sesion=None):
        """Tampoco existia antes -- mismo motivo que 'actualizar' arriba."""
        db = sesion if sesion is not None else SessionLocal()
        try:
            estado = db.query(AlertaEstado).filter(AlertaEstado.id == alerta_estado_id).first()
            if estado:
                db.delete(estado)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()