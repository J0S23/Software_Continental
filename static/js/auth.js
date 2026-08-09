// Sesión: login, registro (pendiente de aprobación) y aplicación de permisos
// de navegación al entrar.

function initAuthTabs() {
    const registroRol = $("registroRol");
    registroRol.replaceChildren(...ROLE_OPTIONS.map((rol) => new Option(rol, rol)));

    bind("tabLogin", "click", () => cambiarTabAuth("login"));
    bind("tabRegistro", "click", () => cambiarTabAuth("registro"));
}

function cambiarTabAuth(tab) {
    $("tabLogin").classList.toggle("is-active", tab === "login");
    $("tabRegistro").classList.toggle("is-active", tab === "registro");
    $("loginForm").hidden = tab !== "login";
    $("registroForm").hidden = tab !== "registro";
    setAuthMessage("");
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
        setAuthMessage(error.message, true);
    }
}

async function registrarUsuario(event) {
    event.preventDefault();
    setAuthMessage("");

    const email = $("registroEmail").value.trim();
    const contrasena = $("registroPassword").value;
    const rol = $("registroRol").value;

    try {
        const data = await apiJson("/auth/registro", {
            method: "POST",
            body: JSON.stringify({ email, contrasena, rol }),
        });
        $("registroForm").reset();
        cambiarTabAuth("login");
        setAuthMessage(data.message || "Registro recibido, pendiente de aprobación.");
    } catch (error) {
        setAuthMessage(error.message, true);
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
    cambiarTabAuth("login");
    setAuthMessage(message);
}

function setAuthMessage(message, isError = false) {
    const box = $("authMessage");
    if (!box) return;
    box.hidden = !message;
    box.textContent = message || "";
    box.classList.toggle("is-error", Boolean(isError));
}

async function mostrarApp(usuario) {
    state.usuario = usuario;
    $("authScreen").hidden = true;
    $("appShell").hidden = false;
    $("userRoleLabel").textContent = usuario.rol || "Rol";
    $("userEmailLabel").textContent = usuario.email || "";

    aplicarPermisosRol();
    await cargarConfiguracionInicial();
    cambiarVista(vistaPermitida(state.currentView) ? state.currentView : "dashboard");
}

function aplicarPermisosRol() {
    document.querySelectorAll(".nav-link").forEach((button) => {
        button.hidden = !vistaPermitida(button.dataset.view);
    });
}
