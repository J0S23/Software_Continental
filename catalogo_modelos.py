from fastapi import HTTPException

from Persistencia.ClientesRepositorio import ClientesRepositorio
from Persistencia.ContratosRepositorio import ContratosRepositorio
from Persistencia.ContratoEquipoRepositorio import ContratoEquipoRepositorio
from Persistencia.CambiosRetiroRepositorio import CambiosRetiroRepositorio
from Persistencia.CostosRepositorio import CostosRepositorio
from Persistencia.EquiposRespaldoRepositorio import EquiposRespaldoRepositorio
from Persistencia.LecturasRepositorio import LecturasRepositorio
from Persistencia.EntregasTonerRepositorio import EntregasTonerRepositorio
from Modulos.enums import (
    EstadoCliente,
    TipoCliente,
    TipoCosto,
    EstadoFactura,
    EmpresaFacturadora,
    RolUsuario,
)
from Persistencia.EquiposRepositorio import EquiposRepositorio
from Persistencia.FacturacionRepositorio import FacturacionRepositorio
from Persistencia.InsumosRepositorio import InsumosRepositorio
from Persistencia.TiposInsumoRepositorio import TiposInsumoRepositorio
from Persistencia.RepuestosRepositorio import RepuestosRepositorio
from Persistencia.ServicioRepositorio import ServicioRepositorio
from Persistencia.UsuariosRepositorio import UsuariosRepositorio


def campo(nombre, etiqueta, tipo="text", opciones=None, requerido=True):
    configuracion = {
        "nombre": nombre,
        "etiqueta": etiqueta,
        "label": etiqueta,
        "tipo": tipo,
        "requerido": requerido,
    }

    if opciones:
        configuracion["opciones"] = opciones

    return configuracion


def opciones_enum(tipo_enum):
    return [item.value for item in tipo_enum]


CATALOGO_DATOS = {
    "clientes": {
        "etiqueta": "Clientes",
        "modelo": ClientesRepositorio,
        "campos": [
            campo("nombre", "Nombre"),
            campo("cliente_id", "Cliente ID"),
            campo("tipo_cliente", "Tipo de cliente", "select", opciones_enum(TipoCliente)),
            campo("estado_cliente", "Estado", "select", opciones_enum(EstadoCliente)),
            campo("condicion_pago", "Condicion de pago"),
            campo("estado_cartera_cliente", "Estado de cartera"),
            campo("telefono", "Telefono", requerido=False),
            campo("celular", "Celular", requerido=False),
            campo("nit", "NIT", requerido=False),
            campo("ciudad", "Ciudad", requerido=False),
            campo("departamento", "Departamento", requerido=False),
            campo("direccion_principal", "Direccion principal", requerido=False),
            campo("correo", "Correo", requerido=False),
            campo("vendedor_comercial", "Vendedor comercial", requerido=False),
        ],
        "enumeraciones": {
            "tipo_cliente": TipoCliente,
            "estado_cliente": EstadoCliente,
        },
    },
    "equipos": {
        "etiqueta": "Equipos",
        "modelo": EquiposRepositorio,
        "campos": [
            campo("numero_serie", "Numero de serie"),
            campo("tipo_equipo", "Tipo de equipo"),
            campo("tecnologia", "Tecnologia"),
            campo("color", "Color"),
            campo("estado_equipo", "Estado del equipo"),
            campo("estado_tecnico", "Estado tecnico"),
            campo("recomendacion_tecnica", "Recomendacion tecnica", requerido=False),
            campo("modelo", "Modelo", requerido=False),
            campo("toner", "Toner", requerido=False),
            campo("rend_orig", "Rendimiento original", "number", requerido=False),
            campo("rend_gen", "Rendimiento generico", "number", requerido=False),
            campo("contador_inicial_bn", "Contador inicial B/N", "number", requerido=False),
            campo("contador_inicial_color", "Contador inicial color", "number", requerido=False),
            campo("cliente_id", "Cliente actual", "number", requerido=False),
            campo("contrato_id", "Contrato actual", "number", requerido=False),
        ],
    },
    "insumos": {
        "etiqueta": "Insumos",
        "modelo": InsumosRepositorio,
        "campos": [
            campo("tipo_insumo_id", "Tipo de insumo", "number"),
            campo("color", "Color", requerido=False),
            campo("estado", "Estado", requerido=False),
        ],
    },
    "tipos_insumo": {
        "etiqueta": "Tipos de insumo",
        "modelo": TiposInsumoRepositorio,
        "campos": [
            campo("nombre", "Nombre"),
            campo("precio", "Precio", "number"),
        ],
    },
    "contratos": {
        "etiqueta": "Contratos",
        "modelo": ContratosRepositorio,
        "campos": [
            campo("numero_contrato", "Numero de contrato"),
            campo("cliente_id", "Cliente", "number"),
            campo("estado_contrato", "Estado del contrato"),
            campo("tipo_contrato", "Tipo de contrato"),
            campo("forma_legalizacion", "Forma de legalizacion"),
            campo("poliza_contrato", "Póliza de contrato", requerido=False),
            campo("poliza_seriedad", "Póliza de seriedad", requerido=False),
            # Legado: contratos nuevos deberian usar el tipo "contrato_equipos" para asociar uno o varios equipos en vez de este campo unico.
            campo("equipo_id", "Equipo (legado, usar 'Equipos por Contrato')", "number", requerido=False),
            campo("fecha_inicio", "Fecha de inicio", "date"),
            campo("fecha_fin", "Fecha de fin", "date", requerido=False),
            campo("valor_mensual_base", "Valor mensual base", "number"),
            campo("paginas_bn_incluidas", "Paginas B/N incluidas", "number"),
            campo("paginas_color_incluidas", "Paginas color incluidas", "number"),
            campo("valor_pagina_adicional_bn", "Valor pagina adicional B/N", "number"),
            campo("valor_pagina_adicional_color", "Valor pagina adicional color", "number"),
            campo("escaneos_incluidos", "Escaneos incluidos", "number", requerido=False),
            campo("valor_escaneo_adicional", "Valor escaneo adicional", "number", requerido=False),
            # "mantenimiento" no se expone: siempre queda Preventivo por defecto (se fija una sola vez).
        ],
    },
    "contrato_equipos": {
        "etiqueta": "Equipos por Contrato",
        "modelo": ContratoEquipoRepositorio,
        "campos": [
            campo("contrato_id", "Contrato", "number"),
            campo("equipo_id", "Equipo", "number"),
            campo("sede", "Sede", requerido=False),
            campo("area_uso", "Area de uso", requerido=False),
            campo("contador_inicial_bn", "Contador inicial B/N", "number", requerido=False),
            campo("contador_inicial_color", "Contador inicial color", "number", requerido=False),
            campo("usuario_responsable", "Usuario responsable", requerido=False),
            campo("observaciones", "Observaciones", requerido=False),
            # "estado_actual" no se expone: crear aqui siempre deja la asignacion en "activo". Para retirar un equipo del contrato
            # (conservando historial), usa ContratoEquipoRepositorio.retirar(), no el PUT generico.
        ],
    },
    "repuestos": {
        "etiqueta": "Repuestos",
        "modelo": RepuestosRepositorio,
        "campos": [
            campo("nombre", "Nombre"),
            campo("precio", "Precio", "number"),
        ],
    },
    "servicios": {
        "etiqueta": "Servicios",
        "modelo": ServicioRepositorio,
        "campos": [
            campo("cliente_id", "Cliente", "number"),
            campo("equipo_id", "Equipo", "number", requerido=False),
            campo("nombre_servicio", "Nombre del servicio"),
            campo("descripcion", "Descripcion", requerido=False),
            campo("precio", "Precio", "number"),
            campo("descripcion_mantenimiento", "Descripcion del mantenimiento", requerido=False),
            campo("repuestos_incluidos", "Repuestos incluidos", requerido=False),
            campo("toner_incluido", "Toner incluido", requerido=False),
            campo("toner_respaldo_sitio", "Toner respaldo sitio", requerido=False),
            campo("equipo_respaldo_incluido", "Equipo respaldo incluido", requerido=False),
            campo("estado", "Estado", requerido=False),
            # "mantenimiento" no se expone: siempre queda Correctivo por defecto.
        ],
    },
    "costos": {
        "etiqueta": "Costos",
        "modelo": CostosRepositorio,
        "campos": [
            campo("fecha_costo", "Fecha del costo", "date"),
            campo("periodo", "Periodo"),
            campo("cliente_id", "Cliente", "number"),
            campo("contrato_id", "Contrato", "number"),
            campo("equipo_id", "Equipo", "number"),
            campo("tipo_costo", "Tipo de costo", "select", opciones_enum(TipoCosto)),
            campo("repuesto_id", "Repuesto", "number", requerido=False),
            campo("descripcion", "Descripcion"),
            campo("cantidad", "Cantidad", "number"),
            campo("valor_unitario", "Valor unitario", "number"),
            campo("valor_total", "Valor total", "number", requerido=False),
            campo("responsable", "Responsable"),
            campo("soporte", "Soporte o documento asociado", requerido=False),
            campo("observaciones", "Observaciones", requerido=False),
        ],
        "enumeraciones": {
            "tipo_costo": TipoCosto,
        },
    },
    "entregas_toner": {
        "etiqueta": "Entregas de Toner",
        "modelo": EntregasTonerRepositorio,
        "campos": [
            campo("fecha_entrega", "Fecha de entrega", "date", requerido=False),
            campo("periodo", "Periodo (MM-YYYY)", requerido=False),
            campo("cliente_id", "Cliente", "number"),
            campo("contrato_id", "Contrato", "number", requerido=False),
            campo("equipo_id", "Equipo", "number"),
            campo("tipo_insumo_id", "Consumible entregado", "number"),
            campo("cantidad", "Cantidad", "number"),
            campo("costo_unitario", "Costo unitario", "number", requerido=False),
            campo("costo_total", "Costo total", "number", requerido=False),
            campo("persona_entrega", "Persona que entrega"),
            campo("persona_recibe", "Persona que recibe", requerido=False),
            campo("motivo", "Motivo de entrega", "select",
                  ["programada", "agotado", "correctivo", "respaldo", "otro"], requerido=False),
            campo("contador_bn", "Contador B/N al momento", "number", requerido=False),
            campo("contador_color", "Contador color al momento", "number", requerido=False),
            campo("observaciones", "Observaciones", requerido=False),
            campo("evidencia_recibido", "Evidencia (ruta/URL)", requerido=False),
        ],
    },
    "facturacion": {
        "etiqueta": "Facturacion",
        "modelo": FacturacionRepositorio,
        "campos": [
            campo("periodo", "Periodo"),
            campo("cliente_id", "Cliente", "number"),
            campo("contrato_id", "Contrato", "number"),
            campo("empresa_factura", "Empresa facturadora", "select", opciones_enum(EmpresaFacturadora)),
            campo("numero_factura", "Numero de factura"),
            campo("fecha_factura", "Fecha de factura", "date"),
            campo("fecha_vencimiento", "Fecha de vencimiento", "date", requerido=False),
            campo("valor_mensual_base", "Valor mensual base", "number"),
            campo("valor_adicionales_bn", "Adicionales blanco y negro", "number", requerido=False),
            campo("valor_adicionales_color", "Adicionales color", "number", requerido=False),
            campo("valor_adicionales_escaneo", "Adicionales escaneo", "number", requerido=False),
            campo("otros_cargos", "Otros cargos", "number", requerido=False),
            campo("subtotal", "Subtotal", "number", requerido=False),
            campo("incluye_iva", "Los valores ya incluyen IVA (1=si, 0=no)", "number", requerido=False),
            campo("porcentaje_iva", "Porcentaje de IVA", "number", requerido=False),
            campo("valor_iva", "Valor IVA", "number", requerido=False),
            campo("impuesto_municipal", "Impuesto municipal", "number", requerido=False),
            campo("impuesto_departamental", "Impuesto departamental", "number", requerido=False),
            campo("impuesto_pro_deporte", "Impuesto pro deporte", "number", requerido=False),
            campo("retenciones", "Retenciones", "number", requerido=False),
            campo("total_facturado", "Total facturado", "number", requerido=False),
            campo("estado_factura", "Estado de la factura", "select", opciones_enum(EstadoFactura)),
            campo("fecha_envio", "Fecha de envio al cliente", "date", requerido=False),
            campo("medio_envio", "Medio de envio", requerido=False),
            campo("observaciones", "Observaciones", requerido=False),
        ],
        "enumeraciones": {
            "empresa_factura": EmpresaFacturadora,
            "estado_factura": EstadoFactura,
        },
    },
    "cambios_retiros": {
    "etiqueta": "Cambios y Retiros",
    "modelo": CambiosRetiroRepositorio,
    "campos": [
        campo("equipo_id", "Equipo", "number"),
        campo("tipo_evento", "Tipo de evento", "select", ["cambio", "retiro"]),
        campo("equipo_reemplazo_id", "Equipo de reemplazo", "number", requerido=False),
        campo("cliente_id", "Cliente", "number", requerido=False),
        campo("contrato_id", "Contrato", "number", requerido=False),
        campo("contador_final", "Contador final", "number", requerido=False),
        campo("motivo", "Motivo"),
        campo("tecnico_responsable", "Tecnico responsable"),
        campo("persona_recibe", "Persona que recibe", requerido=False),
        campo("observaciones", "Observaciones", requerido=False),
    ],
},
    "equipos_respaldo": {
    "etiqueta": "Equipos de Respaldo",
    "modelo": EquiposRespaldoRepositorio,
    "campos": [
        campo("cliente_id", "Cliente", "number"),
        campo("contrato_id", "Contrato", "number", requerido=False),
        campo("equipo_principal_id", "Equipo principal", "number"),
        campo("equipo_respaldo_id", "Equipo de respaldo", "number"),
        campo("motivo", "Motivo"),
        campo("tecnico_responsable", "Tecnico responsable"),
        campo("contador_inicial_respaldo", "Contador inicial", "number", requerido=False),
        campo("fecha_estimada_retiro", "Fecha estimada de retiro", "date", requerido=False),
        campo("costo_asociado", "Costo asociado", "number", requerido=False),
        campo("observaciones", "Observaciones", requerido=False),
    ],
},
    "usuarios": {
        "etiqueta": "Usuarios",
        "modelo": UsuariosRepositorio,
        "campos": [
            campo("nombre_usuario", "Nombre de usuario"),
            campo("email", "Email"),
            campo("rol", "Rol", "select", opciones_enum(RolUsuario)),
            campo("estado", "Estado"),
        ],
        "enumeraciones": {
            "rol": RolUsuario,
        },
    },
    "lecturas": {
        "etiqueta": "Lecturas",
        "modelo": LecturasRepositorio,
        "campos": [
            campo("equipo_id", "Equipo", "number"),
            campo("contrato_id", "Contrato", "number", requerido=False),
            campo("cliente_id", "Cliente", "number", requerido=False),
            campo("periodo", "Periodo (MM-YYYY)", requerido=False),
            campo("medio_lectura", "Medio de lectura", "select",
                  ["presencial", "remota", "reporte_cliente", "sistema", "foto"]),
            campo("estado_lectura", "Estado de lectura", "select",
                  ["pendiente", "registrada", "validada", "observada", "facturada"]),
            campo("contador_bn", "Contador B/N", "number"),
            campo("contador_color", "Contador color", "number"),
        ],
    },
}



def obtener_tipos():
    return {clave: configuracion["etiqueta"] for clave, configuracion in CATALOGO_DATOS.items()}


def obtener_configuracion_frontend():
    return {clave: configuracion["campos"] for clave, configuracion in CATALOGO_DATOS.items()}


def obtener_configuracion_tipo(tipo):
    clave = tipo.lower()

    if clave not in CATALOGO_DATOS:
        raise HTTPException(status_code=404, detail="Tipo de dato no soportado")

    return CATALOGO_DATOS[clave]