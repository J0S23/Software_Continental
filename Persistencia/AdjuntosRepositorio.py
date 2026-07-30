from base_de_datos import SessionLocal
from Modulos.Adjuntos import Adjunto


class AdjuntosRepositorio:
    #CRUD de adjuntos. agregar() la usa routers/adjuntos.py despues de guardar el archivo fisico en disco (ver configuracion.RUTA_ADJUNTOS).

    @staticmethod
    def agregar(tipo_entidad, entidad_id, nombre_original, nombre_archivo,
                tipo_documento=None, content_type=None, tamano_bytes=None,
                subido_por=None, observaciones=None):
        db = SessionLocal()
        try:
            nuevo_adjunto = Adjunto(
                tipo_entidad=tipo_entidad, entidad_id=entidad_id,
                tipo_documento=tipo_documento, nombre_original=nombre_original,
                nombre_archivo=nombre_archivo, content_type=content_type,
                tamano_bytes=tamano_bytes, subido_por=subido_por,
                observaciones=observaciones,
            )
            db.add(nuevo_adjunto)
            db.commit()
            db.refresh(nuevo_adjunto)
            return nuevo_adjunto
        finally:
            db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Adjunto).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(adjunto_id):
        db = SessionLocal()
        try:
            return db.query(Adjunto).filter(Adjunto.id == adjunto_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_entidad(tipo_entidad, entidad_id):
    #La necesita GET /api/adjuntos para listar los adjuntos de un registro especifico (ej. tipo_entidad='equipos', entidad_id=5).
        db = SessionLocal()
        try:
            return (
                db.query(Adjunto)
                .filter(Adjunto.tipo_entidad == tipo_entidad, Adjunto.entidad_id == entidad_id)
                .order_by(Adjunto.fecha_subida.desc())
                .all()
            )
        finally:
            db.close()

    @staticmethod
    def eliminar(adjunto_id):
        #Devuelve el nombre_archivo (para que el router borre el archivo fisico) en vez de un bool, porque a diferencia del resto de
        #repositorios aqui SI hace falta un dato del registro despues de borrarlo de la base de datos.
        db = SessionLocal()
        try:
            adjunto = db.query(Adjunto).filter(Adjunto.id == adjunto_id).first()
            if not adjunto:
                return None
            nombre_archivo = adjunto.nombre_archivo
            db.delete(adjunto)
            db.commit()
            return nombre_archivo
        finally:
            db.close()