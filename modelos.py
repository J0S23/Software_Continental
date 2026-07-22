# archivo: models/equipo.py
import enum
from sqlalchemy import Column, Integer, String, Boolean, Enum as SQLEnum
from database import Base


class TipoEquipo(str, enum.Enum):
    MULTIFUNCIONAL = "multifuncional"
    IMPRESORA = "impresora"
    ESCANER = "escaner"
    PLOTTER = "plotter"
    OTRO = "otro"


class EstadoEquipo(str, enum.Enum):
    DISPONIBLE = "disponible"
    INSTALADO = "instalado"
    EN_MANTENIMIENTO = "en_mantenimiento"
    EN_REPARACION = "en_reparacion"
    DE_RESPALDO = "de_respaldo"
    RETIRADO = "retirado"
    DADO_DE_BAJA = "dado_de_baja"