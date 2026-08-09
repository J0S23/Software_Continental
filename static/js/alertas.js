// Vista "Alertas": tarjetas por nivel con acciones que alternan estado
// (leída/guardada/descartada) contra /api/alertas/estado, más el filtro
// "incluir descartadas" que viaja al backend.

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
    item.className = `alert-card alert-card--${alerta.nivel || "info"}`;
    if (alerta.leida) item.classList.add("is-read");

    const header = document.createElement("div");
    header.className = "alert-card__head";
    const tipo = textSpan(labelize(alerta.tipo || "alerta"));
    tipo.className = "alert-card__type";
    header.append(pill(labelize(alerta.nivel || "info"), alerta.nivel), tipo);
    if (alerta.descartada) header.appendChild(pill("Descartada"));

    const message = document.createElement("p");
    message.textContent = alerta.mensaje || "Alerta sin mensaje";
    item.append(header, message);

    if (withActions) {
        const actions = document.createElement("div");
        actions.className = "section-actions";
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
