from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from datetime import datetime
from base_de_datos import Base, engine


class Adjunto(Base):
    #Tabla generica de archivos/evidencias asociados a cualquier entidad del sistema (clientes, equipos, contratos, lecturas, facturacion, etc).

    #El archivo fisico se guarda en configuracion.RUTA_ADJUNTOS con un nombre generado (uuid4 + extension original) para evitar colisiones y problemas
    #de path traversal; nombre_original conserva el nombre que subio el usuario solo para mostrarlo en el frontend.
    
    __tablename__ = "adjuntos"

    id = Column(Integer, primary_key=True, index=True)
    tipo_entidad = Column(String, nullable=False, index=True)
    entidad_id = Column(Integer, nullable=False, index=True)
    tipo_documento = Column(String, nullable=True)
    nombre_original = Column(String, nullable=False)
    nombre_archivo = Column(String, nullable=False, unique=True)
    content_type = Column(String, nullable=True)
    tamano_bytes = Column(BigInteger, nullable=True)
    subido_por = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)
    fecha_subida = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)