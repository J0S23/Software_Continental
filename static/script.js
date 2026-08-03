let tipos = {};
let tipoActual = "";
let configuracion = {};

// Paginacion de la tabla de registros: limit fijo, skip se mueve de a una
// pagina por click. totalRegistros lo informa el backend en cada respuesta.
const LIMITE_PAGINA = 100;
let skipActual = 0;
let totalRegistros = 0;

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("tipoSelector").addEventListener("change", cambiarTipo);
    document.getElementById("formDatos").addEventListener("submit", agregarDato);
    document.getElementById("limpiarBtn").addEventListener("click", limpiarFormulario);
    document.getElementById("paginaAnteriorBtn").addEventListener("click", irPaginaAnterior);
    document.getElementById("paginaSiguienteBtn").addEventListener("click", irPaginaSiguiente);

    document.getElementById("loginForm").addEventListener("submit", iniciarSesion);
    document.getElementById("registroForm").addEventListener("submit", registrarUsuario);
    document.getElementById("mostrarRegistroBtn").addEventListener("click", () => mostrarAuthCard("registro"));
    document.getElementById("mostrarLoginBtn").addEventListener("click", () => mostrarAuthCard("login"));
    // La app (main) queda oculta hasta iniciar sesion; cargarTipos() se llama
    // recien cuando el login responde bien (ver mostrarSesionActiva).
});

function mostrarAuthCard(cual) {
    document.getElementById("loginCard").hidden = cual !== "login";
    document.getElementById("registroCard").hidden = cual !== "registro";
}

async function iniciarSesion(event) {
    event.preventDefault();

    const email = document.getElementById("loginEmail").value;
    const contrasena = document.getElementById("loginPassword").value;

    try {
        const response = await fetch("/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, contrasena }),
        });
        const data = await leerRespuesta(response);
        mostrarSesionActiva(data.email, data.rol);
    } catch (error) {
        mostrarMensaje(error.message, "error", "authMessageArea");
    }
}

async function registrarUsuario(event) {
    event.preventDefault();

    const email = document.getElementById("registroEmail").value;
    const contrasena = document.getElementById("registroPassword").value;
    const rol = document.getElementById("registroRol").value;

    try {
        const response = await fetch("/auth/registro", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, contrasena, rol }),
        });
        await leerRespuesta(response);

        mostrarMensaje("Registro recibido, pendiente de aprobación por un administrador.", "info", "authMessageArea");
        document.getElementById("registroForm").reset();
        mostrarAuthCard("login");
    } catch (error) {
        mostrarMensaje(error.message, "error", "authMessageArea");
    }
}

function mostrarSesionActiva(email, rol) {
    document.getElementById("authSection").hidden = true;
    document.getElementById("appMain").hidden = false;

    const sesionInfo = document.getElementById("sesionInfo");
    sesionInfo.hidden = false;
    document.getElementById("sesionEmailLabel").textContent = `${email} (${rol})`;

    cargarTipos();
}

async function cargarTipos() {
    try {
        const [tiposResponse, configuracionResponse] = await Promise.all([
            fetch("/api/tipos"),
            fetch("/api/configuracion"),
        ]);

        if (!tiposResponse.ok || !configuracionResponse.ok) {
            throw new Error("No se pudo cargar la configuracion inicial");
        }

        tipos = await tiposResponse.json();
        configuracion = await configuracionResponse.json();

        const selector = document.getElementById("tipoSelector");
        const tipoList = document.getElementById("tipoList");
        selector.innerHTML = '<option value="">Selecciona</option>';
        tipoList.innerHTML = "";

        Object.entries(tipos).forEach(([key, etiqueta]) => {
            selector.appendChild(new Option(etiqueta, key));

            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = "tipo-btn";
            btn.textContent = etiqueta;
            btn.addEventListener("click", () => seleccionarTipo(key));
            tipoList.appendChild(btn);
        });
    } catch (error) {
        mostrarMensaje(`Error cargando tipos: ${error.message}`, "error");
    }
}

function seleccionarTipo(tipo) {
    document.getElementById("tipoSelector").value = tipo;
    cambiarTipo();
}

async function cambiarTipo() {
    tipoActual = document.getElementById("tipoSelector").value;
    skipActual = 0; // cada tipo tiene su propia paginacion, siempre arranca en la primera pagina
    document.querySelectorAll(".tipo-btn").forEach((btn) => {
        btn.classList.toggle("active", btn.textContent === tipos[tipoActual]);
    });

    document.getElementById("formSection").hidden = !tipoActual;
    document.getElementById("dataTableSection").hidden = !tipoActual;

    if (!tipoActual) {
        return;
    }

    if (!configuracion[tipoActual]) {
        mostrarMensaje("No hay configuracion para este tipo de dato", "error");
        return;
    }

    cargarFormulario();
    await obtenerDatos();
}

function cargarFormulario() {
    const formFields = document.getElementById("formFields");
    formFields.innerHTML = "";

    configuracion[tipoActual].forEach((campo) => {
        const div = document.createElement("div");
        div.className = "form-group";

        const label = document.createElement("label");
        label.htmlFor = campo.nombre;
        label.textContent = obtenerEtiqueta(campo);

        const input = crearControl(campo);
        div.append(label, input);
        formFields.appendChild(div);
    });
}

function crearControl(campo) {
    if (campo.tipo === "select" || campo.tipo === "boolean") {
        const select = document.createElement("select");
        select.id = campo.nombre;
        select.name = campo.nombre;
        select.required = campo.requerido !== false;
        select.appendChild(new Option("Selecciona", ""));
        const opciones = campo.tipo === "boolean" ? (campo.opciones || ["Si", "No"]) : campo.opciones;
        opciones.forEach((opcion) => select.appendChild(new Option(opcion, opcion)));
        return select;
    }

    const input = document.createElement("input");
    input.type = campo.tipo;
    input.id = campo.nombre;
    input.name = campo.nombre;
    input.placeholder = obtenerEtiqueta(campo);
    input.required = campo.requerido !== false;

    if (campo.tipo === "number") {
        input.step = "any";
    }

    return input;
}

async function agregarDato(event) {
    event.preventDefault();

    const data = {};
    configuracion[tipoActual].forEach((campo) => {
        data[campo.nombre] = document.getElementById(campo.nombre).value;
    });

    try {
        const response = await fetch(`/api/${tipoActual}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        const result = await leerRespuesta(response);

        mostrarMensaje(result.message, "success");
        limpiarFormulario();
        await obtenerDatos();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function obtenerDatos() {
    try {
        const response = await fetch(`/api/${tipoActual}?skip=${skipActual}&limit=${LIMITE_PAGINA}`);
        const data = await leerRespuesta(response);
        totalRegistros = data.total ?? data.datos.length;
        llenarTabla(data.datos);
        actualizarControlesPaginacion();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

function actualizarControlesPaginacion() {
    const controles = document.getElementById("paginationControls");
    controles.hidden = totalRegistros <= LIMITE_PAGINA;

    const desde = totalRegistros === 0 ? 0 : skipActual + 1;
    const hasta = Math.min(skipActual + LIMITE_PAGINA, totalRegistros);
    document.getElementById("paginacionInfo").textContent = `${desde}-${hasta} de ${totalRegistros}`;

    document.getElementById("paginaAnteriorBtn").disabled = skipActual === 0;
    document.getElementById("paginaSiguienteBtn").disabled = skipActual + LIMITE_PAGINA >= totalRegistros;
}

async function irPaginaAnterior() {
    skipActual = Math.max(0, skipActual - LIMITE_PAGINA);
    await obtenerDatos();
}

async function irPaginaSiguiente() {
    if (skipActual + LIMITE_PAGINA >= totalRegistros) {
        return;
    }
    skipActual += LIMITE_PAGINA;
    await obtenerDatos();
}

function llenarTabla(datos) {
    const tableHead = document.getElementById("tableHead");
    const tableBody = document.getElementById("tableBody");
    const campos = configuracion[tipoActual];

    tableHead.innerHTML = "";
    tableBody.innerHTML = "";

    const headerRow = document.createElement("tr");
    ["ID", ...campos.map(obtenerEtiqueta), "Acciones"].forEach((label) => {
        const th = document.createElement("th");
        th.textContent = label;
        headerRow.appendChild(th);
    });
    tableHead.appendChild(headerRow);

    if (datos.length === 0) {
        const tr = document.createElement("tr");
        const td = document.createElement("td");
        td.colSpan = campos.length + 2;
        td.className = "empty-state";
        td.textContent = "No hay registros";
        tr.appendChild(td);
        tableBody.appendChild(tr);
        return;
    }

    datos.forEach((item) => {
        const tr = document.createElement("tr");
        agregarCelda(tr, item.id);
        campos.forEach((campo) => agregarCelda(tr, item[campo.nombre]));

        const acciones = document.createElement("td");
        acciones.className = "table-actions";
        const eliminarBtn = document.createElement("button");
        eliminarBtn.type = "button";
        eliminarBtn.className = "btn btn-danger btn-small";
        eliminarBtn.textContent = "Eliminar";
        eliminarBtn.addEventListener("click", () => eliminarDato(item.id));
        acciones.appendChild(eliminarBtn);
        tr.appendChild(acciones);

        tableBody.appendChild(tr);
    });
}

function agregarCelda(row, value) {
    const td = document.createElement("td");
    td.textContent = value ?? "";
    row.appendChild(td);
}

function obtenerEtiqueta(campo) {
    return campo.etiqueta || campo.label;
}

async function eliminarDato(id) {
    try {
        const response = await fetch(`/api/${tipoActual}/${id}`, { method: "DELETE" });
        const data = await leerRespuesta(response);
        mostrarMensaje(data.message, "success");
        await obtenerDatos();
    } catch (error) {
        mostrarMensaje(error.message, "error");
    }
}

async function leerRespuesta(response) {
    const data = await response.json();

    if (!response.ok || data.success === false) {
        throw new Error(data.detail || data.error || "No se pudo completar la operacion");
    }

    return data;
}

function limpiarFormulario() {
    document.getElementById("formDatos").reset();
}

function mostrarMensaje(mensaje, tipo = "info", contenedorId = "messageArea") {
    const messageArea = document.getElementById(contenedorId);
    const div = document.createElement("div");
    div.className = `message ${tipo}`;
    div.textContent = mensaje;
    messageArea.appendChild(div);

    setTimeout(() => div.remove(), 4000);
}
