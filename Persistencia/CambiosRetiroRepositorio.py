from datetime import datetime

from base_de_datos import SessionLocal
from Modulos.CambiosRetiro import CambioRetiro
from Persistencia.EquiposRepositorio import EquiposRepositorio


class CambiosRetiroRepositorio:
    """Historial de cambios/retiros de equipo. agregar() ademas actualiza el
    estado del equipo (y del reemplazo, si aplica) en EquiposRepositorio."""

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
        sesion=None,
    ):
        db = sesion if sesion is not None else SessionLocal()
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
            if sesion is None:
                db.commit()
                db.refresh(nuevo_evento)
            else:
                db.flush()
        finally:
            if sesion is None:
                db.close()

        if actualizar_estado_equipo:
            # "retiro" da de baja el equipo; "cambio" lo manda a mantenimiento
            # y deja el equipo de reemplazo (si hay) como instalado.
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
    def actualizar(evento_id, sesion=None, **campos):
        """No existia en el Modulos/CambiosRetiro.py original -- se agrega
        para que servicios_datos.actualizar_registro no caiga al fallback
        de sesion.get(modelo, ...) con un repositorio (que no es ORM)."""
        db = sesion if sesion is not None else SessionLocal()
        try:
            evento = db.query(CambioRetiro).filter(CambioRetiro.id == evento_id).first()
            if not evento:
                return None
            for nombre_campo, valor in campos.items():
                setattr(evento, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(evento)
            else:
                db.flush()
            return evento
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(evento_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            evento = db.query(CambioRetiro).filter(CambioRetiro.id == evento_id).first()
            if evento:
                db.delete(evento)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()