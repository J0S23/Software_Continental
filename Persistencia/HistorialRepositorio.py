from base_de_datos import SessionLocal
from Modulos.Historial import Historial


class HistorialRepositorio:
    """Auditoria transversal de crear/actualizar/eliminar sobre cualquier
    tipo_entidad del catalogo. Usado por servicios_datos.py."""

    @staticmethod
    def registrar(tipo_entidad, entidad_id, accion, usuario_id, campo=None, valor_anterior=None, valor_nuevo=None):
        db = SessionLocal()
        try:
            nuevo_registro = Historial(
                tipo_entidad=tipo_entidad,
                entidad_id=entidad_id,
                accion=accion,
                usuario_id=usuario_id,
                campo=campo,
                valor_anterior=valor_anterior,
                valor_nuevo=valor_nuevo,
            )
            db.add(nuevo_registro)
            db.commit()
            db.refresh(nuevo_registro)
            return nuevo_registro
        finally:
            db.close()

    @staticmethod
    def obtener_por_entidad(tipo_entidad, entidad_id):
        db = SessionLocal()
        try:
            return (
                db.query(Historial)
                .filter(Historial.tipo_entidad == tipo_entidad, Historial.entidad_id == entidad_id)
                .order_by(Historial.fecha)
                .all()
            )
        finally:
            db.close()
