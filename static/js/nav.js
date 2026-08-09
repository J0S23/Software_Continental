// Navegación entre vistas y carga de metadata (/api/tipos, /api/configuracion).

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

function cambiarVista(view) {
    if (!VIEW_META[view] || !vistaPermitida(view)) return;
    state.currentView = view;

    const grupo = grupoPorVista(view);
    const sectionId = grupo ? "datos" : view;

    document.querySelectorAll(".nav-link").forEach((button) => {
        button.classList.toggle("is-active", button.dataset.view === view);
    });
    document.querySelectorAll(".view").forEach((section) => {
        section.classList.toggle("is-active", section.id === `view-${sectionId}`);
    });

    $("activeViewTitle").textContent = VIEW_META[view].title;
    $("activeViewEyebrow").textContent = VIEW_META[view].eyebrow;

    if (grupo) {
        $("datosEyebrow").textContent = grupo.eyebrow;
        $("datosTitle").textContent = grupo.title;
        renderModuleNav(grupo);
        const disponibles = tiposDelGrupo(grupo);
        if (!disponibles.includes(state.tipoActual)) {
            seleccionarTipo(disponibles[0] || "");
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

function renderModuleNav(grupo) {
    const selector = $("tipoSelector");
    const nav = $("tipoGroups");
    selector.replaceChildren(new Option("Selecciona módulo", ""));
    nav.replaceChildren();

    const keys = tiposDelGrupo(grupo);
    keys.forEach((key) => {
        selector.appendChild(new Option(state.tipos[key], key));
        nav.appendChild(crearModuloButton(key));
    });
}

function crearModuloButton(key) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "module-btn";
    button.dataset.tipo = key;
    const label = document.createElement("span");
    label.textContent = state.tipos[key];
    const code = document.createElement("small");
    code.textContent = key;
    button.append(label, code);
    button.addEventListener("click", () => seleccionarTipo(key));
    return button;
}
