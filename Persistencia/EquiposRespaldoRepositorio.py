from datetime import datetime

from base_de_datos import SessionLocal
from Modulos.EquiposRespaldo import EquipoRespaldo
from Persistencia.EquiposRepositorio import EquiposRepositorio


class EquiposRespaldoRepositorio:
    """Asignaciones temporales de equipo de respaldo mientras el principal
    esta en reparacion. agregar()/finalizar() sincronizan el estado de ambos
    equipos en EquiposRepositorio (mismo patron que ContratoEquipoRepositorio)."""

    @staticmethod
    def _asignacion_activa_de(db, equipo_id):
        """Asignacion de respaldo activa donde equipo_id participa, como
        principal o como respaldo. Evita dobles asignaciones y bloquea
        cambios/retiros mientras el equipo esta en un proceso sin cerrar."""
        return (
            db.query(EquipoRespaldo)
            .filter(
                EquipoRespaldo.estado_asignacion == "activo",
                (EquipoRespaldo.equipo_principal_id == equipo_id)
                | (EquipoRespaldo.equipo_respaldo_id == equipo_id),
            )
            .first()
        )

    @staticmethod
    def agregar(
        cliente_id, equipo_principal_id, equipo_respaldo_id, motivo, tecnico_responsable,
        contrato_id=None, contador_inicial_respaldo=None, fecha_estimada_retiro=None,
        costo_asociado=0, observaciones="", actualizar_estado_equipo=True,
    ):
        db = SessionLocal()
        try:
            ya_respaldado = EquiposRespaldoRepositorio._asignacion_activa_de(db, equipo_principal_id)
            if ya_respaldado:
                raise ValueError(
                    f"El equipo {equipo_principal_id} ya tiene una asignacion de respaldo "
                    f"activa (id {ya_respaldado.id})."
                )

            respaldo_ocupado = EquiposRespaldoRepositorio._asignacion_activa_de(db, equipo_respaldo_id)
            if respaldo_ocupado:
                raise ValueError(
                    f"El equipo {equipo_respaldo_id} ya esta participando en otra asignacion "
                    f"de respaldo activa (id {respaldo_ocupado.id})."
                )

            equipo_respaldo_obj = EquiposRepositorio.obtener_por_id(equipo_respaldo_id)
            estado_actual = (equipo_respaldo_obj.estado_equipo or "").strip().lower() if equipo_respaldo_obj else ""
            if equipo_respaldo_obj and estado_actual not in ("de_respaldo", "disponible"):
                raise ValueError(
                    f"El equipo {equipo_respaldo_id} esta en estado '{equipo_respaldo_obj.estado_equipo}' "
                    "y no puede usarse como respaldo."
                )

            nueva_asignacion = EquipoRespaldo(
                cliente_id=cliente_id, contrato_id=contrato_id,
                equipo_principal_id=equipo_principal_id, equipo_respaldo_id=equipo_respaldo_id,
                motivo=motivo, tecnico_responsable=tecnico_responsable,
                contador_inicial_respaldo=contador_inicial_respaldo,
                fecha_estimada_retiro=fecha_estimada_retiro, costo_asociado=costo_asociado,
                observaciones=observaciones, estado_asignacion="activo",
            )
            db.add(nueva_asignacion)
            db.commit()
            db.refresh(nueva_asignacion)
        finally:
            db.close()

        if actualizar_estado_equipo:
            EquiposRepositorio.actualizar(equipo_respaldo_id, estado_equipo="instalado")
            EquiposRepositorio.actualizar(equipo_principal_id, estado_equipo="en_reparacion")

        return nueva_asignacion

    @staticmethod
    def finalizar(asignacion_id, contador_final_respaldo=None, actualizar_estado_equipo=True):
        """Cierra la asignacion cuando el equipo principal vuelve a servicio
        y el respaldo se retira. No borra el registro (se conserva historial),
        solo se marca como devuelto."""
        db = SessionLocal()
        try:
            asignacion = db.query(EquipoRespaldo).filter(EquipoRespaldo.id == asignacion_id).first()
            if not asignacion:
                return None

            asignacion.estado_asignacion = "devuelto"
            asignacion.fecha_real_retiro = datetime.utcnow()
            if contador_final_respaldo is not None:
                asignacion.contador_final_respaldo = contador_final_respaldo

            db.commit()
            db.refresh(asignacion)
            equipo_respaldo_id = asignacion.equipo_respaldo_id
            equipo_principal_id = asignacion.equipo_principal_id
        finally:
            db.close()

        if actualizar_estado_equipo:
            EquiposRepositorio.actualizar(equipo_respaldo_id, estado_equipo="de_respaldo")
            EquiposRepositorio.actualizar(equipo_principal_id, estado_equipo="instalado")

        return asignacion

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(EquipoRespaldo).all()
        finally:
            db.close()

    @staticmethod
    def obtener_activas():
        db = SessionLocal()
        try:
            return db.query(EquipoRespaldo).filter(EquipoRespaldo.estado_asignacion == "activo").all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(asignacion_id):
        db = SessionLocal()
        try:
            return db.query(EquipoRespaldo).filter(EquipoRespaldo.id == asignacion_id).first()
        finally:
            db.close()

    @staticmethod
    def actualizar(asignacion_id, **campos):
        """No existia en el Modulos/EquiposRespaldo.py original -- 'finalizar'
        es la operacion de negocio especifica para cerrar una asignacion
        (y sigue siendo el camino recomendado para eso). Este 'actualizar'
        generico es solo para que el CRUD generico del frontend
        (servicios_datos.py) tenga a donde caer si llega un PUT."""
        db = SessionLocal()
        try:
            asignacion = db.query(EquipoRespaldo).filter(EquipoRespaldo.id == asignacion_id).first()
            if not asignacion:
                return None
            for nombre_campo, valor in campos.items():
                setattr(asignacion, nombre_campo, valor)
            db.commit()
            db.refresh(asignacion)
            return asignacion
        finally:
            db.close()

    @staticmethod
    def eliminar(asignacion_id):
        db = SessionLocal()
        try:
            asignacion = db.query(EquipoRespaldo).filter(EquipoRespaldo.id == asignacion_id).first()
            if asignacion:
                db.delete(asignacion)
                db.commit()
                return True
            return False
        finally:
            db.close()