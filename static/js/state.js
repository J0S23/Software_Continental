// Estado global de la SPA y reglas de permisos.
//
// La matriz de permisos de abajo es un espejo exacto de Modulos/Permisos.py
// (la fuente de verdad vive en el backend, que además la vuelve a exigir en
// cada POST/PUT/DELETE). Reglas fijas documentadas ahí:
//   - Lectura: cualquier usuario logueado, para cualquier tipo. Por eso el
//     menú principal no oculta vistas por rol (excepto "usuarios", que sí
//     exige Administrador general en el propio backend).
//   - Eliminar: solo Administrador general, sin excepción.
//   - "usuarios": solo Administrador general puede crear/editar.
//   - Cualquier otro tipo que no aparezca en PERMISOS_CREAR_EDITAR (hoy solo
//     "cartera") queda cerrado a no-administradores: falla cerrado.

const ADMIN_ROLE = "Administrador general";

const ROLE_OPTIONS = [
    "Administrador general",
    "Gerencia",
    "Subgerencia financiera",
    "Coordinación de renta",
    "Ejecutivo comercial",
    "Servicio técnico",
    "Logística / almacén",
    "Facturación",
    "Cartera",
    "Consulta limitada",
];

const HIDDEN_DATA_TYPES = new Set(["usuarios"]);
const IMPORTABLE_TYPES = new Set([
    "clientes", "sedes", "equipos", "contrato_equipos", "lecturas", "contratos",
    "facturacion", "costos", "cartera", "rentabilidad",
    "mantenimientos_preventivos", "servicios", "cambios_retiros", "equipos_respaldo",
    "tipos_insumo", "insumos", "entregas_toner", "repuestos",
]);

const TIPOS_SOLO_ADMIN_ESCRITURA = new Set(["usuarios"]);

const PERMISOS_CREAR_EDITAR = {
    clientes: ["Coordinación de renta", "Ejecutivo comercial"],
    sedes: ["Coordinación de renta", "Ejecutivo comercial"],
    equipos: ["Coordinación de renta", "Servicio técnico"],
    contrato_equipos: ["Coordinación de renta"],
    contratos: ["Coordinación de renta", "Ejecutivo comercial"],
    cambios_retiros: ["Servicio técnico"],
    equipos_respaldo: ["Servicio técnico"],
    lecturas: ["Coordinación de renta", "Servicio técnico"],
    servicios: ["Servicio técnico"],
    mantenimientos_preventivos: ["Servicio técnico"],
    repuestos: ["Logística / almacén", "Servicio técnico"],
    insumos: ["Logística / almacén"],
    tipos_insumo: ["Logística / almacén"],
    entregas_toner: ["Logística / almacén", "Servicio técnico"],
    costos: ["Subgerencia financiera", "Servicio técnico", "Logística / almacén"],
    facturacion: ["Facturación", "Subgerencia financiera"],
    rentabilidad: ["Subgerencia financiera"],
};

function puedeEscribir(tipo, rol) {
    if (rol === ADMIN_ROLE) return true;
    if (TIPOS_SOLO_ADMIN_ESCRITURA.has(tipo)) return false;
    const permitidos = PERMISOS_CREAR_EDITAR[tipo];
    return Boolean(permitidos && permitidos.includes(rol));
}

function puedeEliminar(rol) {
    return rol === ADMIN_ROLE;
}

function vistaPermitida(view) {
    if (view === "usuarios") return state.usuario?.rol === ADMIN_ROLE;
    return Boolean(state.usuario);
}

// Los 4 grupos del catálogo de datos: cada uno tiene su propio item del
// menú, pero comparten la misma plantilla de "workspace" (#view-datos).
const DATA_GROUP_VIEWS = [
    { view: "base_comercial", title: "Base comercial", eyebrow: "Clientes y contratos", keys: ["clientes", "sedes", "contratos", "contrato_equipos", "equipos"] },
    { view: "operacion_mensual", title: "Operación mensual", eyebrow: "Lecturas y facturación", keys: ["lecturas", "facturacion", "cartera", "costos", "rentabilidad"] },
    { view: "servicio_tecnico", title: "Servicio técnico", eyebrow: "Mantenimiento y soporte", keys: ["servicios", "mantenimientos_preventivos", "cambios_retiros", "equipos_respaldo"] },
    { view: "inventario", title: "Inventario", eyebrow: "Insumos y repuestos", keys: ["tipos_insumo", "insumos", "entregas_toner", "repuestos"] },
];

const VIEW_META = {
    dashboard: { title: "Visión general", eyebrow: "Principal" },
    informes: { title: "Informes", eyebrow: "Gerencia" },
    alertas: { title: "Alertas", eyebrow: "Seguimiento" },
    usuarios: { title: "Usuarios", eyebrow: "Administración" },
};
DATA_GROUP_VIEWS.forEach((grupo) => {
    VIEW_META[grupo.view] = { title: grupo.title, eyebrow: grupo.eyebrow };
});

function grupoPorVista(view) {
    return DATA_GROUP_VIEWS.find((grupo) => grupo.view === view) || null;
}

function tiposDelGrupo(grupo) {
    return grupo.keys.filter((key) => state.tipos[key] && !HIDDEN_DATA_TYPES.has(key));
}

const state = {
    tipos: {},
    configuracion: {},
    tipoActual: "",
    registros: [],
    skip: 0,
    total: 0,
    editingId: null,
    usuario: null,
    currentView: "dashboard",
    currentAdjuntoTarget: null,
    lastFacturaPreview: null,
    facturaPreviewKey: null,
    alertas: [],
    alertasMeta: null,
    charts: {
        financial: null, costs: null, cartera: null,
        ingresosCliente: null, rentabilidadCliente: null, correctivosEquipo: null, toneresCliente: null,
        informeComposicion: null, margenTendencia: null, carteraPorEstado: null,
        preventivosPorEstado: null, equiposConFallas: null, repuestosMasUsados: null, costosTecnicosPorContrato: null,
    },
};
