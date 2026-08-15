// Espacio de trabajo de datos: formulario dinámico dirigido por metadata
// (/api/configuracion), tabla, paginación, import/export, facturación
// automática y los diálogos de historial/adjuntos.

const PAGE_SIZE = 100;

async function seleccionarTipo(tipo) {
    state.tipoActual = tipo || "";
    state.skip = 0;
    state.editingId = null;
    state.registros = [];
    state.total = 0;
    $("tipoSelector").value = state.tipoActual;

    document.querySelectorAll(".module-btn").forEach((button) => {
        button.classList.toggle("is-active", button.dataset.tipo === state.tipoActual);
    });

    renderFormulario();
    renderTabla();
    actualizarControlesImportacion();
    syncAutomationPanel();

    if (state.tipoActual) {
        await obtenerDatos();
    }
}

function getCamposActuales() {
    return state.configuracion[state.tipoActual] || [];
}

function obtenerEtiqueta(campo) {
    return campo.etiqueta || campo.label || labelize(campo.nombre);
}

function fieldId(nombre) {
    return `field-${nombre}`;
}

function esCampoLargo(nombre) {
    return /(observaciones|descripcion|diagnostico|actividades|recomendacion|condiciones|falla|motivo|soporte)/i.test(nombre);
}

function renderFormulario() {
    const fields = $("formFields");
    fields.replaceChildren();
    $("formTitle").textContent = state.tipoActual ? state.tipos[state.tipoActual] : "Selecciona un tipo";
    $("formModeLabel").textContent = state.editingId ? `Editando #${state.editingId}` : "Nuevo registro";

    const puedeEscribirTipo = state.tipoActual && puedeEscribir(state.tipoActual, state.usuario?.rol);
    $("noWriteNote").hidden = !state.tipoActual || puedeEscribirTipo;
    $("formDatos").hidden = !puedeEscribirTipo;
    if (!puedeEscribirTipo) return;

    $("saveRecordBtn").disabled = !state.tipoActual;
    $("cancelEditBtn").hidden = !state.editingId;
    if (!state.tipoActual) return;

    getCamposActuales().forEach((campo) => {
        const label = document.createElement("label");
        label.className = "field";
        label.htmlFor = fieldId(campo.nombre);
        label.append(document.createTextNode(obtenerEtiqueta(campo)));
        label.appendChild(crearControl(campo));
        fields.appendChild(label);
    });
}

function crearControl(campo) {
    const tipo = campo.tipo || "text";
    let control;

    if (tipo === "select" || tipo === "boolean") {
        control = document.createElement("select");
        control.className = "select";
        control.appendChild(new Option("Selecciona", ""));
        const opciones = tipo === "boolean" ? (campo.opciones || ["Si", "No"]) : (campo.opciones || []);
        opciones.forEach((opcion) => control.appendChild(new Option(opcion, opcion)));
    } else if (esCampoLargo(campo.nombre)) {
        control = document.createElement("textarea");
        control.className = "textarea";
        control.rows = 3;
    } else {
        control = document.createElement("input");
        control.className = "input";
        control.type = tipo === "number" || tipo === "date" ? tipo : "text";
        if (tipo === "number") {
            control.step = "any";
            control.inputMode = "decimal";
        }
    }

    control.id = fieldId(campo.nombre);
    control.name = campo.nombre;
    control.required = campo.requerido !== false;
    control.placeholder = obtenerEtiqueta(campo);

    if (campo.nombre === "periodo" && !state.editingId) {
        control.value = periodoActual();
    }

    return control;
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
        const data = await apiJson(url, { method, body: JSON.stringify(payload) });
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
        td.className = "empty-state-cell";
        td.colSpan = columnas.length + 2;
        td.textContent = "Sin registros para mostrar";
        tr.appendChild(td);
        body.appendChild(tr);
        return;
    }

    const rol = state.usuario?.rol;
    const puedeEscribirTipo = puedeEscribir(state.tipoActual, rol);
    const puedeBorrar = puedeEliminar(rol);

    datos.forEach((item) => {
        const tr = document.createElement("tr");
        appendCell(tr, item.id);
        columnas.forEach((campo) => appendCell(tr, item[campo.nombre], campo));

        const actions = document.createElement("td");
        actions.className = "row-actions-cell";
        const botones = [
            actionButton("Historial", () => abrirHistorial(item)),
            actionButton("Adjuntos", () => abrirAdjuntos(item)),
        ];
        if (puedeEscribirTipo) botones.unshift(actionButton("Editar", () => editarRegistro(item)));
        if (puedeBorrar) botones.push(actionButton("Eliminar", () => eliminarRegistro(item.id), "danger"));

        const menu = document.createElement("div");
        menu.className = "row-actions";
        menu.hidden = true;
        menu.append(...botones);

        const toggle = document.createElement("button");
        toggle.type = "button";
        toggle.className = "row-actions-toggle";
        toggle.textContent = "⋯";
        toggle.setAttribute("aria-label", "Mostrar acciones");
        toggle.addEventListener("click", () => {
            menu.hidden = !menu.hidden;
            toggle.classList.toggle("is-open", !menu.hidden);
        });

        actions.append(toggle, menu);
        tr.appendChild(actions);
        body.appendChild(tr);
    });
}

function registrosFiltrados() {
    const query = normalizarTexto($("recordSearch").value);
    if (!query) return state.registros;
    return state.registros.filter((registro) => Object.values(registro).some((value) => normalizarTexto(value).includes(query)));
}

function obtenerColumnasTabla() {
    const campos = getCamposActuales();
    const prioridad = [
        "nombre", "numero_contrato", "numero_serie", "cliente_id", "contrato_id", "equipo_id",
        "periodo", "estado_cliente", "estado_contrato", "estado_equipo", "estado_factura", "estado",
        "monto", "total_facturado", "valor_total",
    ];

    const columnas = [];
    prioridad.forEach((nombre) => {
        const campo = campos.find((item) => item.nombre === nombre);
        if (campo && !columnas.includes(campo)) columnas.push(campo);
    });
    campos.forEach((campo) => {
        if (columnas.length < 8 && !columnas.includes(campo)) columnas.push(campo);
    });
    return columnas;
}

function appendCell(row, value, campo = null) {
    const td = document.createElement("td");
    td.textContent = formatearValor(value, campo);
    row.appendChild(td);
}

function editarRegistro(item) {
    state.editingId = item.id;
    renderFormulario();
    getCamposActuales().forEach((campo) => {
        const control = $(fieldId(campo.nombre));
        if (control) control.value = valorParaControl(item[campo.nombre], campo);
    });
    $("formModeLabel").textContent = `Editando #${item.id}`;
    $("cancelEditBtn").hidden = false;
    document.querySelector(".editor-col")?.scrollIntoView({ behavior: "smooth", block: "start" });
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
    const habilitado = IMPORTABLE_TYPES.has(tipo) && puedeEscribir(tipo, state.usuario?.rol);
    $("importBox").hidden = !tipo || !IMPORTABLE_TYPES.has(tipo);
    $("downloadTemplateBtn").disabled = !habilitado;
    $("importBtn").disabled = !habilitado;
    $("importFile").disabled = !habilitado;
    $("exportCurrentBtn").disabled = !tipo;
    $("importTypeLabel").textContent = habilitado
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
        const data = await apiJson(`/api/importar/${state.tipoActual}`, { method: "POST", body });
        fileInput.value = "";
        mostrarToast(data.message || "Importación completada", data.errores?.length ? "info" : "success");
        await obtenerDatos();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

// ---------------------------------------------------------------------
// Facturación automática: previsualizar (GET) y solo entonces confirmar
// (POST). El botón de confirmar arranca deshabilitado y solo se habilita
// tras un preview exitoso para el contrato/periodo actuales; si hay
// inconsistencias o equipos sin lectura, exige marcar "Forzar generación"
// antes de dejar avanzar (routers/facturacion_automatica.py espera esto).
// ---------------------------------------------------------------------

function syncAutomationPanel() {
    const panel = $("billingAutomationPanel");
    panel.hidden = state.tipoActual !== "facturacion" || !puedeEscribir("facturacion", state.usuario?.rol);
    resetFacturaPreview();
    syncAutomationPeriod();
}

function syncAutomationPeriod() {
    const input = $("autoPeriodo");
    if (input && !input.value) input.value = periodoActual();
}

function resetFacturaPreview() {
    state.lastFacturaPreview = null;
    state.facturaPreviewKey = null;
    const boton = $("generarFacturaBtn");
    if (boton) boton.disabled = true;
    const hint = $("facturaConfirmHint");
    if (hint) hint.textContent = "Previsualiza el cálculo antes de generar.";
    $("autoFacturaPreview")?.replaceChildren();
    $("forzarFacturaField")?.classList.remove("is-attention");
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
        $("forzarFacturaField")?.classList.add("is-attention");
        return;
    }

    const payload = {
        numero_factura: numeroFactura,
        fecha_factura: fechaToIso(fechaFactura),
        estado_factura: estadoFactura,
        forzar,
    };
    if ($("autoEmpresaFactura").value) payload.empresa_factura = $("autoEmpresaFactura").value;
    if ($("autoFechaVencimiento").value) payload.fecha_vencimiento = fechaToIso($("autoFechaVencimiento").value);

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
    $("generarFacturaBtn").disabled = false;
    $("facturaConfirmHint").textContent = tieneAdvertencias
        ? "Hay advertencias: revisa el detalle antes de confirmar."
        : "Cálculo listo. Revisa los datos y confirma para generar la factura.";
    $("forzarFacturaField")?.classList.toggle("is-attention", tieneAdvertencias);

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
        warning.className = "inline-note";
        warning.textContent = [
            calculo.equipos_sin_lectura?.length ? `Equipos sin lectura: ${calculo.equipos_sin_lectura.join(", ")}` : "",
            ...(calculo.inconsistencias || []),
            "Marca 'Forzar generación' para continuar de todas formas.",
        ].filter(Boolean).join(" | ");
        container.appendChild(warning);
    }
}

// ---------------------------------------------------------------------
// Diálogo de historial
// ---------------------------------------------------------------------

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
            meta.textContent = `${entry.fecha ? fechaCorta(entry.fecha) : "Sin fecha"} · ${entry.usuario || "Usuario N/D"}`;
            const values = document.createElement("p");
            values.textContent = entry.campo ? `${entry.valor_anterior ?? "N/D"} → ${entry.valor_nuevo ?? "N/D"}` : "Registro creado o eliminado";
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

// ---------------------------------------------------------------------
// Diálogo de adjuntos
// ---------------------------------------------------------------------

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
            row.className = "list-row";
            const info = document.createElement("div");
            const name = document.createElement("strong");
            name.textContent = adjunto.nombre_original;
            const meta = document.createElement("span");
            meta.textContent = `${adjunto.tipo_documento || "Documento"} · ${bytes(adjunto.tamano_bytes)}`;
            info.append(name, meta);
            const actions = document.createElement("div");
            actions.className = "section-actions";
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

function mostrarDialog(id) {
    const dialog = $(id);
    if (dialog.showModal) dialog.showModal();
    else dialog.setAttribute("open", "");
}
