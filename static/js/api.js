// Cliente HTTP fino sobre fetch: agrega credenciales, decide el content-type
// (deja pasar FormData tal cual) y normaliza los errores del backend
// ({success:false, detail}) a un Error con mensaje legible.

async function apiJson(url, options = {}) {
    const response = await fetch(url, {
        credentials: "same-origin",
        ...options,
        headers: {
            ...(options.body instanceof FormData ? {} : { "Content-Type": "application/json" }),
            ...(options.headers || {}),
        },
    });

    const contentType = response.headers.get("content-type") || "";
    const data = contentType.includes("application/json")
        ? await response.json()
        : { detail: await response.text() };

    if (!response.ok || data.success === false) {
        throw new Error(data.detail || data.error || "No se pudo completar la operación");
    }

    return data;
}
