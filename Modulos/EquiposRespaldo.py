from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine
from Persistencia.EquiposRepositorio import EquiposRepositorio

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

class EquipoRespaldo(Base):
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

    @staticmethod
    def _asignacion_activa_de(db, equipo_id):
        """Asignacion de respaldo activa donde equipo_id participa, como
        principal o como respaldo. Se usa para evitar dobles asignaciones
        y para bloquear cambios/retiros mientras el equipo esta en un
        proceso de respaldo sin cerrar."""
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

        #Crea la asignacion de respaldo.

        #NOTA IMPORTANTE: este metodo NO crea automaticamente un registro
        #en Costos.py, aunque guarda costo_asociado aqui para consulta
        #rapida. Si el costo del respaldo debe aparecer en los informes
        #mensuales / rentabilidad (Modulos/Informes_mensuales.py filtra por
        #Costos.tipo_costo), hay que llamar tambien a:

            #Costos.agregar(..., tipo_costo=TipoCosto.EQUIPO_RESPALDO, ...)

        #desde el router, para no duplicar logica de negocio dentro del
        #modelo. Se deja como decision explicita del router/servicio que
        #llama a este metodo.

        db = SessionLocal()
        try:
            ya_respaldado = EquipoRespaldo._asignacion_activa_de(db, equipo_principal_id)
            if ya_respaldado:
                #El raise ValueError esta dentro del try por lo que la sesión se cierra igual aunque se aborte la operación
                raise ValueError(
                    f"El equipo {equipo_principal_id} ya tiene una asignacion de respaldo "
                    f"activa (id {ya_respaldado.id})."
                )

            respaldo_ocupado = EquipoRespaldo._asignacion_activa_de(db, equipo_respaldo_id)
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
            if actualizar_estado_equipo:
                EquiposRepositorio.actualizar(equipo_respaldo_id, estado_equipo="instalado")
                EquiposRepositorio.actualizar(equipo_principal_id, estado_equipo="en_reparacion")

        return nueva_asignacion

    @staticmethod
    def finalizar(asignacion_id, contador_final_respaldo=None, actualizar_estado_equipo=True):

        #Cierra la asignacion cuando el equipo principal vuelve a servicio
        #y el respaldo se retira. Metodo separado de 'eliminar' porque aqui
        #NO se borra el registro (se necesita conservar el historial),
        #solo se marca como devuelto.

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