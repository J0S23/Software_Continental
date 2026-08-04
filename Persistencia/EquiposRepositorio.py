from base_de_datos import SessionLocal
from Modulos.Equipos import Equipos


class EquiposRepositorio:
    """CRUD de equipos fisicos. actualizar() es el punto usado por otros
    repositorios (ContratoEquipoRepositorio, CambiosRetiroRepositorio,
    EquiposRespaldoRepositorio) para sincronizar estado_equipo/contrato_id."""

    @staticmethod
    def agregar(numero_serie, tipo_equipo, tecnologia, color, estado_equipo, estado_tecnico,
                recomendacion_tecnica="", modelo="", toner="", rend_orig=None, rend_gen=None,
                contador_inicial_bn=0, contador_inicial_color=0,
                cliente_id=None, contrato_id=None, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            nuevo_equipo = Equipos(
                numero_serie=numero_serie, tipo_equipo=tipo_equipo, tecnologia=tecnologia,
                color=color, estado_equipo=estado_equipo, estado_tecnico=estado_tecnico,
                recomendacion_tecnica=recomendacion_tecnica, modelo=modelo, toner=toner,
                rend_orig=rend_orig, rend_gen=rend_gen,
                contador_inicial_bn=contador_inicial_bn, contador_inicial_color=contador_inicial_color,
                cliente_id=cliente_id, contrato_id=contrato_id,
            )
            db.add(nuevo_equipo)
            if sesion is None:
                db.commit()
                db.refresh(nuevo_equipo)
            else:
                db.flush()
            return nuevo_equipo
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Equipos).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(equipo_id):
        db = SessionLocal()
        try:
            return db.query(Equipos).filter(Equipos.id == equipo_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_cliente(cliente_id):
        db = SessionLocal()
        try:
            return db.query(Equipos).filter(Equipos.cliente_id == cliente_id).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_contrato(contrato_id):
        db = SessionLocal()
        try:
            return db.query(Equipos).filter(Equipos.contrato_id == contrato_id).all()
        finally:
            db.close()

    @staticmethod
    def actualizar(equipo_id, sesion=None, **valores):
        db = sesion if sesion is not None else SessionLocal()
        try:
            equipo = db.query(Equipos).filter(Equipos.id == equipo_id).first()
            if not equipo:
                return None
            for campo, valor in valores.items():
                setattr(equipo, campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(equipo)
            else:
                db.flush()
            return equipo
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(equipo_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            equipo = db.query(Equipos).filter(Equipos.id == equipo_id).first()
            if equipo:
                db.delete(equipo)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()