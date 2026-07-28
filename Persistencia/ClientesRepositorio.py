from base_de_datos import SessionLocal
from Modulos.Clientes import Clientes


class ClientesRepositorio:

    @staticmethod
    def agregar(
        tipo_cliente, estado_cliente, condicion_pago, estado_cartera_cliente,
        nombre, cliente_id, telefono=None, celular=None, nit=None, ciudad=None,
        departamento=None, direccion_principal=None, correo=None,
        vendedor_comercial=None, multiempresa=None,
    ):
        db = SessionLocal()
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
            db.commit()
            db.refresh(nuevo_cliente)
            return nuevo_cliente
        finally:
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
    def actualizar(cliente_id, **valores):
        db = SessionLocal()
        try:
            cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()
            if not cliente:
                return None
            for campo, valor in valores.items():
                setattr(cliente, campo, valor)
            db.commit()
            db.refresh(cliente)
            return cliente
        finally:
            db.close()

    @staticmethod
    def eliminar(cliente_id):
        db = SessionLocal()
        try:
            cliente = db.query(Clientes).filter(Clientes.id == cliente_id).first()
            if cliente:
                db.delete(cliente)
                db.commit()
                return True
            return False
        finally:
            db.close()