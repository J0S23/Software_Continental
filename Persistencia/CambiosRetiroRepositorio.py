from datetime import datetime

from base_de_datos import SessionLocal
from Modulos.CambiosRetiro import CambioRetiro
from Persistencia.EquiposRepositorio import EquiposRepositorio


class CambiosRetiroRepositorio:

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
    def actualizar(evento_id, **campos):
        """No existia en el Modulos/CambiosRetiro.py original -- se agrega
        para que servicios_datos.actualizar_registro no caiga al fallback
        de sesion.get(modelo, ...) con un repositorio (que no es ORM)."""
        db = SessionLocal()
        try:
            evento = db.query(CambioRetiro).filter(CambioRetiro.id == evento_id).first()
            if not evento:
                return None
            for nombre_campo, valor in campos.items():
                setattr(evento, nombre_campo, valor)
            db.commit()
            db.refresh(evento)
            return evento
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
                return True
            return False
        finally:
            db.close()