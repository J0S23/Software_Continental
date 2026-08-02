from base_de_datos import SessionLocal
from Modulos.MantenimientosPreventivos import MantenimientoPreventivo


class MantenimientosPreventivosRepositorio:

    @staticmethod
    def agregar(
        equipo_id, fecha_programada, cliente_id=None, contrato_id=None,
        periodo=None, fecha_realizada=None, tecnico_asignado=None,
        actividades_realizadas=None, repuestos_utilizados=None,
        contador_bn=None, contador_color=None, frecuencia_preventivo=None,
        estado="programado", observaciones=None, sesion=None,
    ):
        periodo = periodo or (
            f"{fecha_programada.month:02d}-{fecha_programada.year}" if fecha_programada else None
        )
        db = sesion if sesion is not None else SessionLocal()
        try:
            nuevo = MantenimientoPreventivo(
                equipo_id=equipo_id, cliente_id=cliente_id, contrato_id=contrato_id,
                periodo=periodo, fecha_programada=fecha_programada, fecha_realizada=fecha_realizada,
                tecnico_asignado=tecnico_asignado, actividades_realizadas=actividades_realizadas,
                repuestos_utilizados=repuestos_utilizados, contador_bn=contador_bn,
                contador_color=contador_color, frecuencia_preventivo=frecuencia_preventivo,
                estado=estado, observaciones=observaciones,
            )
            db.add(nuevo)
            if sesion is None:
                db.commit()
                db.refresh(nuevo)
            else:
                db.flush()
            return nuevo
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(MantenimientoPreventivo).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(mantenimiento_id):
        db = SessionLocal()
        try:
            return db.query(MantenimientoPreventivo).filter(MantenimientoPreventivo.id == mantenimiento_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_equipo(equipo_id):
        db = SessionLocal()
        try:
            return (
                db.query(MantenimientoPreventivo)
                .filter(MantenimientoPreventivo.equipo_id == equipo_id)
                .order_by(MantenimientoPreventivo.fecha_programada)
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def obtener_por_periodo(periodo):
        db = SessionLocal()
        try:
            return db.query(MantenimientoPreventivo).filter(MantenimientoPreventivo.periodo == periodo).all()
        finally:
            db.close()

    @staticmethod
    def obtener_vencidos_sin_realizar(antes_de):
        #Preventivos programados antes de 'antes_de' que no llegaron a 'realizado' ni 'cancelado'. La necesita Alertas para 'preventivo_vencido'.
        db = SessionLocal()
        try:
            return (
                db.query(MantenimientoPreventivo)
                .filter(
                    MantenimientoPreventivo.fecha_programada < antes_de,
                    MantenimientoPreventivo.estado.notin_(["realizado", "cancelado"]),
                )
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def actualizar(mantenimiento_id, sesion=None, **campos):
        db = sesion if sesion is not None else SessionLocal()
        try:
            registro = db.query(MantenimientoPreventivo).filter(MantenimientoPreventivo.id == mantenimiento_id).first()
            if not registro:
                return None
            for nombre_campo, valor in campos.items():
                setattr(registro, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(registro)
            else:
                db.flush()
            return registro
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(mantenimiento_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            registro = db.query(MantenimientoPreventivo).filter(MantenimientoPreventivo.id == mantenimiento_id).first()
            if registro:
                db.delete(registro)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()