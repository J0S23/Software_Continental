from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Rentabilidad(Base):
    __tablename__ = "rentabilidad"
    
    id = Column(Integer, primary_key=True, index=True)
    periodo = Column(String)
    #Atributos que permiten guardar rentabilidad por contrato
    contrato_id = Column(Integer, nullable=True)
    cliente_id = Column(Integer, nullable=True)
    ingresos = Column(Float, default=0)
    costos = Column(Float, default=0)
    ganancia = Column(Float, default=0)
    porcentaje_rentabilidad = Column(Float, default=0)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(periodo, ingresos=0, costos=0, ganancia=0, porcentaje_rentabilidad=0,
                contrato_id=None, cliente_id=None):
        """Agrega un registro de rentabilidad a la BD"""
        db = SessionLocal()
        nuevo_registro = Rentabilidad(
            periodo=periodo,
            contrato_id=contrato_id,
            cliente_id=cliente_id,
            ingresos=ingresos,
            costos=costos,
            ganancia=ganancia,
            porcentaje_rentabilidad=porcentaje_rentabilidad,
        )
        db.add(nuevo_registro)
        db.commit()
        db.refresh(nuevo_registro)
        db.close()
        return nuevo_registro
    
    @staticmethod
    def obtener_todos():
        """Obtiene todos los registros de rentabilidad"""
        db = SessionLocal()
        registros = db.query(Rentabilidad).all()
        db.close()
        return registros
    
    @staticmethod
    def obtener_por_id(rentabilidad_id):
        """Obtiene un registro de rentabilidad por ID"""
        db = SessionLocal()
        registro = db.query(Rentabilidad).filter(Rentabilidad.id == rentabilidad_id).first()
        db.close()
        return registro

    def obtener_por_contrato(contrato_id, periodo=None):
        #Metodo que necesita la rentabilidad automatica para saber si ya
        #existe un calculo de este contrato en este periodo
        db = SessionLocal()
        query = db.query(Rentabilidad).filter(Rentabilidad.contrato_id == contrato_id)
        if periodo:
            query = query.filter(Rentabilidad.periodo == periodo)
        registros = query.all()
        db.close()
        return registros
    
    @staticmethod
    def eliminar(rentabilidad_id):
        """Elimina un registro de rentabilidad por ID"""
        db = SessionLocal()
        registro = db.query(Rentabilidad).filter(Rentabilidad.id == rentabilidad_id).first()
        if registro:
            db.delete(registro)
            db.commit()
        db.close()
