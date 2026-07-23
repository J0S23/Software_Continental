from enum import Enum


class TipoCliente(str, Enum):
    """Tipos de clientes en el sistema"""
    PERSONA_NATURAL = "persona_natural"
    EMPRESA_PRIVADA = "empresa_privada"
    ENTIDAD_PUBLICA = "entidad_publica"
    INSTITUCION_EDUCATIVA = "institucion_educativa"
    IPS = "ips"
    OTRO = "otro"


class EstadoCliente(str, Enum):
    """Estados posibles de un cliente"""
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    SUSPENDIDO = "suspendido"
    PROSPECTO = "prospecto"


class TipoCosto(str, Enum):
    """Tipos de costo asociados a un contrato (seccion 11.1 del documento)"""
    TONER = "toner"
    REPUESTO = "repuesto"
    MANO_OBRA = "mano_obra"
    DESPLAZAMIENTO = "desplazamiento"
    FLETE = "flete"
    MANTENIMIENTO_PREVENTIVO = "mantenimiento_preventivo"
    MANTENIMIENTO_CORRECTIVO = "mantenimiento_correctivo"
    EQUIPO_RESPALDO = "equipo_respaldo"
    REPARACION_MAYOR = "reparacion_mayor"
    ACCESORIO = "accesorio"
    DEPRECIACION = "depreciacion"
    OTRO = "otro"