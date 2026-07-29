# Enumeraciones compartidas por todos los Modulos/*.py y Persistencia/*.py.
# Heredan de str para que se serialicen directo a JSON con su .value.
from enum import Enum
import enum

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


class EstadoFactura(str, Enum):
    """Estados posibles de una factura (seccion 9 del documento)"""
    PENDIENTE = "pendiente"
    ENVIADA = "enviada"
    PAGADA = "pagada"
    VENCIDA = "vencida"
    ANULADA = "anulada"
    EN_RECLAMACION = "en_reclamacion"


class RolUsuario(str, Enum):
    """Roles de usuario del sistema (seccion 20.1 del documento)"""
    ADMINISTRADOR_GENERAL = "Administrador general"
    GERENCIA = "Gerencia"
    SUBGERENCIA_FINANCIERA = "Subgerencia financiera"
    COORDINACION_RENTA = "Coordinación de renta"
    EJECUTIVO_COMERCIAL = "Ejecutivo comercial"
    SERVICIO_TECNICO = "Servicio técnico"
    LOGISTICA_ALMACEN = "Logística / almacén"
    FACTURACION = "Facturación"
    CARTERA = "Cartera"
    CONSULTA_LIMITADA = "Consulta limitada"

class EstadoAprobacion(str, Enum):
    """Estado de aprobacion de una cuenta de usuario"""
    PENDIENTE = "pendiente"
    APROBADO = "aprobado"
    RECHAZADO = "rechazado"

class TipoEquipo(str, enum.Enum):
    """Categoria de equipo fisico (impresora, escaner, etc)."""
    MULTIFUNCIONAL = "multifuncional"
    IMPRESORA = "impresora"
    ESCANER = "escaner"
    PLOTTER = "plotter"
    OTRO = "otro"

class EstadoEquipo(str, enum.Enum):
    """Ciclo de vida del equipo fisico (no confundir con el estado de su asignacion a un contrato)."""
    DISPONIBLE = "disponible"
    INSTALADO = "instalado"
    EN_MANTENIMIENTO = "en_mantenimiento"
    EN_REPARACION = "en_reparacion"
    DE_RESPALDO = "de_respaldo"
    RETIRADO = "retirado"
    DADO_DE_BAJA = "dado_de_baja"


class EmpresaFacturadora(str, Enum):
    """Empresa a nombre de la cual se emite la factura (soporte multiempresa)."""
    CONTINENTAL_LTDA = "Continental Ltda."
    OTRA = "Otra"

class TipoMantenimiento(str, Enum):
    """Tipos de mantenimiento que puede incluir un servicio"""
    PREVENTIVO = "preventivo"
    CORRECTIVO = "correctivo"