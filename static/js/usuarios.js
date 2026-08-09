// Vista "Usuarios": aprobar/rechazar cuentas pendientes (solo Administrador
// general llega aquí; ver vistaPermitida() en state.js).

async function cargarUsuarios() {
    const container = $("pendingUsersList");
    container.replaceChildren();

    try {
        const data = await apiJson("/auth/pendientes");
        const usuarios = data.usuarios || [];
        if (!usuarios.length) {
            empty(container, "Sin usuarios pendientes.");
            return;
        }

        usuarios.forEach((usuario) => {
            const card = document.createElement("article");
            card.className = "user-card";
            const info = document.createElement("div");
            const name = document.createElement("strong");
            name.textContent = usuario.email;
            const meta = document.createElement("span");
            meta.textContent = usuario.rol || "Rol no indicado";
            info.append(name, meta);

            const select = document.createElement("select");
            select.className = "select";
            select.id = `role-${usuario.id}`;
            ROLE_OPTIONS.forEach((role) => select.appendChild(new Option(role, role)));
            select.value = usuario.rol || ADMIN_ROLE;

            const actions = document.createElement("div");
            actions.className = "section-actions";
            actions.append(
                select,
                actionButton("Aprobar", () => aprobarUsuario(usuario.id), "primary"),
                actionButton("Rechazar", () => rechazarUsuario(usuario.id), "danger")
            );
            card.append(info, actions);
            container.appendChild(card);
        });
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

async function aprobarUsuario(id) {
    const rol = $(`role-${id}`).value;
    try {
        const data = await apiJson(`/auth/${id}/aprobar`, { method: "POST", body: JSON.stringify({ rol }) });
        mostrarToast(data.message || "Usuario aprobado", "success");
        await cargarUsuarios();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}

async function rechazarUsuario(id) {
    try {
        const data = await apiJson(`/auth/${id}/rechazar`, { method: "POST" });
        mostrarToast(data.message || "Usuario rechazado", "success");
        await cargarUsuarios();
    } catch (error) {
        mostrarToast(error.message, "error");
    }
}
