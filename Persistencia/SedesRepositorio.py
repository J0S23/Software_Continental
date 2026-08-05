from base_de_datos import SessionLocal
from Modulos.Sedes import Sedes


class SedesRepositorio:
    #CRUD de sedes/ubicaciones de un cliente Un cliente puede tener varias sedes activas

    @staticmethod
    def agregar(
        cliente_id, nombre_sede, codigo_sede=None, ciudad=None, departamento=None,
        direccion=None, piso_oficina_area=None, persona_responsable=None,
        telefono_contacto=None, correo_contacto=None, horario_atencion=None,
        condiciones_ingreso=None, observaciones_acceso=None,
        estado_sede="activa", sesion=None,
    ):
        db = sesion if sesion is not None else SessionLocal()
        try:
            nueva_sede = Sedes(
                cliente_id=cliente_id, codigo_sede=codigo_sede, nombre_sede=nombre_sede,
                ciudad=ciudad, departamento=departamento, direccion=direccion,
                piso_oficina_area=piso_oficina_area, persona_responsable=persona_responsable,
                telefono_contacto=telefono_contacto, correo_contacto=correo_contacto,
                horario_atencion=horario_atencion, condiciones_ingreso=condiciones_ingreso,
                observaciones_acceso=observaciones_acceso, estado_sede=estado_sede,
            )
            db.add(nueva_sede)
            if sesion is None:
                db.commit()
                db.refresh(nueva_sede)
            else:
                db.flush()
            return nueva_sede
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Sedes).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(sede_id):
        db = SessionLocal()
        try:
            return db.query(Sedes).filter(Sedes.id == sede_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_cliente(cliente_id):
        #Todas las sedes de un cliente. La necesitara el punto 4 de Requerimientos especiales para poblar el selector de sede_id en ContratoEquipo.
        db = SessionLocal()
        try:
            return db.query(Sedes).filter(Sedes.cliente_id == cliente_id).all()
        finally:
            db.close()

    @staticmethod
    def actualizar(sede_id, sesion=None, **campos):
        db = sesion if sesion is not None else SessionLocal()
        try:
            sede = db.query(Sedes).filter(Sedes.id == sede_id).first()
            if not sede:
                return None
            for nombre_campo, valor in campos.items():
                setattr(sede, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(sede)
            else:
                db.flush()
            return sede
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(sede_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            sede = db.query(Sedes).filter(Sedes.id == sede_id).first()
            if sede:
                db.delete(sede)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()