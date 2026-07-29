from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum
from datetime import datetime
from base_de_datos import Base, engine
from Modulos.enums import RolUsuario, EstadoAprobacion


class Usuarios(Base):
    """Solo define columnas. Acceso a datos en Persistencia/UsuariosRepositorio.py."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String)
    email = Column(String)
    password_hash = Column(String)
    rol = Column(SQLEnum(RolUsuario))
    estado = Column(String)
    estado_aprobacion = Column(SQLEnum(EstadoAprobacion), default=EstadoAprobacion.PENDIENTE)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)
    fecha_registro = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)