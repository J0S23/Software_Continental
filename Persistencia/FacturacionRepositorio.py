from base_de_datos import SessionLocal
from Modulos.Facturacion import Facturacion


class FacturacionRepositorio:
    """CRUD de facturas. agregar() calcula subtotal/IVA/total cuando no
    vienen explicitos, para no obligar al llamador a hacer la aritmetica."""

    @staticmethod
    def agregar(periodo, cliente_id, contrato_id, numero_factura, fecha_factura, estado_factura,
        empresa_factura=None, es_multiempresa=False, fecha_vencimiento=None,
        valor_mensual_base=0, valor_adicionales_bn=0, valor_adicionales_color=0,
        valor_adicionales_escaneo=0, otros_cargos=0, subtotal=None,
        incluye_iva=False, porcentaje_iva=0, valor_iva=None,
        impuesto_municipal=0, impuesto_departamental=0, impuesto_pro_deporte=0,
        retenciones=0, total_facturado=None, fecha_envio=None, medio_envio=None,
        observaciones=None, sesion=None):
        if subtotal is None:
            subtotal = (
                valor_mensual_base + valor_adicionales_bn + valor_adicionales_color
                + valor_adicionales_escaneo + otros_cargos
            )

        if valor_iva is None:
            if incluye_iva:
                # subtotal ya incluye IVA: se extrae el IVA implicito (formula inversa).
                valor_iva = subtotal - (subtotal / (1 + porcentaje_iva / 100)) if porcentaje_iva else 0
            else:
                # subtotal no incluye IVA: se calcula y se suma aparte.
                valor_iva = subtotal * (porcentaje_iva / 100) if porcentaje_iva else 0

        if total_facturado is None:
            # Si incluye_iva, subtotal ya trae el IVA adentro; si no, hay que sumarlo.
            base_con_iva = subtotal if incluye_iva else subtotal + valor_iva
            total_facturado = (
                base_con_iva + impuesto_municipal + impuesto_departamental
                + impuesto_pro_deporte - retenciones
            )

        db = sesion if sesion is not None else SessionLocal()
        try:
            nueva_factura = Facturacion(
                periodo=periodo, cliente_id=cliente_id, contrato_id=contrato_id,
                empresa_factura=empresa_factura, es_multiempresa=es_multiempresa,
                numero_factura=numero_factura, fecha_factura=fecha_factura,
                fecha_vencimiento=fecha_vencimiento, valor_mensual_base=valor_mensual_base,
                valor_adicionales_bn=valor_adicionales_bn, valor_adicionales_color=valor_adicionales_color,
                valor_adicionales_escaneo=valor_adicionales_escaneo, otros_cargos=otros_cargos,
                subtotal=subtotal, incluye_iva=incluye_iva, porcentaje_iva=porcentaje_iva,
                valor_iva=valor_iva, impuesto_municipal=impuesto_municipal,
                impuesto_departamental=impuesto_departamental, impuesto_pro_deporte=impuesto_pro_deporte,
                retenciones=retenciones, total_facturado=total_facturado,
                estado_factura=estado_factura, fecha_envio=fecha_envio, medio_envio=medio_envio,
                observaciones=observaciones,
            )
            db.add(nueva_factura)
            if sesion is None:
                db.commit()
                db.refresh(nueva_factura)
            else:
                db.flush()
            return nueva_factura
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Facturacion).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(factura_id):
        db = SessionLocal()
        try:
            return db.query(Facturacion).filter(Facturacion.id == factura_id).first()
        finally:
            db.close()

    @staticmethod
    def obtener_por_contrato(contrato_id, periodo=None):
        db = SessionLocal()
        try:
            query = db.query(Facturacion).filter(Facturacion.contrato_id == contrato_id)
            if periodo:
                query = query.filter(Facturacion.periodo == periodo)
            return query.all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_periodo(periodo):
        """La necesitan Informes_mensuales.informe_general/informe_cartera
        y Dashboard.serie_cartera_por_edad, que antes filtraban periodo
        directo con db.query()."""
        db = SessionLocal()
        try:
            return db.query(Facturacion).filter(Facturacion.periodo == periodo).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_cliente(cliente_id, periodo=None):
        """La necesita Informes_mensuales.informe_por_cliente."""
        db = SessionLocal()
        try:
            query = db.query(Facturacion).filter(Facturacion.cliente_id == cliente_id)
            if periodo:
                query = query.filter(Facturacion.periodo == periodo)
            return query.all()
        finally:
            db.close()

    @staticmethod
    def actualizar(factura_id, sesion=None, **campos):
        db = sesion if sesion is not None else SessionLocal()
        try:
            factura = db.query(Facturacion).filter(Facturacion.id == factura_id).first()
            if not factura:
                return None
            for nombre_campo, valor in campos.items():
                setattr(factura, nombre_campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(factura)
            else:
                db.flush()
            return factura
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(factura_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            factura = db.query(Facturacion).filter(Facturacion.id == factura_id).first()
            if factura:
                db.delete(factura)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()