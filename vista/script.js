document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.addEventListener("click", () => cambiarTab(btn.dataset.tab));
    });

    document.getElementById("refrescarActivas").addEventListener("click", cargarActivas);
    document.getElementById("incluirDescartadas").addEventListener("change", cargarActivas);
    document.getElementById("refrescarGuardadas").addEventListener("click", cargarGuardadas);
    document.getElementById("formConsola").addEventListener("submit", enviarConsola);

    cargarActivas();
});

function cambiarTab(tab) {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.tab === tab);
    });
    document.querySelectorAll(".tab-panel").forEach((panel) => {
        panel.classList.toggle("active", panel.id === `panel-${tab}`);
    });

    if (tab === "guardadas") {
        cargarGuardadas();
    }
}

/* ---------- Alertas activas ---------- */

async function cargarActivas() {
    const incluirDescartadas = document.getElementById("incluirDescartadas").checked;
    const lista = document.getElementById("listaActivas");
    const resumen = document.getElementById("resumenActivas");

    try {
        const data = await peticion("GET", `/api/alertas?incluir_descartadas=${incluirDescartadas}`);
        resumen.textContent = `${data.total} alerta(s) - ${data.criticas} critica(s) - generado ${formatearFecha(data.generado_en)}`;
        renderizarAlertas(lista, data.alertas, { origen: "activas" });
    } catch (error) {
        mostrarMensaje(`Error cargando alertas: ${error.message}`, "error");
    }
}

/* ---------- Guardadas ---------- */

async function cargarGuardadas() {
    const lista = document.getElementById("listaGuardadas");
    const resumen = document.getElementById("resumenGuardadas");

    try {
        const data = await peticion("GET", "/api/alertas/guardadas");
        resumen.textContent = `${data.alertas.length} alerta(s) guardada(s)`;
        renderizarAlertas(lista, data.alertas, { origen: "guardadas" });
    } catch (error) {
        mostrarMensaje(`Error cargando guardadas: ${error.message}`, "error");
    }
}

/* ---------- Render comun ---------- */

function renderizarAlertas(contenedor, alertas, { origen }) {
    contenedor.innerHTML = "";

    if (!alertas || alertas.length === 0) {
        const vacio = document.createElement("div");
        vacio.className = "empty-state";
        vacio.textContent = "No hay alertas para mostrar.";
        contenedor.appendChild(vacio);
        return;
    }

    alertas.forEach((alerta) => contenedor.appendChild(crearTarjetaAlerta(alerta, origen)));
}

function crearTarjetaAlerta(alerta, origen) {
    const card = document.createElement("div");
    card.className = `alerta-card nivel-${alerta.nivel || "info"}`;
    if (alerta.leida) card.classList.add("leida");

    const info = document.createElement("div");
    info.className = "alerta-info";

    const tipo = document.createElement("span");
    tipo.className = "alerta-tipo";
    tipo.textContent = `${alerta.tipo} - ref: ${alerta.referencia_id ?? "-"}`;

    const mensaje = document.createElement("span");
    mensaje.className = "alerta-mensaje";
    mensaje.textContent = alerta.mensaje;

    const flags = document.createElement("div");
    flags.className = "alerta-flags";
    flags.append(
        crearFlag("leida", alerta.leida),
        crearFlag("guardada", alerta.guardada),
        crearFlag("descartada", alerta.descartada),
    );

    info.append(tipo, mensaje, flags);

    const acciones = document.createElement("div");
    acciones.className = "alerta-acciones";

    acciones.appendChild(
        crearBotonEstado(alerta, "leida", alerta.leida ? "Marcar no leida" : "Marcar leida", "btn-secondary", origen),
    );
    acciones.appendChild(
        crearBotonEstado(alerta, "guardada", alerta.guardada ? "Quitar guardado" : "Guardar", "btn-success", origen),
    );
    acciones.appendChild(
        crearBotonEstado(alerta, "descartada", alerta.descartada ? "Restaurar" : "Descartar", "btn-danger", origen),
    );

    card.append(info, acciones);
    return card;
}

function crearFlag(nombre, activo) {
    const span = document.createElement("span");
    span.className = `flag${activo ? " on" : ""}`;
    span.textContent = nombre;
    return span;
}

function crearBotonEstado(alerta, campo, etiqueta, clase, origen) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `btn btn-small ${clase}`;
    btn.textContent = etiqueta;
    btn.addEventListener("click", async () => {
        try {
            const cambios = { tipo: alerta.tipo, referencia_id: alerta.referencia_id };
            cambios[campo] = !alerta[campo];

            // Guarda un snapshot del mensaje/nivel al guardar, para poder
            // mostrar la alerta en "Guardadas" aunque luego deje de calcularse.
            if (campo === "guardada" && cambios.guardada) {
                cambios.mensaje = alerta.mensaje;
                cambios.nivel = alerta.nivel;
            }

            await peticion("POST", "/api/alertas/estado", cambios);
            mostrarMensaje(`Alerta actualizada (${campo})`, "success");

            if (origen === "guardadas") {
                await cargarGuardadas();
            } else {
                await cargarActivas();
            }
        } catch (error) {
            mostrarMensaje(`No se pudo actualizar la alerta: ${error.message}`, "error");
        }
    });
    return btn;
}

/* ---------- Consola API ---------- */

async function enviarConsola(event) {
    event.preventDefault();

    const metodo = document.getElementById("consolaMetodo").value;
    const ruta = document.getElementById("consolaRuta").value.trim();
    const bodyTexto = document.getElementById("consolaBody").value.trim();
    const resultado = document.getElementById("consolaResultado");

    let body;
    if (bodyTexto) {
        try {
            body = JSON.parse(bodyTexto);
        } catch (error) {
            resultado.textContent = `Body invalido: ${error.message}`;
            return;
        }
    }

    try {
        const data = await peticion(metodo, ruta, body);
        resultado.textContent = JSON.stringify(data, null, 2);
        agregarHistorial(metodo, ruta, true, data);
    } catch (error) {
        resultado.textContent = `Error: ${error.message}`;
        agregarHistorial(metodo, ruta, false, error.detalle || { error: error.message });
    }
}

function agregarHistorial(metodo, ruta, ok, data) {
    const historial = document.getElementById("consolaHistorial");
    const item = document.createElement("details");
    item.className = `historial-item ${ok ? "ok" : "error"}`;

    const summary = document.createElement("summary");
    summary.textContent = `${new Date().toLocaleTimeString()} - ${metodo} ${ruta} - ${ok ? "OK" : "ERROR"}`;

    const pre = document.createElement("pre");
    pre.textContent = JSON.stringify(data, null, 2);

    item.append(summary, pre);
    historial.prepend(item);
}

/* ---------- Utilidades ---------- */

async function peticion(metodo, ruta, body) {
    const opciones = { method: metodo, headers: {} };

    if (body !== undefined) {
        opciones.headers["Content-Type"] = "application/json";
        opciones.body = JSON.stringify(body);
    }

    const response = await fetch(ruta, opciones);
    const data = await response.json().catch(() => ({}));

    if (!response.ok || data.success === false) {
        const error = new Error(data.detail || data.error || `HTTP ${response.status}`);
        error.detalle = data;
        throw error;
    }

    return data;
}

function formatearFecha(iso) {
    if (!iso) return "-";
    try {
        return new Date(iso).toLocaleString();
    } catch {
        return iso;
    }
}

function mostrarMensaje(mensaje, tipo = "info") {
    const messageArea = document.getElementById("messageArea");
    const div = document.createElement("div");
    div.className = `message ${tipo}`;
    div.textContent = mensaje;
    messageArea.appendChild(div);
    setTimeout(() => div.remove(), 4000);
}
