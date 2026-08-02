from base_de_datos import SessionLocal
from Modulos.Insumos import Insumo


class InsumosRepositorio:
    """CRUD de insumos individuales (unidades de stock); el precio se
    obtiene indirectamente de su TipoInsumo (ver Modulos/Insumos.py)."""

    @staticmethod
    def agregar(tipo_insumo_id, color="", estado="", sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            nuevo_insumo = Insumo(tipo_insumo_id=tipo_insumo_id, color=color, estado=estado)
            db.add(nuevo_insumo)
            if sesion is None:
                db.commit()
                db.refresh(nuevo_insumo)
            else:
                db.flush()
            return nuevo_insumo
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Insumo).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(insumo_id):
        db = SessionLocal()
        try:
            return db.query(Insumo).filter(Insumo.id == insumo_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_tipo(tipo_insumo_id):
        """No existia antes; util para responder 'cuanto stock hay de
        este tipo de insumo' sin traer toda la tabla y filtrar en Python."""
        db = SessionLocal()
        try:
            return db.query(Insumo).filter(Insumo.tipo_insumo_id == tipo_insumo_id).all()
        finally:
            db.close()

    @staticmethod
    def actualizar(insumo_id, sesion=None, **campos):
        db = sesion if sesion is not None else SessionLocal()
        try:
            insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
            if not insumo:
                return None
            for nombre_campo, valor in campos.items():
                setattr(insumo, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(insumo)
            else:
                db.flush()
            return insumo
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(insumo_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            insumo = db.query(Insumo).filter(Insumo.id == insumo_id).first()
            if insumo:
                db.delete(insumo)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def contar_disponibles_agrupado():
        #Devuelve {tipo_insumo_id: cantidad_disponible}, contando solo las unidades con estado 'disponible' (o sin estado). La necesita
        #Servicio/Alertas._alertas_stock para comparar contra TipoInsumo.stock_minimo sin hacer una query por tipo.
        db = SessionLocal()
        try:
            insumos = db.query(Insumo).all()
        finally:
            db.close()

        conteo = {}
        for insumo in insumos:
            estado_normalizado = (insumo.estado or "").strip().lower()
            if estado_normalizado and estado_normalizado != "disponible":
                continue
            conteo[insumo.tipo_insumo_id] = conteo.get(insumo.tipo_insumo_id, 0) + 1
        return conteo