const PAGE_SIZE = 100;
const ADMIN_ROLE = "Administrador general";
const IMPORTABLE_TYPES = new Set(["clientes", "equipos", "lecturas"]);
const HIDDEN_DATA_TYPES = new Set(["usuarios"]);

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

// Los 4 grupos del catálogo de datos, cada uno con su propio item del
// .main-nav (data-view). Comparten la misma plantilla data-workspace:
// cambiarVista() solo pre-filtra qué tipos quedan disponibles en cada uno.
const DATA_GROUP_VIEWS = [
    { view: "base_comercial", title: "Base comercial", keys: ["clientes", "sedes", "contratos", "contrato_equipos", "equipos"] },
    { view: "operacion_mensual", title: "Operación mensual", keys: ["lecturas", "facturacion", "cartera", "costos", "rentabilidad"] },
    { view: "servicio_tecnico", title: "Servicio técnico", keys: ["servicios", "mantenimientos_preventivos", "cambios_retiros", "equipos_respaldo"] },
    { view: "inventario", title: "Inventario", keys: ["tipos_insumo", "insumos", "entregas_toner", "repuestos"] },
];

const VIEW_META = {
    dashboard: { title: "Visión general", eyebrow: "Administrador general" },
    base_comercial: { title: "Base comercial", eyebrow: "Clientes y contratos" },
    operacion_mensual: { title: "Operación mensual", eyebrow: "Lecturas y facturación" },
    servicio_tecnico: { title: "Servicio técnico", eyebrow: "Mantenimiento y soporte" },
    inventario: { title: "Inventario", eyebrow: "Insumos y repuestos" },
    informes: { title: "Informes", eyebrow: "Gerencia" },
    alertas: { title: "Alertas", eyebrow: "Seguimiento" },
    usuarios: { title: "Usuarios", eyebrow: "Administración" },
};

// Mapa de permisos por rol (documento de requerimientos, seccion 20.2).
// views: vistas del .main-nav visibles para el rol.
// modules: claves de state.tipos habilitadas dentro de los 4 grupos de datos
//          (null = todas). readOnly: oculta crear/editar/eliminar/importar.
const ROLE_PERMISSIONS = {
    [ADMIN_ROLE]: { views: ["dashboard", "base_comercial", "operacion_mensual", "servicio_tecnico", "inventario", "informes", "alertas", "usuarios"], modules: null, readOnly: false },
    "Gerencia": { views: ["dashboard", "base_comercial", "operacion_mensual", "servicio_tecnico", "inventario", "informes", "alertas"], modules: null, readOnly: true },
    "Subgerencia financiera": { views: ["dashboard", "base_comercial", "operacion_mensual", "informes", "alertas"], modules: ["contratos", "facturacion", "cartera", "costos", "rentabilidad"], readOnly: false },
    "Coordinación de renta": { views: ["dashboard", "base_comercial", "operacion_mensual", "informes"], modules: ["clientes", "sedes", "contratos", "contrato_equipos", "equipos", "lecturas", "facturacion"], readOnly: false },
    "Ejecutivo comercial": { views: ["dashboard", "base_comercial", "informes"], modules: ["clientes", "sedes", "contratos", "contrato_equipos", "equipos"], readOnly: false },
    "Servicio técnico": { views: ["dashboard", "base_comercial", "servicio_tecnico"], modules: ["servicios", "mantenimientos_preventivos", "cambios_retiros", "equipos_respaldo", "equipos"], readOnly: false },
    "Logística / almacén": { views: ["dashboard", "inventario"], modules: ["tipos_insumo", "insumos", "entregas_toner", "repuestos"], readOnly: false },
    "Facturación": { views: ["dashboard", "operacion_mensual", "informes"], modules: ["facturacion", "cartera"], readOnly: false },
    "Cartera": { views: ["dashboard", "base_comercial", "operacion_mensual", "informes", "alertas"], modules: ["cartera", "clientes"], readOnly: false },
    "Consulta limitada": { views: ["dashboard", "base_comercial", "operacion_mensual", "servicio_tecnico", "inventario", "informes", "alertas"], modules: null, readOnly: true },
};

function grupoPorVista(view) {
    return DATA_GROUP_VIEWS.find((grupo) => grupo.view === view) || null;
}

function clavesDisponibles(grupo) {
    return grupo.keys.filter((key) => state.tipos[key] && !HIDDEN_DATA_TYPES.has(key) && moduloPermitido(key));
}

function permisosRol() {
    return ROLE_PERMISSIONS[state.usuario?.rol] || ROLE_PERMISSIONS[ADMIN_ROLE];
}

function vistaPermitida(view) {
    return permisosRol().views.includes(view);
}

function moduloPermitido(key) {
    const permisos = permisosRol();
    return !permisos.modules || permisos.modules.includes(key);
}

function esSoloLectura() {
    return Boolean(permisosRol().readOnly);
}

function aplicarPermisosRol() {
    document.querySelectorAll(".nav-item").forEach((button) => {
        button.hidden = !vistaPermitida(button.dataset.view);
    });
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
    charts: {
        financial: null, costs: null, cartera: null,
        ingresosCliente: null, rentabilidadCliente: null, correctivosEquipo: null, toneresCliente: null,
    },
};

document.addEventListener("DOMContentLoaded", () => {
    setDefaultPeriod();
    bindStaticEvents();
    verificarSesion();
});

function $(id) {
    return document.getElementById(id);
}

function bind(id, eventName, handler) {
    const element = $(id);
    if (element) {
        element.addEventListener(eventName, handler);
    }
}

function bindStaticEvents() {
    bind("loginForm", "submit", iniciarSesion);
    bind("logoutBtn", "click", cerrarSesion);
    bind("refreshBtn", "click", refrescarVistaActual);
    bind("periodInput", "change", () => {
        syncAutomationPeriod();
        refrescarVistaActual();
    });

    document.querySelectorAll(".nav-item").forEach((button) => {
        button.addEventListener("click", () => cambiarVista(button.dataset.view));
    });

    bind("tipoSelector", "change", (event) => seleccionarTipo(event.target.value));
    bind("formDatos", "submit", guardarRegistro);
    bind("resetFormBtn", "click", limpiarFormulario);
    bind("cancelEditBtn", "click", limpiarFormulario);
    bind("recordSearch", "input", renderTabla);
    bind("paginaAnteriorBtn", "click", irPaginaAnterior);
    bind("paginaSiguienteBtn", "click", irPaginaSiguiente);
    bind("exportCurrentBtn", "click", exportarTipoActual);
    bind("downloadTemplateBtn", "click", descargarPlantilla);
    bind("importBtn", "click", importarExcel);

    bind("loadReportsBtn", "click", cargarInformes);
    bind("loadClientReportBtn", "click", cargarInformeCliente);
    bind("loadEquipoReportBtn", "click", cargarInformeEquipo);
    bind("loadAlertsBtn", "click", cargarAlertas);
    bind("includeDiscardedFilter", "change", cargarAlertas);
    bind("alertLevelFilter", "change", renderAlertasActivas);
    bind("loadUsersBtn", "click", cargarUsuarios);

    bind("closeAdjuntosBtn", "click", cerrarAdjuntos);
    bind("adjuntosForm", "submit", subirAdjunto);
    bind("closeHistoryBtn", "click", cerrarHistorial);

    bind("previewFacturaBtn", "click", previsualizarFacturacion);
    bind("generarFacturaBtn", "click", generarFacturacionAutomatica);
    bind("autoContratoId", "input", resetFacturaPreview);
    bind("autoPeriodo", "input", resetFacturaPreview);
}

function setDefaultPeriod() {
    const today = new Date();
    const periodo = `${String(today.getMonth() + 1).padStart(2, "0")}-${today.getFullYear()}`;
    $("periodInput").value = periodo;
}

function periodoActual() {
    const value = $("periodInput").value.trim();
    return value || `${String(new Date().getMonth() + 1).padStart(2, "0")}-${new Date().getFullYear()}`;
}

async function apiJson(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options,
        headers: {
            ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
            ...(options.headers || {}),
        },
    });

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
        ? await response.json()
        : { detail: await response.text() };

    if (!response.ok || data.success === false) {
        throw new Error(data.detail || data.error || "No se pudo completar la operación");
    }

    return data;
}

async function verificarSesion() {
    try {
        const data = await apiJson("/auth/me");
        await mostrarApp(data.usuario);
    } catch (error) {
        mostrarAuth();
    }
}

async function iniciarSesion(event) {
    event.preventDefault();
    setAuthMessage("");

    const email = $("loginEmail").value.trim();
    const contrasena = $("loginPassword").value;

    try {
        const data = await apiJson("/auth/login", {
            method: "POST",
            body: JSON.stringify({ email, contrasena }),
        });

        await mostrarApp({ email: data.email, rol: data.rol });
        mostrarToast("Sesión iniciada", "success");
    } catch (error) {
        setAuthMessage(error.message);
    }
}

async function cerrarSesion(callApi = true) {
    if (callApi) {
        await apiJson("/auth/logout", { method: "POST" }).catch(() => null);
    }
    state.usuario = null;
    mostrarAuth();
}

function mostrarAuth(message = "") {
    $("authScreen").hidden = false;
    $("appShell").hidden = true;
    setAuthMessage(message);
}

async function mostrarApp(usuario) {
    state.usuario = usuario;
    $("authScreen").hidden = true;
    $("appShell").hidden = false;
    $("userRoleLabel").textContent = usuario.rol || ADMIN_ROLE;
    $("userEmailLabel").textContent = usuario.email || "";

    aplicarPermisosRol();
    await cargarConfiguracionInicial();
    const vistaInicial = vistaPermitida(state.currentView) ? state.currentView : permisosRol().views[0];
    cambiarVista(vistaInicial || "dashboard");
}

function setAuthMessage(message) {
    const box = $("authMessage");
    if (!box) return;
    box.hidden = !message;
    box.textContent = message || "";
}

async function cargarConfiguracionInicial() {
    if (Object.keys(state.tipos).length) return;

    try {
        const [tipos, configuracion] = await Promise.all([
            apiJson("/api/tipos"),
            apiJson("/api/configuracion"),
        ]);
        state.tipos = tipos;
        state.configuracion = configuracion;
    } catch (error) {
        mostrarToast(`No se pudo cargar la configuración: ${error.message}`, "error");
    }
}

function renderTipos(grupo) {
    const selector = $("tipoSelector");
    const groupsContainer = $("tipoGroups");
    selector.replaceChildren(new Option("Selecciona módulo", ""));
    groupsContainer.replaceChildren();

    if (!grupo) return;
    const keys = clavesDisponibles(grupo);
    if (!keys.length) return;

    const section = document.createElement("section");
    section.className = "module-group";
    const title = document.createElement("h3");
    title.textContent = grupo.title;
    section.appendChild(title);

    keys.forEach((key) => {
        selector.appendChild(new Option(state.tipos[key], key));
        section.appendChild(crearModuloButton(key));
    });

    groupsContainer.appendChild(section);
}

function crearModuloButton(key) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "module-button";
    button.dataset.tipo = key;
    const label = document.createElement("span");
    label.textContent = state.tipos[key];
    const code = document.createElement("small");
    code.textContent = key;
    button.append(label, code);
    button.addEventListener("click", () => seleccionarTipo(key));
    return button;
}

async function seleccionarTipo(tipo) {
    state.tipoActual = tipo || "";
    state.skip = 0;
    state.editingId = null;
    state.registros = [];
    state.total = 0;
    $("tipoSelector").value = state.tipoActual;

    document.querySelectorAll(".module-button").forEach((button) => {
        button.classList.toggle("active", button.dataset.tipo === state.tipoActual);
    });

    renderFormulario();
    renderTabla();
    actualizarControlesImportacion();
    syncAutomationPanel();

    if (state.tipoActual) {
        await obtenerDatos();
    }
}

function renderFormulario() {
    const fields = $("formFields");
    fields.replaceChildren();
    $("formTitle").textContent = state.tipoActual ? state.tipos[state.tipoActual] : "Selecciona un tipo";
    $("formModeLabel").textContent = state.editingId ? `Editando #${state.editingId}` : "Nuevo registro";

    const soloLectura = esSoloLectura();
    document.querySelector(".editor-panel")?.toggleAttribute("hidden", soloLectura);
    if (soloLectura) return;

    $("saveRecordBtn").disabled = !state.tipoActual;
    $("cancelEditBtn").hidden = !state.editingId;

    if (!state.tipoActual) return;

    getCamposActuales().forEach((campo) => {
        const label = document.createElement("label");
        label.className = "field";
        label.htmlFor = fieldId(campo.nombre);
        label.append(document.createTextNode(obtenerEtiqueta(campo)));

        const control = crearControl(campo);
        label.appendChild(control);
        fields.appendChild(label);
    });
}

function crearControl(campo) {
    const tipo = campo.tipo || "text";
    const id = fieldId(campo.nombre);
    let control;

    if (tipo === "select" || tipo === "boolean") {
        control = document.createElement("select");
        control.appendChild(new Option("Selecciona", ""));
        const opciones = tipo === "boolean" ? (campo.opciones || ["Si", "No"]) : (campo.opciones || []);
        opciones.forEach((opcion) => control.appendChild(new Option(opcion, opcion)));
    } else if (esCampoLargo(campo.nombre)) {
        control = document.createElement("textarea");
        control.rows = 3;
    } else {
        control = document.createElement("input");
        control.type = tipo === "number" || tipo === "date" ? tipo : "text";
        if (tipo === "number") {
            control.step = "any";
            control.inputMode = "decimal";
        }
    }

    control.id = id;
    control.name = campo.nombre;
    control.required = campo.requerido !== false;
    control.placeholder = obtenerEtiqueta(campo);

    if (campo.nombre === "periodo" && !state.editingId) {
        control.value = periodoActual();
    }

    return control;
}

function esCampoLargo(nombre) {
    return /(observaciones|descripcion|diagnostico|actividades|recomendacion|condiciones|falla|motivo|soporte)/i.test(nombre);
}

function fieldId(nombre) {
    return `field-${nombre}`;
}

async function guardarRegistro(event) {
    event.preventDefault();
    if (!state.tipoActual) return;

    const payload = {};
    getCamposActuales().forEach((campo) => {
        const control = $(fieldId(campo.nombre));
        payload[campo.nombre] = control ? control.value : "";
    });

    const editando = Boolean(state.editingId);
    const url = editando ? `/api/${state.tipoActual}/${state.editingId}` : `/api/${state.tipoActual}`;
    const method = editando ? "PUT" : "POST";

    try {
        const data = await apiJson(url, {
            method,
            body: JSON.stringify(payload),
        });
        mostrarToast(data.message || (editando ? "Registro actualizado" : "Registro creado"), "success");
        limpiarFormulario();
        await obtenerDatos();
        if (state.tipoActual === "facturacion") {
            cargarDashboard().catch(() => null);
        }
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

function limpiarFormulario() {
    state.editingId = null;
    $("formDatos").reset();
    renderFormulario();
    syncAutomationPanel();
}

async function obtenerDatos() {
    if (!state.tipoActual) return;

    try {
        const data = await apiJson(`/api/${state.tipoActual}?skip=${state.skip}&limit=${PAGE_SIZE}`);
        state.registros = data.datos || [];
        state.total = data.total ?? state.registros.length;
        renderTabla();
        actualizarPaginacion();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

function renderTabla() {
    const head = $("tableHead");
    const body = $("tableBody");
    head.replaceChildren();
    body.replaceChildren();

    if (!state.tipoActual) {
        $("recordTotalLabel").textContent = "0 registros";
        return;
    }

    const columnas = obtenerColumnasTabla();
    const trHead = document.createElement("tr");
    ["ID", ...columnas.map(obtenerEtiqueta), "Acciones"].forEach((label) => {
        const th = document.createElement("th");
        th.textContent = label;
        trHead.appendChild(th);
    });
    head.appendChild(trHead);

    const datos = registrosFiltrados();
    $("recordTotalLabel").textContent = `${state.total} registro${state.total === 1 ? "" : "s"}`;

    if (!datos.length) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.className = "empty-state";
        td.colSpan = columnas.length + 2;
        td.textContent = "Sin registros para mostrar";
        tr.appendChild(td);
        body.appendChild(tr);
        return;
    }

    datos.forEach((item) => {
        const tr = document.createElement("tr");
        appendCell(tr, item.id);
        columnas.forEach((campo) => appendCell(tr, item[campo.nombre], campo));

        const actions = document.createElement("td");
        actions.className = "table-actions";
        const botones = [
            actionButton("Historial", () => abrirHistorial(item)),
            actionButton("Adjuntos", () => abrirAdjuntos(item)),
        ];
        if (!esSoloLectura()) {
            botones.unshift(actionButton("Editar", () => editarRegistro(item)));
            botones.push(actionButton("Eliminar", () => eliminarRegistro(item.id), "danger"));
        }
        actions.append(...botones);
        tr.appendChild(actions);
        body.appendChild(tr);
    });
}

function registrosFiltrados() {
    const query = normalizarTexto($("recordSearch").value);
    if (!query) return state.registros;

    return state.registros.filter((registro) => {
        return Object.values(registro).some((value) => normalizarTexto(value).includes(query));
    });
}

function obtenerColumnasTabla() {
    const campos = getCamposActuales();
    const prioridad = [
        "nombre",
        "numero_contrato",
        "numero_serie",
        "cliente_id",
        "contrato_id",
        "equipo_id",
        "periodo",
        "estado_cliente",
        "estado_contrato",
        "estado_equipo",
        "estado_factura",
        "estado",
        "monto",
        "total_facturado",
        "valor_total",
    ];

    const columnas = [];
    prioridad.forEach((nombre) => {
        const campo = campos.find((item) => item.nombre === nombre);
        if (campo && !columnas.includes(campo)) columnas.push(campo);
    });

    campos.forEach((campo) => {
        if (columnas.length < 8 && !columnas.includes(campo)) {
            columnas.push(campo);
        }
    });

    return columnas;
}

function appendCell(row, value, campo = null) {
    const td = document.createElement("td");
    td.textContent = formatearValor(value, campo);
    row.appendChild(td);
}

function actionButton(text, handler, variant = "ghost") {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `button button-${variant} button-small`;
    button.textContent = text;
    button.addEventListener("click", handler);
    return button;
}

function editarRegistro(item) {
    state.editingId = item.id;
    renderFormulario();
    getCamposActuales().forEach((campo) => {
        const control = $(fieldId(campo.nombre));
        if (control) {
            control.value = valorParaControl(item[campo.nombre], campo);
        }
    });
    $("formModeLabel").textContent = `Editando #${item.id}`;
    $("cancelEditBtn").hidden = false;
    document.querySelector(".editor-panel")?.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function eliminarRegistro(id) {
    if (!confirm(`¿Eliminar el registro #${id}?`)) return;

    try {
        const data = await apiJson(`/api/${state.tipoActual}/${id}`, { method: "DELETE" });
        mostrarToast(data.message || "Registro eliminado", "success");
        await obtenerDatos();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

function actualizarPaginacion() {
    const controls = $("paginationControls");
    controls.hidden = state.total <= PAGE_SIZE;
    const desde = state.total ? state.skip + 1 : 0;
    const hasta = Math.min(state.skip + PAGE_SIZE, state.total);
    $("paginacionInfo").textContent = `${desde}-${hasta} de ${state.total}`;
    $("paginaAnteriorBtn").disabled = state.skip === 0;
    $("paginaSiguienteBtn").disabled = state.skip + PAGE_SIZE >= state.total;
}

async function irPaginaAnterior() {
    state.skip = Math.max(0, state.skip - PAGE_SIZE);
    await obtenerDatos();
}

async function irPaginaSiguiente() {
    if (state.skip + PAGE_SIZE >= state.total) return;
    state.skip += PAGE_SIZE;
    await obtenerDatos();
}

function actualizarControlesImportacion() {
    const tipo = state.tipoActual;
    const soloLectura = esSoloLectura();
    document.querySelector(".import-box")?.toggleAttribute("hidden", soloLectura);
    if (soloLectura) return;

    const enabled = IMPORTABLE_TYPES.has(tipo);
    $("downloadTemplateBtn").disabled = !enabled;
    $("importBtn").disabled = !enabled;
    $("importFile").disabled = !enabled;
    $("exportCurrentBtn").disabled = !tipo;
    $("importTypeLabel").textContent = enabled
        ? `Carga masiva de ${state.tipos[tipo]}`
        : "Importación disponible para clientes, equipos y lecturas";
}

function exportarTipoActual() {
    if (!state.tipoActual) return;
    window.location.href = `/api/exportar/${state.tipoActual}/excel`;
}

function descargarPlantilla() {
    if (!IMPORTABLE_TYPES.has(state.tipoActual)) return;
    window.location.href = `/api/importar/${state.tipoActual}/plantilla`;
}

async function importarExcel() {
    if (!IMPORTABLE_TYPES.has(state.tipoActual)) return;

    const fileInput = $("importFile");
    if (!fileInput.files.length) {
        mostrarToast("Selecciona un archivo Excel.", "error");
        return;
    }

    const body = new FormData();
    body.append("archivo", fileInput.files[0]);

    try {
        const data = await apiJson(`/api/importar/${state.tipoActual}`, {
            method: "POST",
            body,
        });
        fileInput.value = "";
        mostrarToast(data.message || "Importación completada", data.errores?.length ? "info" : "success");
        await obtenerDatos();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

function syncAutomationPanel() {
    const panel = $("billingAutomationPanel");
    if (!panel) return;
    panel.hidden = state.tipoActual !== "facturacion" || esSoloLectura();
    resetFacturaPreview();
    syncAutomationPeriod();
}

function resetFacturaPreview() {
    state.lastFacturaPreview = null;
    state.facturaPreviewKey = null;
    const boton = $("generarFacturaBtn");
    if (boton) boton.disabled = true;
    const hint = $("facturaConfirmHint");
    if (hint) {
        hint.hidden = false;
        hint.textContent = "Previsualiza el cálculo antes de generar.";
    }
    $("autoFacturaPreview")?.replaceChildren();
    $("forzarFacturaField")?.classList.remove("attention");
}

function syncAutomationPeriod() {
    const input = $("autoPeriodo");
    if (input && !input.value) input.value = periodoActual();
}

async function previsualizarFacturacion() {
    const contratoId = $("autoContratoId").value;
    const periodo = $("autoPeriodo").value || periodoActual();
    if (!contratoId) {
        mostrarToast("Ingresa el contrato a facturar.", "error");
        return;
    }

    try {
        const calculo = await apiJson(`/api/facturacion-automatica/${contratoId}/${periodo}`);
        state.lastFacturaPreview = calculo;
        state.facturaPreviewKey = `${contratoId}|${periodo}`;
        renderFacturaPreview(calculo);
    } catch (error) {
        resetFacturaPreview();
        mostrarToast(error.message, "error");
    }
}

async function generarFacturacionAutomatica() {
    const contratoId = $("autoContratoId").value;
    const periodo = $("autoPeriodo").value || periodoActual();
    const numeroFactura = $("autoNumeroFactura").value.trim();
    const fechaFactura = $("autoFechaFactura").value;
    const estadoFactura = $("autoEstadoFactura").value;

    if (!contratoId || !numeroFactura || !fechaFactura || !estadoFactura) {
        mostrarToast("Completa contrato, número, fecha y estado de factura.", "error");
        return;
    }

    if (state.facturaPreviewKey !== `${contratoId}|${periodo}`) {
        mostrarToast("Previsualiza el cálculo para este contrato y periodo antes de generar.", "error");
        return;
    }

    const tieneAdvertencias = Boolean(
        state.lastFacturaPreview?.equipos_sin_lectura?.length || state.lastFacturaPreview?.inconsistencias?.length
    );
    const forzar = $("autoForzarFactura").checked;
    if (tieneAdvertencias && !forzar) {
        mostrarToast("El preview tiene inconsistencias o equipos sin lectura. Marca 'Forzar generación' para continuar.", "error");
        $("forzarFacturaField")?.classList.add("attention");
        return;
    }

    const payload = {
        numero_factura: numeroFactura,
        fecha_factura: fechaToIso(fechaFactura),
        estado_factura: estadoFactura,
        forzar,
    };

    if ($("autoEmpresaFactura").value) {
        payload.empresa_factura = $("autoEmpresaFactura").value;
    }
    if ($("autoFechaVencimiento").value) {
        payload.fecha_vencimiento = fechaToIso($("autoFechaVencimiento").value);
    }

    try {
        const data = await apiJson(`/api/facturacion-automatica/${contratoId}/${periodo}`, {
            method: "POST",
            body: JSON.stringify(payload),
        });
        mostrarToast(`${data.message}. Total: ${moneda(data.total_facturado)}`, "success");
        $("autoForzarFactura").checked = false;
        resetFacturaPreview();
        await seleccionarTipo("facturacion");
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

function renderFacturaPreview(calculo) {
    const container = $("autoFacturaPreview");
    if (!container) return;
    container.replaceChildren();

    const tieneAdvertencias = Boolean(calculo.equipos_sin_lectura?.length || calculo.inconsistencias?.length);
    const boton = $("generarFacturaBtn");
    if (boton) boton.disabled = false;
    const hint = $("facturaConfirmHint");
    if (hint) {
        hint.textContent = tieneAdvertencias
            ? "Hay advertencias: revisa el detalle antes de confirmar."
            : "Cálculo listo. Revisa los datos y confirma para generar la factura.";
    }
    $("forzarFacturaField")?.classList.toggle("attention", tieneAdvertencias);

    const summary = document.createElement("div");
    summary.className = "preview-grid";
    [
        ["Cliente", calculo.cliente_id],
        ["Consumo B/N", calculo.consumo_bn],
        ["Adicionales B/N", calculo.paginas_adicionales_bn],
        ["Consumo color", calculo.consumo_color],
        ["Adicionales color", calculo.paginas_adicionales_color],
        ["Total", moneda(calculo.total_facturado)],
    ].forEach(([label, value]) => summary.appendChild(keyValue(label, value)));
    container.appendChild(summary);

    if (tieneAdvertencias) {
        const warning = document.createElement("div");
        warning.className = "inline-message warning";
        warning.textContent = [
            calculo.equipos_sin_lectura?.length ? `Equipos sin lectura: ${calculo.equipos_sin_lectura.join(", ")}` : "",
            ...(calculo.inconsistencias || []),
            "Marca 'Forzar generación' para continuar de todas formas.",
        ].filter(Boolean).join(" | ");
        container.appendChild(warning);
    }
}

function fechaToIso(fecha) {
    return new Date(`${fecha}T00:00:00`).toISOString();
}

function cambiarVista(view) {
    if (!VIEW_META[view] || !vistaPermitida(view)) return;
    state.currentView = view;

    const grupo = grupoPorVista(view);
    const sectionId = grupo ? "datos" : view;

    document.querySelectorAll(".nav-item").forEach((button) => {
        button.classList.toggle("active", button.dataset.view === view);
    });
    document.querySelectorAll(".app-view").forEach((section) => {
        section.classList.toggle("active", section.id === `view-${sectionId}`);
    });

    $("activeViewTitle").textContent = VIEW_META[view].title;
    $("activeViewEyebrow").textContent = VIEW_META[view].eyebrow;

    if (grupo) {
        renderTipos(grupo);
        const keys = clavesDisponibles(grupo);
        if (!keys.includes(state.tipoActual)) {
            seleccionarTipo(keys[0] || "");
            return;
        }
    }

    refrescarVistaActual();
}

function refrescarVistaActual() {
    if (!state.usuario) return;

    const loaders = {
        dashboard: cargarDashboard,
        base_comercial: obtenerDatos,
        operacion_mensual: obtenerDatos,
        servicio_tecnico: obtenerDatos,
        inventario: obtenerDatos,
        informes: cargarInformes,
        alertas: cargarAlertas,
        usuarios: cargarUsuarios,
    };
    loaders[state.currentView]?.();
}

async function cargarDashboard() {
    const periodo = periodoActual();
    const [
        snapshotResult, financieraResult, costosResult, carteraResult,
        ingresosClienteResult, rentabilidadClienteResult, correctivosEquipoResult, toneresClienteResult,
        informeResult, alertasResult,
    ] = await Promise.allSettled([
        apiJson(`/api/dashboard/${periodo}`),
        apiJson(`/api/dashboard/${periodo}/serie-financiera?meses=6`),
        apiJson(`/api/dashboard/${periodo}/costos-por-tipo?meses=6`),
        apiJson(`/api/dashboard/${periodo}/cartera-por-edad?meses=6`),
        apiJson(`/api/dashboard/${periodo}/ingresos-por-cliente?meses=6`),
        apiJson(`/api/dashboard/${periodo}/rentabilidad-por-cliente?meses=6`),
        apiJson(`/api/dashboard/${periodo}/correctivos-por-equipo?meses=6`),
        apiJson(`/api/dashboard/${periodo}/toneres-por-cliente?meses=6`),
        apiJson(`/api/informes/${periodo}`),
        apiJson("/api/alertas"),
    ]);

    mostrarErrorDashboard([
        snapshotResult, financieraResult, costosResult, carteraResult,
        ingresosClienteResult, rentabilidadClienteResult, correctivosEquipoResult, toneresClienteResult,
        informeResult, alertasResult,
    ]);

    const snapshot = settledValue(snapshotResult)?.dashboard || {};
    const financiera = settledValue(financieraResult)?.serie || [];
    const costos = ultimaSerieConDatos(settledValue(costosResult)?.serie, "costos_por_tipo");
    const cartera = ultimaSerieConDatos(settledValue(carteraResult)?.serie, "cartera_por_edad");
    const ingresosCliente = ultimaSerieConDatos(settledValue(ingresosClienteResult)?.serie, "valores_por_cliente");
    const rentabilidadCliente = ultimaSerieConDatos(settledValue(rentabilidadClienteResult)?.serie, "valores_por_cliente");
    const correctivosEquipo = ultimaSerieConDatos(settledValue(correctivosEquipoResult)?.serie, "correctivos_por_equipo");
    const toneresCliente = ultimaSerieConDatos(settledValue(toneresClienteResult)?.serie, "toneres_por_cliente");
    const informe = settledValue(informeResult)?.informe || {};
    const alertas = settledValue(alertasResult) || { total: 0, alertas: [] };

    renderKpis(snapshot);
    renderFinancialChart(financiera);
    renderRankChart("costs", "costsChart", costos?.costos_por_tipo || {}, moneda, "accent");
    renderRankChart("cartera", "carteraChart", cartera?.cartera_por_edad || {}, moneda, "danger");
    renderRankChart("ingresosCliente", "ingresosClienteChart", ingresosCliente?.valores_por_cliente || {}, moneda, "accent");
    renderRankChart("rentabilidadCliente", "rentabilidadClienteChart", rentabilidadCliente?.valores_por_cliente || {}, porcentaje, "ok");
    renderRankChart("correctivosEquipo", "correctivosEquipoChart", correctivosEquipo?.correctivos_por_equipo || {}, entero, "danger");
    renderRankChart("toneresCliente", "toneresClienteChart", toneresCliente?.toneres_por_cliente || {}, entero, "brand");
    renderRecommendations(informe.recomendaciones || generarRecomendaciones(snapshot));
    renderAlertPreview(alertas);
}

function mostrarErrorDashboard(resultados) {
    const box = $("dashboardError");
    if (!box) return;

    const fallidos = resultados.filter((resultado) => resultado.status === "rejected");
    if (!fallidos.length) {
        box.hidden = true;
        box.textContent = "";
        return;
    }

    box.hidden = false;
    box.textContent = `No se pudo cargar parte del dashboard (${fallidos.length} de ${resultados.length} secciones): ${fallidos[0].reason.message}`;
}

function renderKpis(data) {
    const cards = [
        ["Facturado", data.facturado_mes, moneda, "money"],
        ["Recaudado", data.recaudado_mes, moneda, "money"],
        ["Cartera", data.cartera_pendiente, moneda, "risk"],
        ["Utilidad", data.utilidad_bruta, moneda, "profit"],
        ["Margen", data.margen_promedio, porcentaje, "profit"],
        ["Contratos activos", data.contratos_activos, entero, "count"],
        ["Equipos instalados", data.equipos_instalados, entero, "count"],
        ["Disponibles", data.equipos_disponibles, entero, "count"],
        ["En reparación", data.equipos_en_reparacion, entero, "risk"],
        ["Clientes en mora", data.clientes_en_mora, entero, "risk"],
        ["Contratos por vencer", data.contratos_por_vencer, entero, "risk"],
        ["Tóneres entregados", data.toneres_entregados_mes, entero, "count"],
    ];

    const grid = $("kpiGrid");
    grid.replaceChildren();
    cards.forEach(([label, value, formatter, tone]) => {
        const card = document.createElement("article");
        card.className = `kpi-card ${tone}`;
        const span = document.createElement("span");
        span.textContent = label;
        const strong = document.createElement("strong");
        strong.textContent = formatter(value);
        card.append(span, strong);
        grid.appendChild(card);
    });
}

function chartColor(token) {
    const value = getComputedStyle(document.documentElement).getPropertyValue(`--${token}`).trim();
    return value || "#1B3A6B";
}

function destruirChart(key) {
    if (state.charts[key]) {
        state.charts[key].destroy();
        state.charts[key] = null;
    }
}

function crearCanvas(container, alturaPx) {
    const canvas = document.createElement("canvas");
    canvas.style.width = "100%";
    canvas.style.height = `${alturaPx}px`;
    container.appendChild(canvas);
    return canvas;
}

function renderFinancialChart(serie) {
    const container = $("financialChart");
    container.replaceChildren();
    destruirChart("financial");
    if (!serie.length) {
        empty(container, "Sin datos financieros para el periodo.");
        return;
    }

    const canvas = crearCanvas(container, 300);
    state.charts.financial = new Chart(canvas.getContext("2d"), {
        type: "bar",
        data: {
            labels: serie.map((item) => item.periodo),
            datasets: [
                { label: "Facturado", data: serie.map((item) => item.facturado || 0), backgroundColor: chartColor("accent") },
                { label: "Recaudado", data: serie.map((item) => item.recaudado || 0), backgroundColor: chartColor("brand") },
                { label: "Utilidad", data: serie.map((item) => item.utilidad || 0), backgroundColor: chartColor("ok") },
            ],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom" },
                tooltip: { callbacks: { label: (ctx) => `${ctx.dataset.label}: ${moneda(ctx.raw)}` } },
            },
            scales: {
                y: { ticks: { callback: (value) => moneda(value) } },
            },
        },
    });
}

function renderRankChart(chartKey, containerId, data, formatter = entero, colorToken = "brand") {
    const container = $(containerId);
    container.replaceChildren();
    destruirChart(chartKey);

    const entries = Object.entries(data || {}).sort((a, b) => (b[1] || 0) - (a[1] || 0)).slice(0, 8);
    if (!entries.length) {
        empty(container, "Sin datos para mostrar.");
        return;
    }

    const canvas = crearCanvas(container, 260);
    state.charts[chartKey] = new Chart(canvas.getContext("2d"), {
        type: "bar",
        data: {
            labels: entries.map(([label]) => labelize(label)),
            datasets: [{ data: entries.map(([, value]) => value || 0), backgroundColor: chartColor(colorToken) }],
        },
        options: {
            indexAxis: "y",
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (ctx) => formatter(ctx.raw) } },
            },
            scales: {
                x: { ticks: { callback: (value) => formatter(value) } },
            },
        },
    });
}

function renderRecommendations(items) {
    const container = $("recommendationList");
    container.replaceChildren();
    if (!items.length) {
        empty(container, "Sin recomendaciones activas.");
        return;
    }

    items.forEach((item) => {
        const div = document.createElement("div");
        div.className = "recommendation-item";
        div.textContent = item;
        container.appendChild(div);
    });
}

function generarRecomendaciones(snapshot) {
    const items = [];
    if ((snapshot.margen_promedio || 0) < 15) items.push("Revisar contratos con margen bajo antes de renovar tarifas.");
    if ((snapshot.cartera_pendiente || 0) > 0) items.push("Priorizar gestión de cartera pendiente del periodo.");
    if ((snapshot.contratos_por_vencer || 0) > 0) items.push("Preparar renovaciones de contratos próximos a vencer.");
    return items;
}

function renderAlertPreview(data) {
    $("alertSummary").textContent = `${data.total || 0} alerta${data.total === 1 ? "" : "s"}`;
    const container = $("alertPreviewList");
    container.replaceChildren();
    const alertas = data.alertas || [];
    if (!alertas.length) {
        empty(container, "Sin alertas activas.");
        return;
    }
    alertas.slice(0, 5).forEach((alerta) => container.appendChild(alertElement(alerta, false)));
}

async function cargarInformes() {
    const periodo = periodoActual();
    actualizarLinksInformes(periodo);

    const [generalResult, carteraResult, tecnicoResult] = await Promise.allSettled([
        apiJson(`/api/informes/${periodo}`),
        apiJson(`/api/informes/${periodo}/cartera`),
        apiJson(`/api/informes/${periodo}/tecnico`),
    ]);

    const general = settledValue(generalResult)?.informe;
    const cartera = settledValue(carteraResult)?.informe;
    const tecnico = settledValue(tecnicoResult)?.informe;

    renderInformeGeneral(general || {});
    renderInformeCartera(cartera?.clientes || []);
    renderInformeTecnico(tecnico || {});

    [generalResult, carteraResult, tecnicoResult].forEach((result) => {
        if (result.status === "rejected") mostrarToast(result.reason.message, "error");
    });
}

function actualizarLinksInformes(periodo) {
    const links = {
        generalPdfLink: `/api/informes/${periodo}/pdf`,
        generalExcelLink: `/api/informes/${periodo}/excel`,
        carteraPdfLink: `/api/informes/${periodo}/cartera/pdf`,
        carteraExcelLink: `/api/informes/${periodo}/cartera/excel`,
        tecnicoPdfLink: `/api/informes/${periodo}/tecnico/pdf`,
        tecnicoExcelLink: `/api/informes/${periodo}/tecnico/excel`,
    };
    Object.entries(links).forEach(([id, href]) => {
        if ($(id)) $(id).href = href;
    });
}

function renderInformeGeneral(data) {
    const grid = $("reportGeneralGrid");
    grid.replaceChildren();
    [
        ["Contratos", data.total_contratos, entero],
        ["Clientes", data.total_clientes, entero],
        ["Equipos", data.total_equipos, entero],
        ["Facturado", data.facturado_mes, moneda],
        ["Recaudado", data.recaudado_mes, moneda],
        ["Cartera", data.cartera_pendiente, moneda],
        ["Costos", data.costos_mes, moneda],
        ["Utilidad", data.utilidad_bruta, moneda],
        ["Margen", data.margen_promedio, porcentaje],
        ["Preventivos", data.preventivos_del_mes, entero],
        ["Correctivos", data.correctivos_del_mes, entero],
        ["Clientes en mora", data.clientes_en_mora, entero],
    ].forEach(([label, value, formatter]) => {
        const card = document.createElement("article");
        card.className = "kpi-card compact-card";
        card.append(textSpan(label), textStrong(formatter(value)));
        grid.appendChild(card);
    });
}

function renderInformeCartera(clientes) {
    const head = $("carteraReportHead");
    const body = $("carteraReportBody");
    head.replaceChildren();
    body.replaceChildren();

    const tr = document.createElement("tr");
    ["Cliente", "Emitidas", "Pagadas", "Vencidas", "Saldo", "Mora", "Estado"].forEach((label) => {
        const th = document.createElement("th");
        th.textContent = label;
        tr.appendChild(th);
    });
    head.appendChild(tr);

    if (!clientes.length) {
        const emptyRow = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = 7;
        td.className = "empty-state";
        td.textContent = "Sin facturas en el periodo";
        emptyRow.appendChild(td);
        body.appendChild(emptyRow);
        return;
    }

    clientes.forEach((cliente) => {
        const row = document.createElement("tr");
        [
            cliente.cliente_id,
            cliente.facturas_emitidas,
            cliente.facturas_pagadas,
            cliente.facturas_vencidas,
            moneda(cliente.saldo_pendiente),
            cliente.dias_mora_max,
            cliente.estado,
        ].forEach((value) => appendCell(row, value));
        body.appendChild(row);
    });
}

function renderInformeTecnico(data) {
    const container = $("technicalReport");
    container.replaceChildren();
    container.append(
        keyValue("Correctivos del mes", entero(data.correctivos_del_mes)),
        keyValue("Tiempo promedio de respuesta", dias(data.tiempo_promedio_respuesta)),
        keyValue("Tiempo promedio de solución", dias(data.tiempo_promedio_solucion))
    );

    renderMiniList(container, "Preventivos por estado", data.preventivos_por_estado || {}, entero);
    renderMiniList(container, "Equipos con más fallas", objectFromList(data.equipos_con_mas_fallas, "equipo_id", "fallas"), entero);
    renderMiniList(container, "Repuestos más usados", objectFromList(data.repuestos_mas_usados, "descripcion", "cantidad"), entero);
    renderMiniList(container, "Costos técnicos por contrato", data.costos_tecnicos_por_contrato || {}, moneda);
}

async function cargarInformeCliente() {
    const id = $("reportClientId").value;
    if (!id) return;

    try {
        const data = await apiJson(`/api/informes/${periodoActual()}/cliente/${id}`);
        renderDetalleInforme("clientReportDetail", data.informe, {
            pdf: `/api/informes/${periodoActual()}/cliente/${id}/pdf`,
            excel: `/api/informes/${periodoActual()}/cliente/${id}/excel`,
        });
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

async function cargarInformeEquipo() {
    const id = $("reportEquipoId").value;
    if (!id) return;

    try {
        const data = await apiJson(`/api/informes/${periodoActual()}/equipo/${id}`);
        renderDetalleInforme("equipoReportDetail", data.informe, {
            pdf: `/api/informes/${periodoActual()}/equipo/${id}/pdf`,
            excel: `/api/informes/${periodoActual()}/equipo/${id}/excel`,
        });
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

function renderDetalleInforme(containerId, data, links) {
    const container = $(containerId);
    container.replaceChildren();
    const actions = document.createElement("div");
    actions.className = "inline-actions";
    actions.append(anchor("PDF", links.pdf), anchor("Excel", links.excel));
    container.appendChild(actions);
    Object.entries(data || {}).forEach(([key, value]) => {
        container.appendChild(keyValue(labelize(key), formatearValor(value)));
    });
}

async function cargarAlertas() {
    const incluirDescartadas = $("includeDiscardedFilter")?.checked || false;
    try {
        const [activas, guardadas] = await Promise.all([
            apiJson(`/api/alertas?incluir_descartadas=${incluirDescartadas}`),
            apiJson("/api/alertas/guardadas"),
        ]);
        state.alertas = activas.alertas || [];
        state.alertasMeta = { criticas: activas.criticas || 0, generadoEn: activas.generado_en };
        renderAlertasActivas();
        renderAlertasGuardadas(guardadas.alertas || []);
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

function renderAlertasActivas() {
    const filtro = $("alertLevelFilter").value;
    const alertas = (state.alertas || []).filter((alerta) => !filtro || alerta.nivel === filtro);
    $("alertsTitle").textContent = `${alertas.length} alerta${alertas.length === 1 ? "" : "s"}`;

    const meta = $("alertsMeta");
    if (meta) {
        meta.textContent = state.alertasMeta
            ? `${state.alertasMeta.criticas} críticas · ${fechaCorta(state.alertasMeta.generadoEn)}`
            : "";
    }

    const container = $("alertsList");
    container.replaceChildren();
    if (!alertas.length) {
        empty(container, "Sin alertas con este filtro.");
        return;
    }
    alertas.forEach((alerta) => container.appendChild(alertElement(alerta, true)));
}

function renderAlertasGuardadas(alertas) {
    const container = $("savedAlertsList");
    container.replaceChildren();
    if (!alertas.length) {
        empty(container, "Sin alertas guardadas.");
        return;
    }
    alertas.forEach((alerta) => container.appendChild(alertElement(alerta, true)));
}

function alertElement(alerta, withActions) {
    const item = document.createElement("article");
    item.className = `alert-item ${alerta.nivel || "info"}`;
    if (alerta.leida) item.classList.add("leida");

    const header = document.createElement("div");
    header.className = "alert-item-header";
    const tipo = textSpan(labelize(alerta.tipo || "alerta"));
    tipo.className = "alert-item-tipo";
    header.append(statusPill(labelize(alerta.nivel || "info")), tipo);
    if (alerta.descartada) header.appendChild(statusPill("Descartada"));

    const message = document.createElement("p");
    message.textContent = alerta.mensaje || "Alerta sin mensaje";
    item.append(header, message);

    if (withActions) {
        const actions = document.createElement("div");
        actions.className = "inline-actions";
        actions.append(
            actionButton(alerta.leida ? "Marcar no leída" : "Marcar leída", () => actualizarEstadoAlerta(alerta, { leida: !alerta.leida }), "ghost"),
            actionButton(alerta.guardada ? "Quitar guardado" : "Guardar", () => actualizarEstadoAlerta(alerta, { guardada: !alerta.guardada }), "secondary"),
            actionButton(alerta.descartada ? "Restaurar" : "Descartar", () => actualizarEstadoAlerta(alerta, { descartada: !alerta.descartada }), alerta.descartada ? "secondary" : "ghost")
        );
        item.appendChild(actions);
    }

    return item;
}

async function actualizarEstadoAlerta(alerta, patch) {
    try {
        await apiJson("/api/alertas/estado", {
            method: "POST",
            body: JSON.stringify({
                tipo: alerta.tipo,
                referencia_id: alerta.referencia_id,
                mensaje: alerta.mensaje,
                nivel: alerta.nivel,
                ...patch,
            }),
        });
        await cargarAlertas();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

async function cargarUsuarios() {
    const container = $("pendingUsersList");
    container.replaceChildren();

    try {
        const data = await apiJson("/auth/pendientes");
        const usuarios = data.usuarios || [];
        if (!usuarios.length) {
            empty(container, "Sin usuarios pendientes.");
            return;
        }

        usuarios.forEach((usuario) => {
            const card = document.createElement("article");
            card.className = "user-card";
            const info = document.createElement("div");
            const name = document.createElement("strong");
            name.textContent = usuario.email;
            const meta = document.createElement("span");
            meta.textContent = usuario.rol || "Rol no indicado";
            info.append(name, meta);

            const select = document.createElement("select");
            select.id = `role-${usuario.id}`;
            ROLE_OPTIONS.forEach((role) => select.appendChild(new Option(role, role)));
            select.value = usuario.rol || ADMIN_ROLE;

            const actions = document.createElement("div");
            actions.className = "inline-actions";
            actions.append(
                select,
                actionButton("Aprobar", () => aprobarUsuario(usuario.id), "primary"),
                actionButton("Rechazar", () => rechazarUsuario(usuario.id), "danger")
            );
            card.append(info, actions);
            container.appendChild(card);
        });
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

async function aprobarUsuario(id) {
    const rol = $(`role-${id}`).value;
    try {
        const data = await apiJson(`/auth/${id}/aprobar`, {
            method: "POST",
            body: JSON.stringify({ rol }),
        });
        mostrarToast(data.message || "Usuario aprobado", "success");
        await cargarUsuarios();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

async function rechazarUsuario(id) {
    try {
        const data = await apiJson(`/auth/${id}/rechazar`, { method: "POST" });
        mostrarToast(data.message || "Usuario rechazado", "success");
        await cargarUsuarios();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

async function abrirAdjuntos(item) {
    state.currentAdjuntoTarget = { tipo: state.tipoActual, id: item.id };
    $("adjuntosTitle").textContent = `Adjuntos #${item.id}`;
    $("adjuntosContext").textContent = `${state.tipos[state.tipoActual]} · ${resumenRegistro(item)}`;
    $("adjuntosForm").reset();
    mostrarDialog("adjuntosDialog");
    await cargarAdjuntos();
}

async function cargarAdjuntos() {
    const target = state.currentAdjuntoTarget;
    if (!target) return;

    const list = $("adjuntosList");
    list.replaceChildren();
    try {
        const data = await apiJson(`/api/adjuntos?tipo_entidad=${target.tipo}&entidad_id=${target.id}`);
        const adjuntos = data.adjuntos || [];
        if (!adjuntos.length) {
            empty(list, "Sin adjuntos.");
            return;
        }
        adjuntos.forEach((adjunto) => {
            const row = document.createElement("div");
            row.className = "adjunto-row";
            const info = document.createElement("div");
            const name = document.createElement("strong");
            name.textContent = adjunto.nombre_original;
            const meta = document.createElement("span");
            meta.textContent = `${adjunto.tipo_documento || "Documento"} · ${bytes(adjunto.tamano_bytes)}`;
            info.append(name, meta);
            const actions = document.createElement("div");
            actions.className = "inline-actions";
            actions.append(anchor("Descargar", adjunto.url_descarga), actionButton("Eliminar", () => eliminarAdjunto(adjunto.id), "danger"));
            row.append(info, actions);
            list.appendChild(row);
        });
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

async function subirAdjunto(event) {
    event.preventDefault();
    const target = state.currentAdjuntoTarget;
    if (!target) return;

    const file = $("adjuntoArchivo").files[0];
    if (!file) {
        mostrarToast("Selecciona un archivo.", "error");
        return;
    }

    const body = new FormData();
    body.append("tipo_entidad", target.tipo);
    body.append("entidad_id", target.id);
    body.append("tipo_documento", $("adjuntoTipoDocumento").value);
    body.append("observaciones", $("adjuntoObservaciones").value);
    body.append("archivo", file);

    try {
        const data = await apiJson("/api/adjuntos", { method: "POST", body });
        mostrarToast(data.message || "Adjunto subido", "success");
        $("adjuntosForm").reset();
        await cargarAdjuntos();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

async function eliminarAdjunto(id) {
    if (!confirm(`¿Eliminar el adjunto #${id}?`)) return;
    try {
        const data = await apiJson(`/api/adjuntos/${id}`, { method: "DELETE" });
        mostrarToast(data.message || "Adjunto eliminado", "success");
        await cargarAdjuntos();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

function cerrarAdjuntos() {
    $("adjuntosDialog").close();
    state.currentAdjuntoTarget = null;
}

async function abrirHistorial(item) {
    $("historyTitle").textContent = `Historial #${item.id}`;
    $("historyContext").textContent = `${state.tipos[state.tipoActual]} · ${resumenRegistro(item)}`;
    const list = $("historyList");
    list.replaceChildren();
    mostrarDialog("historyDialog");

    try {
        const data = await apiJson(`/api/historial/${state.tipoActual}/${item.id}`);
        const historial = data.historial || [];
        if (!historial.length) {
            empty(list, "Sin cambios registrados.");
            return;
        }
        historial.forEach((entry) => {
            const row = document.createElement("article");
            row.className = "history-row";
            const title = document.createElement("strong");
            title.textContent = `${labelize(entry.accion)}${entry.campo ? ` · ${labelize(entry.campo)}` : ""}`;
            const meta = document.createElement("span");
            meta.textContent = `${entry.fecha ? fechaCorta(entry.fecha) : "Sin fecha"} · Usuario ${entry.usuario_id || "N/D"}`;
            const values = document.createElement("p");
            values.textContent = entry.campo
                ? `${entry.valor_anterior ?? "N/D"} → ${entry.valor_nuevo ?? "N/D"}`
                : "Registro creado o eliminado";
            row.append(title, meta, values);
            list.appendChild(row);
        });
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

function cerrarHistorial() {
    $("historyDialog").close();
}

function mostrarDialog(id) {
    const dialog = $(id);
    if (dialog.showModal) {
        dialog.showModal();
    } else {
        dialog.setAttribute("open", "");
    }
}

function getCamposActuales() {
    return state.configuracion[state.tipoActual] || [];
}

function obtenerEtiqueta(campo) {
    return campo.etiqueta || campo.label || labelize(campo.nombre);
}

function valorParaControl(value, campo) {
    if (value === null || value === undefined) return "";
    if ((campo.tipo || "") === "date") return String(value).slice(0, 10);
    if ((campo.tipo || "") === "boolean") return value === true ? "Si" : value === false ? "No" : value;
    return value;
}

function formatearValor(value, campo = null) {
    if (value === null || value === undefined || value === "") return "N/D";
    const nombre = campo?.nombre || "";
    if (typeof value === "object") return JSON.stringify(value);
    if (/(valor|monto|total|precio|costo|saldo|ingresos|costos|ganancia|recaudado|facturado|cartera)/i.test(nombre)) {
        return moneda(value);
    }
    if (/(porcentaje|margen|rentabilidad)/i.test(nombre)) {
        return porcentaje(value);
    }
    if (/(fecha)/i.test(nombre) || /^\d{4}-\d{2}-\d{2}T/.test(String(value))) {
        return fechaCorta(value);
    }
    if (typeof value === "boolean") return value ? "Sí" : "No";
    return String(value);
}

function moneda(value) {
    const number = Number(value || 0);
    return new Intl.NumberFormat("es-CO", {
        style: "currency",
        currency: "COP",
        maximumFractionDigits: 0,
    }).format(number);
}

function porcentaje(value) {
    if (value === null || value === undefined || value === "") return "N/D";
    return `${Number(value || 0).toFixed(1)}%`;
}

function entero(value) {
    if (value === null || value === undefined || value === "") return "0";
    return new Intl.NumberFormat("es-CO", { maximumFractionDigits: 0 }).format(Number(value || 0));
}

function dias(value) {
    if (value === null || value === undefined) return "N/D";
    return `${Number(value).toFixed(1)} días`;
}

function bytes(value) {
    const number = Number(value || 0);
    if (number < 1024) return `${number} B`;
    if (number < 1024 * 1024) return `${(number / 1024).toFixed(1)} KB`;
    return `${(number / 1024 / 1024).toFixed(1)} MB`;
}

function fechaCorta(value) {
    if (!value) return "N/D";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value).slice(0, 10);
    return new Intl.DateTimeFormat("es-CO", { dateStyle: "medium" }).format(date);
}

function labelize(value) {
    return String(value || "")
        .replace(/_/g, " ")
        .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function normalizarTexto(value) {
    return String(value ?? "")
        .normalize("NFD")
        .replace(/\p{Diacritic}/gu, "")
        .toLowerCase()
        .trim();
}

function resumenRegistro(item) {
    const campos = ["nombre", "numero_contrato", "numero_serie", "periodo", "estado", "estado_factura"];
    const found = campos.map((campo) => item[campo]).find(Boolean);
    return found || `ID ${item.id}`;
}

function settledValue(result) {
    return result.status === "fulfilled" ? result.value : null;
}

function ultimaSerieConDatos(serie = [], key) {
    return [...serie].reverse().find((item) => Object.keys(item[key] || {}).length) || serie[serie.length - 1] || null;
}

function objectFromList(list = [], keyField, valueField) {
    return list.reduce((acc, item) => {
        acc[item[keyField]] = item[valueField];
        return acc;
    }, {});
}

function textSpan(text) {
    const span = document.createElement("span");
    span.textContent = text;
    return span;
}

function textStrong(text) {
    const strong = document.createElement("strong");
    strong.textContent = text;
    return strong;
}

function keyValue(label, value) {
    const item = document.createElement("div");
    item.className = "key-value";
    item.append(textSpan(label), textStrong(value ?? "N/D"));
    return item;
}

function statusPill(text) {
    const pill = document.createElement("span");
    pill.className = "status-pill";
    pill.textContent = text;
    return pill;
}

function anchor(text, href) {
    const link = document.createElement("a");
    link.className = "text-action";
    link.href = href;
    link.textContent = text;
    return link;
}

function empty(container, message) {
    const div = document.createElement("div");
    div.className = "empty-state";
    div.textContent = message;
    container.appendChild(div);
}

function renderMiniList(container, title, data, formatter) {
    const entries = Object.entries(data || {});
    if (!entries.length) return;

    const block = document.createElement("div");
    block.className = "mini-list";
    const heading = document.createElement("h3");
    heading.textContent = title;
    block.appendChild(heading);
    entries.forEach(([label, value]) => block.appendChild(keyValue(labelize(label), formatter(value))));
    container.appendChild(block);
}

function mostrarToast(message, type = "info") {
    const stack = $("toastStack");
    const toast = document.createElement("div");
    toast.className = `toast ${type}`;
    toast.textContent = message;
    stack.appendChild(toast);
    setTimeout(() => toast.remove(), 4500);
}
