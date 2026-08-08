from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class Sedes(Base):
    #Sede, dependencia o ubicacion donde estan instalados los equipos de un cliente. Un mismo cliente puede tener varias sedes (soporte multisede).

    __tablename__ = "sedes"

    id = Column(Integer, primary_key=True, index=True)

    # A que cliente pertenece esta sede. Sin ForeignKey a proposito, mismo patron que cliente_id/contrato_id/equipo_id en el resto
    # del proyecto (ver Modulos/Costos.py, Modulos/Lecturas.py, etc).
    
    cliente_id = Column(Integer, nullable=False, index=True)

    codigo_sede = Column(String, nullable=True)
    nombre_sede = Column(String, nullable=False)

    ciudad = Column(String, nullable=True)
    departamento = Column(String, nullable=True)
    direccion = Column(String, nullable=True)
    piso_oficina_area = Column(String, nullable=True)

    persona_responsable = Column(String, nullable=True)
    telefono_contacto = Column(String, nullable=True)
    correo_contacto = Column(String, nullable=True)
    horario_atencion = Column(String, nullable=True)

    condiciones_ingreso = Column(String, nullable=True)
    observaciones_acceso = Column(String, nullable=True)

    # activa | inactiva | cerrada
    estado_sede = Column(String, default="activa", nullable=False)

    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)