from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, SessionLocal, engine


class Lecturas(Base):
    __tablename__ = "lecturas"
    
    id = Column(Integer, primary_key=True, index=True)
    equipo_id = Column(Integer)
    #Atributos que permiten saber las lecturas de un contrato en un periodo
    contrato_id = Column(Integer, nullable=True)
    cliente_id = Column(Integer, nullable=True)
    periodo = Column(String, nullable=True)
    medio_lectura = Column(String)
    estado_lectura = Column(String)
    #Dos contadores para separar entre blanco y negro y color
    contador_bn = Column(Integer, default=0)
    contador_color = Column(Integer, default=0)
    fecha_lectura = Column(DateTime, default=datetime.utcnow)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    
    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)
    
    @staticmethod
    def agregar(equipo_id, medio_lectura, estado_lectura,
        contador_bn=0, contador_color=0,
        contrato_id=None, cliente_id=None, periodo=None,
        fecha_lectura=None,):
        """Agrega una lectura a la BD"""
        db = SessionLocal()
        nueva_lectura = Lecturas(
            equipo_id=equipo_id,
            medio_lectura=medio_lectura,
            estado_lectura=estado_lectura,
            contador_bn=contador_bn,
            contador_color=contador_color,
            contrato_id=contrato_id,
            cliente_id=cliente_id,
            periodo=periodo,
            fecha_lectura=fecha_lectura or datetime.utcnow()
        )
        db.add(nueva_lectura)
        db.commit()
        db.refresh(nueva_lectura)
        db.close()
        return nueva_lectura
    
    @staticmethod
    def obtener_todos():
        """Obtiene todas las lecturas"""
        db = SessionLocal()
        lecturas = db.query(Lecturas).all()
        db.close()
        return lecturas
    
    @staticmethod
    def obtener_por_id(lectura_id):
        """Obtiene una lectura por ID"""
        db = SessionLocal()
        lectura = db.query(Lecturas).filter(Lecturas.id == lectura_id).first()
        db.close()
        return lectura
    
    @staticmethod
    def eliminar(lectura_id):
        """Elimina una lectura por ID"""
        db = SessionLocal()
        lectura = db.query(Lecturas).filter(Lecturas.id == lectura_id).first()
        if lectura:
            db.delete(lectura)
            db.commit()
        db.close()
