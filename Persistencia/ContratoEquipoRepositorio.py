from datetime import datetime

from base_de_datos import SessionLocal
from Modulos.ContratoEquipo import ContratoEquipo
from Persistencia.EquiposRepositorio import EquiposRepositorio


class ContratoEquipoRepositorio:

    #CRUD + logica de negocio para la tabla intermediaria contrato-equipo.
    #agregar()/retirar() mantienen Equipos.contrato_id y Equipos.estado_equipo sincronizados como cache del contrato 
    #activo actual del equipo (mismo patron que ya usan CambiosRetiroRepositorio y EquiposRespaldoRepositorio para sincronizar el estado del equipo).
    #La fuente de verdad para el historial y para "que equipos tiene un contrato" es siempre esta tabla.
    
    @staticmethod
    def obtener_activo_por_equipo(equipo_id):
        db = SessionLocal()
        try:
            return (
                db.query(ContratoEquipo)
                .filter(ContratoEquipo.equipo_id == equipo_id, ContratoEquipo.estado_actual == "activo")
                .first()
            )
        finally:
            db.close()

    @staticmethod
    def agregar(
        contrato_id, equipo_id, sede=None, area_uso=None,
        contador_inicial_bn=0, contador_inicial_color=0,
        usuario_responsable=None, observaciones=None, fecha_instalacion=None,
        actualizar_estado_equipo=True, sesion=None,
    ):
        #Asocia un equipo a un contrato. Bloquea (ValueError) si el equipo ya tiene una asignacion activa -- un equipo fisico solo
        #puede estar instalado en un contrato a la vez, ya sea el mismo contrato (duplicado) u otro (hay que retirarlo de ahi primero).

        ya_activo = ContratoEquipoRepositorio.obtener_activo_por_equipo(equipo_id)
        if ya_activo and ya_activo.contrato_id != contrato_id:
            raise ValueError(
                f"El equipo {equipo_id} ya esta asignado activamente al contrato "
                f"{ya_activo.contrato_id}. Retira esa asignacion antes de reasignarlo."
            )
        if ya_activo and ya_activo.contrato_id == contrato_id:
            raise ValueError(
                f"El equipo {equipo_id} ya esta activo en el contrato {contrato_id} "
                f"(asignacion {ya_activo.id})."
            )

        db = sesion if sesion is not None else SessionLocal()
        try:
            nueva_asignacion = ContratoEquipo(
                contrato_id=contrato_id, equipo_id=equipo_id, sede=sede, area_uso=area_uso,
                contador_inicial_bn=contador_inicial_bn, contador_inicial_color=contador_inicial_color,
                usuario_responsable=usuario_responsable, observaciones=observaciones,
                estado_actual="activo", fecha_instalacion=fecha_instalacion or datetime.utcnow(),
            )
            db.add(nueva_asignacion)
            if sesion is None:
                db.commit()
                db.refresh(nueva_asignacion)
            else:
                db.flush()
        finally:
            if sesion is None:
                db.close()

        if actualizar_estado_equipo:
            EquiposRepositorio.actualizar(equipo_id, contrato_id=contrato_id, estado_equipo="instalado")

        return nueva_asignacion

    @staticmethod
    def retirar(asignacion_id, fecha_retiro=None, actualizar_estado_equipo=True):
        #Cierra una asignacion (estado_actual="retirado") sin borrar el registro, para conservar el historial.
        #Limpia Equipos.contrato_id y vuelve el equipo a 'disponible' -- llamar a EquiposRepositorio despues si en realidad
        #se va a otro estado (retirado, en reparacion, etc.).
        db = SessionLocal()
        try:
            asignacion = db.query(ContratoEquipo).filter(ContratoEquipo.id == asignacion_id).first()
            if not asignacion:
                return None

            asignacion.estado_actual = "retirado"
            asignacion.fecha_retiro = fecha_retiro or datetime.utcnow()
            db.commit()
            db.refresh(asignacion)
            equipo_id = asignacion.equipo_id
        finally:
            db.close()

        if actualizar_estado_equipo:
            EquiposRepositorio.actualizar(equipo_id, contrato_id=None, estado_equipo="disponible")

        return asignacion

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(ContratoEquipo).all()
        finally:
            db.close()

    @staticmethod
    def obtener_todos_activos():
        #La necesita Alertas._alertas_equipos para saber que equipos tienen contrato activo, sin recorrer contrato por contrato.
        db = SessionLocal()
        try:
            return db.query(ContratoEquipo).filter(ContratoEquipo.estado_actual == "activo").all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(asignacion_id):
        db = SessionLocal()
        try:
            return db.query(ContratoEquipo).filter(ContratoEquipo.id == asignacion_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_contrato(contrato_id, solo_activos=True):
        #La necesita FacturacionAutomatica para saber que equipos debe facturar de un contrato. Por defecto solo trae los activos.
        db = SessionLocal()
        try:
            query = db.query(ContratoEquipo).filter(ContratoEquipo.contrato_id == contrato_id)
            if solo_activos:
                query = query.filter(ContratoEquipo.estado_actual == "activo")
            return query.all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_equipo(equipo_id, solo_activos=False):
        db = SessionLocal()
        try:
            query = db.query(ContratoEquipo).filter(ContratoEquipo.equipo_id == equipo_id)
            if solo_activos:
                query = query.filter(ContratoEquipo.estado_actual == "activo")
            return query.order_by(ContratoEquipo.fecha_instalacion).all()
        finally:
            db.close()

    @staticmethod
    def actualizar(asignacion_id, sesion=None, **campos):
        #CRUD generico (para servicios_datos.py / PUT del frontend). No dispara los efectos secundarios de agregar()/retirar():
        #si se usa para cambiar estado_actual a 'retirado' desde el frontend generico, Equipos.contrato_id NO se limpia automaticamente. Usa retirar()
        #para el flujo de negocio completo (o expon un endpoint dedicado que lo llame).
        db = sesion if sesion is not None else SessionLocal()
        try:
            asignacion = db.query(ContratoEquipo).filter(ContratoEquipo.id == asignacion_id).first()
            if not asignacion:
                return None
            for nombre_campo, valor in campos.items():
                setattr(asignacion, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(asignacion)
            else:
                db.flush()
            return asignacion
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(asignacion_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            asignacion = db.query(ContratoEquipo).filter(ContratoEquipo.id == asignacion_id).first()
            if asignacion:
                db.delete(asignacion)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()