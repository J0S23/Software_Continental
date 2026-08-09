// Vista "Visión general": KPIs (5 primarios siempre visibles + 7 operativos
// colapsados), tendencia financiera, alertas activas y, dentro del panel
// colapsable, el desglose por costos/cartera/cliente/equipo.

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
    const fallidos = resultados.filter((r) => r.status === "rejected");
    if (!fallidos.length) {
        box.hidden = true;
        box.textContent = "";
        return;
    }
    box.hidden = false;
    box.textContent = `No se pudo cargar parte del dashboard (${fallidos.length} de ${resultados.length} secciones): ${fallidos[0].reason.message}`;
}

function renderKpis(data) {
    renderKpiGroup("kpiGrid", [
        ["Facturado", data.facturado_mes, moneda, "money"],
        ["Recaudado", data.recaudado_mes, moneda, "money"],
        ["Cartera", data.cartera_pendiente, moneda, "risk"],
        ["Utilidad", data.utilidad_bruta, moneda, "profit"],
        ["Margen", data.margen_promedio, porcentaje, "profit"],
    ]);

    renderKpiGroup("kpiGridSecundario", [
        ["Contratos activos", data.contratos_activos, entero, "count"],
        ["Equipos instalados", data.equipos_instalados, entero, "count"],
        ["Disponibles", data.equipos_disponibles, entero, "count"],
        ["En reparación", data.equipos_en_reparacion, entero, "risk"],
        ["Clientes en mora", data.clientes_en_mora, entero, "risk"],
        ["Contratos por vencer", data.contratos_por_vencer, entero, "risk"],
        ["Tóneres entregados", data.toneres_entregados_mes, entero, "count"],
    ], "is-compact");
}

function renderKpiGroup(gridId, cards, extraClass = "") {
    const grid = $(gridId);
    if (!grid) return;
    grid.replaceChildren();
    cards.forEach(([label, value, formatter, tone]) => {
        const card = document.createElement("article");
        card.className = `kpi kpi--${tone}${extraClass ? ` ${extraClass}` : ""}`;
        card.append(textSpan(label), textStrong(formatter(value)));
        grid.appendChild(card);
    });
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
            scales: { y: { ticks: { callback: (value) => moneda(value) } } },
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
        div.className = "kv";
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
