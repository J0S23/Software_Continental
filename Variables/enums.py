from enum import Enum


class TipoCliente(str, Enum):
    """Tipos de clientes en el sistema"""
    EMPRESA = "Empresa"
    PERSONA = "Persona"
    GOBIERNO = "Gobierno"
    ONG = "ONG"


class EstadoCliente(str, Enum):
    """Estados posibles de un cliente"""
    ACTIVO = "Activo"
    INACTIVO = "Inactivo"
    SUSPENDIDO = "Suspendido"
    PROSPECTO = "Prospecto"
