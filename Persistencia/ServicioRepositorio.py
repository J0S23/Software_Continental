from base_de_datos import SessionLocal
from Modulos.Servicio import Servicio


class ServicioRepositorio:
    """CRUD de servicios (mantenimientos/prestaciones) ofrecidos a un cliente/equipo."""

    @staticmethod
    def agregar(cliente_id, equipo_id, nombre_servicio, descripcion="", precio=0,
                descripcion_mantenimiento="", repuestos_incluidos="No", toner_incluido="No",
                toner_respaldo_sitio="No", equipo_respaldo_incluido="No", estado="Activo"):
        db = SessionLocal()
        try:
            nuevo_servicio = Servicio(
                cliente_id=cliente_id,
                equipo_id=equipo_id,
                nombre_servicio=nombre_servicio,
                descripcion=descripcion,
                precio=precio,
                descripcion_mantenimiento=descripcion_mantenimiento,
                repuestos_incluidos=repuestos_incluidos,
                toner_incluido=toner_incluido,
                toner_respaldo_sitio=toner_respaldo_sitio,
                equipo_respaldo_incluido=equipo_respaldo_incluido,
                estado=estado,
            )
            db.add(nuevo_servicio)
            db.commit()
            db.refresh(nuevo_servicio)
            return nuevo_servicio
        finally:
            db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Servicio).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(servicio_id):
        db = SessionLocal()
        try:
            return db.query(Servicio).filter(Servicio.id == servicio_id).first()
        finally:
            db.close()

    @staticmethod
    def actualizar(servicio_id, **campos):
        """No existia en el Modulos/Servicio.py original -- se agrega por
        el mismo motivo que en CambiosRetiro/EquiposRespaldo: para que
        servicios_datos.actualizar_registro (PUT del CRUD generico) no
        caiga al fallback de sesion.get(modelo, ...) con un repositorio."""
        db = SessionLocal()
        try:
            servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
            if not servicio:
                return None
            for nombre_campo, valor in campos.items():
                setattr(servicio, nombre_campo, valor)
            db.commit()
            db.refresh(servicio)
            return servicio
        finally:
            db.close()

    @staticmethod
    def eliminar(servicio_id):
        db = SessionLocal()
        try:
            servicio = db.query(Servicio).filter(Servicio.id == servicio_id).first()
            if servicio:
                db.delete(servicio)
                db.commit()
                return True
            return False
        finally:
            db.close()