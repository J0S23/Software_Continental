// Utilidades compartidas: acceso al DOM, formateo y helpers genéricos.
// Cargado primero: todo lo demás asume que estas funciones ya existen.

function $(id) {
    return document.getElementById(id);
}

function bind(id, eventName, handler) {
    const element = $(id);
    if (element) element.addEventListener(eventName, handler);
}

function mostrarToast(message, type = "info") {
    const stack = $("toastStack");
    const toast = document.createElement("div");
    toast.className = `toast toast--${type}`;
    toast.textContent = message;
    stack.appendChild(toast);
    setTimeout(() => toast.remove(), 4500);
}

function empty(container, message) {
    const div = document.createElement("div");
    div.className = "empty-state";
    div.textContent = message;
    container.appendChild(div);
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
    item.className = "kv";
    item.append(textSpan(label), textStrong(value ?? "N/D"));
    return item;
}

function pill(text, tone = "") {
    const span = document.createElement("span");
    span.className = tone ? `pill pill--${tone}` : "pill";
    span.textContent = text;
    return span;
}

function actionButton(text, handler, variant = "ghost") {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `btn btn--${variant} btn--sm`;
    button.textContent = text;
    button.addEventListener("click", handler);
    return button;
}

function anchor(text, href) {
    const link = document.createElement("a");
    link.className = "link-btn";
    link.href = href;
    link.textContent = text;
    return link;
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

function fechaToIso(fecha) {
    return new Date(`${fecha}T00:00:00`).toISOString();
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

function valorParaControl(value, campo) {
    if (value === null || value === undefined) return "";
    if ((campo.tipo || "") === "date") return String(value).slice(0, 10);
    if ((campo.tipo || "") === "boolean") return value === true ? "Si" : value === false ? "No" : value;
    return value;
}

function objectFromList(list = [], keyField, valueField) {
    return list.reduce((acc, item) => {
        acc[item[keyField]] = item[valueField];
        return acc;
    }, {});
}

function settledValue(result) {
    return result.status === "fulfilled" ? result.value : null;
}

function ultimaSerieConDatos(serie = [], key) {
    return [...serie].reverse().find((item) => Object.keys(item[key] || {}).length) || serie[serie.length - 1] || null;
}
