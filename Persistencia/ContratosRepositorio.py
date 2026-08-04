from base_de_datos import SessionLocal
from Modulos.Contratos import Contratos


class ContratosRepositorio:
    """CRUD de contratos comerciales con clientes."""

    @staticmethod
    def agregar(numero_contrato, cliente_id, estado_contrato, tipo_contrato, forma_legalizacion,
        fecha_inicio, fecha_fin=None, poliza_contrato="", poliza_seriedad="", equipo_id=None,
        valor_mensual_base=0, paginas_bn_incluidas=0, paginas_color_incluidas=0,
        valor_pagina_adicional_bn=0, valor_pagina_adicional_color=0,
        escaneos_incluidos=0, valor_escaneo_adicional=0, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            nuevo_contrato = Contratos(
                numero_contrato=numero_contrato, cliente_id=cliente_id,
                estado_contrato=estado_contrato, tipo_contrato=tipo_contrato,
                forma_legalizacion=forma_legalizacion, fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin, poliza_contrato=poliza_contrato,
                poliza_seriedad=poliza_seriedad, equipo_id=equipo_id,
                valor_mensual_base=valor_mensual_base,
                paginas_bn_incluidas=paginas_bn_incluidas,
                paginas_color_incluidas=paginas_color_incluidas,
                valor_pagina_adicional_bn=valor_pagina_adicional_bn,
                valor_pagina_adicional_color=valor_pagina_adicional_color,
                escaneos_incluidos=escaneos_incluidos,
                valor_escaneo_adicional=valor_escaneo_adicional,
            )
            db.add(nuevo_contrato)
            if sesion is None:
                db.commit()
                db.refresh(nuevo_contrato)
            else:
                db.flush()
            return nuevo_contrato
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Contratos).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(contrato_id):
        db = SessionLocal()
        try:
            return db.query(Contratos).filter(Contratos.id == contrato_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_cliente(cliente_id):
        #La necesita Informes_mensuales.informe_por_cliente, que antes hacia esta misma query directo con db.query().
        db = SessionLocal()
        try:
            return db.query(Contratos).filter(Contratos.cliente_id == cliente_id).all()
        finally:
            db.close()

    @staticmethod
    def obtener_activos():
        #La necesita Alertas._alertas_equipos, que antes filtraba estado_contrato == "activo"' directo con db.query().
        db = SessionLocal()
        try:
            return db.query(Contratos).filter(Contratos.estado_contrato == "activo").all()
        finally:
            db.close()

    @staticmethod
    def actualizar(contrato_id, sesion=None, **valores):
        db = sesion if sesion is not None else SessionLocal()
        try:
            contrato = db.query(Contratos).filter(Contratos.id == contrato_id).first()
            if not contrato:
                return None
            for campo, valor in valores.items():
                setattr(contrato, campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(contrato)
            else:
                db.flush()
            return contrato
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(contrato_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            contrato = db.query(Contratos).filter(Contratos.id == contrato_id).first()
            if contrato:
                db.delete(contrato)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()