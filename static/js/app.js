// Punto de entrada: fija el periodo por defecto, conecta todos los
// listeners y arranca verificando si ya hay sesión.

document.addEventListener("DOMContentLoaded", () => {
    setDefaultPeriod();
    initAuthTabs();
    bindStaticEvents();
    initSidebarToggle();
    initNavGroups();
    verificarSesion();
});

function setDefaultPeriod() {
    const today = new Date();
    $("periodInput").value = `${String(today.getMonth() + 1).padStart(2, "0")}-${today.getFullYear()}`;
}

function periodoActual() {
    const value = $("periodInput").value.trim();
    return value || `${String(new Date().getMonth() + 1).padStart(2, "0")}-${new Date().getFullYear()}`;
}

function bindStaticEvents() {
    bind("loginForm", "submit", iniciarSesion);
    bind("registroForm", "submit", registrarUsuario);
    bind("logoutBtn", "click", () => cerrarSesion());
    bind("refreshBtn", "click", refrescarVistaActual);
    bind("periodInput", "change", () => {
        syncAutomationPeriod();
        refrescarVistaActual();
    });

    document.querySelectorAll(".nav-link").forEach((button) => {
        button.addEventListener("click", () => cambiarVista(button.dataset.view));
    });

    document.querySelector(".collapse")?.addEventListener("toggle", (event) => {
        if (!event.target.open) return;
        ["costs", "cartera", "ingresosCliente", "rentabilidadCliente", "correctivosEquipo", "toneresCliente"].forEach((key) => {
            state.charts[key]?.resize();
        });
    });

    bind("tipoSelector", "change", (event) => seleccionarTipo(event.target.value));
    bind("formDatos", "submit", guardarRegistro);
    bind("resetFormBtn", "click", limpiarFormulario);
    bind("cancelEditBtn", "click", limpiarFormulario);
    bind("recordSearch", "input", renderTabla);
    bind("paginaAnteriorBtn", "click", irPaginaAnterior);
    bind("paginaSiguienteBtn", "click", irPaginaSiguiente);
    bind("exportCurrentBtn", "click", exportarTipoActual);
    bind("downloadTemplateBtn", "click", descargarPlantilla);
    bind("importBtn", "click", importarExcel);
    bind("previewFacturaBtn", "click", previsualizarFacturacion);
    bind("generarFacturaBtn", "click", generarFacturacionAutomatica);
    bind("autoContratoId", "input", resetFacturaPreview);
    bind("autoPeriodo", "input", resetFacturaPreview);

    bind("loadReportsBtn", "click", cargarInformes);
    bind("loadClientReportBtn", "click", cargarInformeCliente);
    bind("loadEquipoReportBtn", "click", cargarInformeEquipo);
    bind("loadAlertsBtn", "click", cargarAlertas);
    bind("includeDiscardedFilter", "change", cargarAlertas);
    bind("alertLevelFilter", "change", renderAlertasActivas);
    bind("loadUsersBtn", "click", cargarUsuarios);

    bind("closeAdjuntosBtn", "click", cerrarAdjuntos);
    bind("adjuntosForm", "submit", subirAdjunto);
    bind("closeHistoryBtn", "click", cerrarHistorial);
}
