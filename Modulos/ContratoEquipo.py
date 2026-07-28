from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from base_de_datos import Base, engine


class ContratoEquipo(Base):
    #Tabla intermediaria contrato-equipo permite que un contrato tenga uno o varios equipos asociados, cada uno con su propia informacion de instalacion.

    #Un mismo equipo puede tener varias filas a lo largo del tiempo (una por cada contrato en el que estuvo instalado),
    #pero solo debe tener una fila con estado_actual="activo" a la vez -- eso se valida en ContratoEquipoRepositorio.agregar(),
    # no aqui a nivel de columna,porque SQLite no soporta un constraint condicional simple para eso.

    #Equipos.contrato_id se mantiene como cache del contrato activo actual del equipo (lo sincroniza ContratoEquipoRepositorio),
    #util para queries rapidas que no necesitan el historial completo. La fuente de verdad para "que equipos tiene este contrato"
    #y para el historial de instalaciones/retiros es siempre esta tabla, no Equipos.contrato_id ni Contratos.equipo_id 
    # este ultimo queda como campo legado
    

    __tablename__ = "contrato_equipos"

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, nullable=False)
    equipo_id = Column(Integer, nullable=False)
    sede = Column(String, nullable=True)
    area_uso = Column(String, nullable=True)
    contador_inicial_bn = Column(Integer, default=0)
    contador_inicial_color = Column(Integer, default=0)
    usuario_responsable = Column(String, nullable=True)
    observaciones = Column(String, nullable=True)
    # Ciclo de vida de la asignacion, no del equipo fisico (ese usa
    # Equipos.estado_equipo, via EquiposRepositorio). Valores: "activo" | "retirado"
    estado_actual = Column(String, default="activo", nullable=False)
    fecha_instalacion = Column(DateTime, default=datetime.utcnow)
    fecha_retiro = Column(DateTime, nullable=True)
    fecha_creacion = Column(DateTime, default=datetime.utcnow)

    @staticmethod
    def crear_tabla():
        Base.metadata.create_all(bind=engine)