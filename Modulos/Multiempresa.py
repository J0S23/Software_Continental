from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Multiempresa(Base):
    __tablename__ = "multiempresa"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_empresa = Column(String)
    nit = Column(String)
    email = Column(String, nullable=True)
    telefono = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(nombre_empresa, nit, email="", telefono="", direccion=""):
        """Agrega una empresa a la BD"""
        db = SessionLocal()
        nueva_empresa = Multiempresa(
            nombre_empresa=nombre_empresa,
            nit=nit,
            email=email,
            telefono=telefono,
            direccion=direccion
        )
        db.add(nueva_empresa)
        db.commit()
        db.refresh(nueva_empresa)
        db.close()
        return nueva_empresa
    
    @staticmethod
    def obtener_todos():
        """Obtiene todas las empresas"""
        db = SessionLocal()
        empresas = db.query(Multiempresa).all()
        db.close()
        return empresas
    
    @staticmethod
    def obtener_por_id(empresa_id):
        """Obtiene una empresa por ID"""
        db = SessionLocal()
        empresa = db.query(Multiempresa).filter(Multiempresa.id == empresa_id).first()
        db.close()
        return empresa
    
    @staticmethod
    def eliminar(empresa_id):
        """Elimina una empresa por ID"""
        db = SessionLocal()
        empresa = db.query(Multiempresa).filter(Multiempresa.id == empresa_id).first()
        if empresa:
            db.delete(empresa)
            db.commit()
        db.close()
