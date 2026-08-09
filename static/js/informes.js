// Vista "Informes": resumen ejecutivo (con variación vs. mes anterior),
// comparativo financiero, tendencia de margen, indicadores operativos,
// recomendaciones (calculadas por el backend), cartera (con gráfica por
// estado), técnico (con gráficas en vez de listas de texto) y las
// consultas puntuales por cliente/equipo.

async function cargarInformes() {
    const periodo = periodoActual();
    actualizarLinksInformes(periodo);

    const [generalResult, anteriorResult, financieraResult, carteraResult, tecnicoResult] = await Promise.allSettled([
        apiJson(`/api/informes/${periodo}`),
        apiJson(`/api/informes/${periodoAnterior(periodo)}`),
        apiJson(`/api/dashboard/${periodo}/serie-financiera?meses=6`),
        apiJson(`/api/informes/${periodo}/cartera`),
        apiJson(`/api/informes/${periodo}/tecnico`),
    ]);

    const general = settledValue(generalResult)?.informe || {};
    const generalAnterior = settledValue(anteriorResult)?.informe || null;
    const financiera = settledValue(financieraResult)?.serie || [];
    const cartera = settledValue(carteraResult)?.informe;
    const tecnico = settledValue(tecnicoResult)?.informe;

    renderResumenEjecutivo(general, generalAnterior);
    renderInformeComposicion(general);
    renderMargenTendencia(financiera);
    renderInformeOperacion(general);
    renderInformeRecomendaciones(general.recomendaciones);
    renderInformeCartera(cartera?.clientes || []);
    renderInformeTecnico(tecnico || {});

    [generalResult, carteraResult, tecnicoResult].forEach((result) => {
        if (result.status === "rejected") mostrarToast(result.reason.message, "error");
    });
}

function periodoAnterior(periodo) {
    const [mesStr, anioStr] = periodo.split("-");
    let mes = parseInt(mesStr, 10) - 1;
    let anio = parseInt(anioStr, 10);
    if (mes < 1) {
        mes = 12;
        anio -= 1;
    }
    return `${String(mes).padStart(2, "0")}-${anio}`;
}

function deltaPorcentual(actual, anterior, invertido = false) {
    if (!anterior) return null;
    const cambio = ((actual - anterior) / Math.abs(anterior)) * 100;
    if (Math.abs(cambio) < 0.05) return null;
    const subiendo = cambio > 0;
    return { subiendo, bueno: invertido ? !subiendo : subiendo, texto: `${Math.abs(cambio).toFixed(1)}% vs. mes anterior` };
}

function deltaPuntos(actual, anterior) {
    if (anterior === null || anterior === undefined) return null;
    const cambio = actual - anterior;
    if (Math.abs(cambio) < 0.05) return null;
    const subiendo = cambio > 0;
    return { subiendo, bueno: subiendo, texto: `${Math.abs(cambio).toFixed(1)} pts vs. mes anterior` };
}

function heroStat(label, valor, formatter, deltaInfo) {
    const card = document.createElement("article");
    card.className = "hero-stat";
    card.append(textSpan(label), textStrong(formatter(valor)));
    if (deltaInfo) {
        const badge = document.createElement("span");
        badge.className = `delta ${deltaInfo.bueno ? "delta--good" : "delta--bad"}`;
        badge.textContent = `${deltaInfo.subiendo ? "▲" : "▼"} ${deltaInfo.texto}`;
        card.appendChild(badge);
    }
    return card;
}

function renderResumenEjecutivo(data, anterior) {
    const grid = $("heroStats");
    if (!grid) return;
    grid.replaceChildren();
    grid.append(
        heroStat("Facturado", data.facturado_mes, moneda, deltaPorcentual(data.facturado_mes, anterior?.facturado_mes)),
        heroStat("Recaudado", data.recaudado_mes, moneda, deltaPorcentual(data.recaudado_mes, anterior?.recaudado_mes)),
        heroStat("Utilidad", data.utilidad_bruta, moneda, deltaPorcentual(data.utilidad_bruta, anterior?.utilidad_bruta)),
        heroStat("Margen", data.margen_promedio, porcentaje, deltaPuntos(data.margen_promedio, anterior?.margen_promedio)),
        heroStat("Cartera pendiente", data.cartera_pendiente, moneda, deltaPorcentual(data.cartera_pendiente, anterior?.cartera_pendiente, true))
    );
}

function renderMargenTendencia(serie) {
    const container = $("margenTendenciaChart");
    if (!container) return;
    container.replaceChildren();
    destruirChart("margenTendencia");

    const conDatos = serie.filter((item) => item.facturado || item.recaudado);
    if (!conDatos.length) {
        empty(container, "Sin datos suficientes para la tendencia.");
        return;
    }

    const canvas = crearCanvas(container, 220);
    state.charts.margenTendencia = new Chart(canvas.getContext("2d"), {
        type: "line",
        data: {
            labels: serie.map((item) => item.periodo),
            datasets: [{
                label: "Margen",
                data: serie.map((item) => item.margen || 0),
                borderColor: chartColor("ok"),
                backgroundColor: chartColor("ok"),
                tension: 0.3,
                pointRadius: 3,
                fill: false,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (ctx) => porcentaje(ctx.raw) } },
            },
            scales: { y: { ticks: { callback: (value) => `${value}%` } } },
        },
    });
}

function renderInformeOperacion(data) {
    renderKpiGroup("informeOperacionGrid", [
        ["Contratos", data.total_contratos, entero, "count"],
        ["Clientes", data.total_clientes, entero, "count"],
        ["Equipos", data.total_equipos, entero, "count"],
        ["Costos", data.costos_mes, moneda, "money"],
        ["Preventivos", data.preventivos_del_mes, entero, "count"],
        ["Correctivos", data.correctivos_del_mes, entero, "risk"],
        ["Contratos por vencer", data.contratos_por_vencer, entero, "risk"],
        ["Clientes en mora", data.clientes_en_mora, entero, "risk"],
        ["Tóneres entregados", data.toneres_entregados, entero, "count"],
    ], "is-compact");
}

function renderInformeRecomendaciones(items) {
    const container = $("informeRecomendaciones");
    if (!container) return;
    container.replaceChildren();
    if (!items || !items.length) {
        empty(container, "Sin recomendaciones activas este periodo.");
        return;
    }
    items.forEach((texto) => {
        const div = document.createElement("div");
        div.className = "rec-item";
        div.textContent = texto;
        container.appendChild(div);
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

function renderInformeComposicion(data) {
    const container = $("informeComposicionChart");
    if (!container) return;
    container.replaceChildren();
    destruirChart("informeComposicion");

    const categorias = ["Facturado", "Recaudado", "Costos", "Utilidad"];
    const valores = [data.facturado_mes || 0, data.recaudado_mes || 0, data.costos_mes || 0, data.utilidad_bruta || 0];
    if (!valores.some(Boolean)) {
        empty(container, "Sin datos financieros para el periodo.");
        return;
    }

    const canvas = crearCanvas(container, 220);
    state.charts.informeComposicion = new Chart(canvas.getContext("2d"), {
        type: "bar",
        data: {
            labels: categorias,
            datasets: [{
                data: valores,
                backgroundColor: [chartColor("accent"), chartColor("brand"), chartColor("danger"), chartColor("ok")],
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: { callbacks: { label: (ctx) => moneda(ctx.raw) } },
            },
            scales: { y: { ticks: { callback: (value) => moneda(value) } } },
        },
    });
}

function renderInformeCartera(clientes) {
    const saldoPorEstado = clientes.reduce((acc, cliente) => {
        const estado = cliente.estado || "sin_estado";
        acc[estado] = (acc[estado] || 0) + (cliente.saldo_pendiente || 0);
        return acc;
    }, {});
    renderRankChart("carteraPorEstado", "carteraPorEstadoChart", saldoPorEstado, moneda, "danger");

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
        td.className = "empty-state-cell";
        td.textContent = "Sin facturas en el periodo";
        emptyRow.appendChild(td);
        body.appendChild(emptyRow);
        return;
    }

    clientes.forEach((cliente) => {
        const row = document.createElement("tr");
        [
            cliente.cliente_id, cliente.facturas_emitidas, cliente.facturas_pagadas, cliente.facturas_vencidas,
            moneda(cliente.saldo_pendiente), cliente.dias_mora_max, cliente.estado,
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

    const chartsGrid = document.createElement("div");
    chartsGrid.className = "grid grid-2-even";
    container.appendChild(chartsGrid);

    crearBloqueGrafica(chartsGrid, "preventivosPorEstado", "Preventivos por estado");
    crearBloqueGrafica(chartsGrid, "equiposConFallas", "Equipos con más fallas");
    crearBloqueGrafica(chartsGrid, "repuestosMasUsados", "Repuestos más usados");
    crearBloqueGrafica(chartsGrid, "costosTecnicosPorContrato", "Costos técnicos por contrato");

    renderRankChart("preventivosPorEstado", "chart-preventivosPorEstado", data.preventivos_por_estado || {}, entero, "brand");
    renderRankChart("equiposConFallas", "chart-equiposConFallas", objectFromList(data.equipos_con_mas_fallas, "equipo_id", "fallas"), entero, "danger");
    renderRankChart("repuestosMasUsados", "chart-repuestosMasUsados", objectFromList(data.repuestos_mas_usados, "descripcion", "cantidad"), entero, "accent");
    renderRankChart("costosTecnicosPorContrato", "chart-costosTecnicosPorContrato", data.costos_tecnicos_por_contrato || {}, moneda, "ok");
}

function crearBloqueGrafica(container, key, titulo) {
    const block = document.createElement("div");
    block.className = "stack";
    const heading = document.createElement("h3");
    heading.textContent = titulo;
    heading.style.fontSize = "0.98rem";
    const chartHost = document.createElement("div");
    chartHost.className = "rank-box";
    chartHost.id = `chart-${key}`;
    block.append(heading, chartHost);
    container.appendChild(block);
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
    actions.className = "section-actions";
    actions.append(anchor("PDF", links.pdf), anchor("Excel", links.excel));
    container.appendChild(actions);
    Object.entries(data || {}).forEach(([key, value]) => {
        container.appendChild(keyValue(labelize(key), formatearValor(value)));
    });
}
