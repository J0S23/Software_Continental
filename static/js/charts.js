// Helpers de Chart.js compartidos por dashboard.js e informes.js.

function chartColor(name) {
    const map = {
        brand: "--brand",
        accent: "--accent",
        ok: "--success-600",
        danger: "--danger-600",
        warning: "--warning-600",
    };
    const token = map[name] || name;
    const value = getComputedStyle(document.documentElement).getPropertyValue(token).trim();
    return value || "#14315c";
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

// Barras horizontales genéricas para datos {etiqueta: valor}. Usado por el
// dashboard (costos, cartera por edad, desglose por cliente/equipo) y por
// informes.js (composición de cartera, informe técnico).
function renderRankChart(chartKey, containerId, data, formatter = entero, colorToken = "brand") {
    const container = $(containerId);
    if (!container) return;
    container.replaceChildren();
    destruirChart(chartKey);

    const entries = Object.entries(data || {}).sort((a, b) => (b[1] || 0) - (a[1] || 0)).slice(0, 8);
    if (!entries.length) {
        empty(container, "Sin datos para mostrar.");
        return;
    }

    const canvas = crearCanvas(container, 240);
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
