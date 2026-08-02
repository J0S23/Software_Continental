from base_de_datos import SessionLocal
from Modulos.Clientes import Clientes


class ClientesRepositorio:
    """CRUD de clientes. Expuesto via el catalogo generico en catalogo_modelos.py."""

    @staticmethod
    def agregar(
        tipo_cliente, estado_cliente, condicion_pago, estado_cartera_cliente,
        nombre, cliente_id, telefono=None, celular=None, nit=None, ciudad=None,
        departamento=None, direccion_principal=None, correo=None,
        vendedor_comercial=None, multiempresa=None, sesion=None,
    ):
        db = sesion if sesion is not None else SessionLocal()
        try:
            nuevo_cliente = Clientes(
                tipo_cliente=tipo_cliente, estado_cliente=estado_cliente,
                condicion_pago=condicion_pago, estado_cartera_cliente=estado_cartera_cliente,
                multiempresa=multiempresa, nombre=nombre, cliente_id=cliente_id,
                telefono=telefono, celular=celular, nit=nit, ciudad=ciudad,
                departamento=departamento, direccion_principal=direccion_principal,
                correo=correo, vendedor_comercial=vendedor_comercial,
            )
            db.add(nuevo_cliente)
            if sesion is None:
                db.commit()
                db.refresh(nuevo_cliente)
            else:
                db.flush()
            return nuevo_cliente
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def obtener_todos():
        db = SessionLocal()
        try:
            return db.query(Clientes).all()
        finally:
            db.close()

    @staticmethod
    def obtener_por_id(cliente_id):
        db = SessionLocal()
        try:
            return db.query(Clientes).filter(Clientes.id == cliente_id).first()
        finally:
            db.close()

    @staticmethod
    def actualizar(cliente_id, sesion=None, **valores):
        db = sesion if sesion is not None else SessionLocal()
        try:
            cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()
            if not cliente:
                return None
            for campo, valor in valores.items():
                setattr(cliente, campo, valor)
            if sesion is None:
                db.commit()
                db.refresh(cliente)
            else:
                db.flush()
            return cliente
        finally:
            if sesion is None:
                db.close()

    @staticmethod
    def eliminar(cliente_id, sesion=None):
        db = sesion if sesion is not None else SessionLocal()
        try:
            cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()
            if cliente:
                db.delete(cliente)
                if sesion is None:
                    db.commit()
                else:
                    db.flush()
                return True
            return False
        finally:
            if sesion is None:
                db.close()