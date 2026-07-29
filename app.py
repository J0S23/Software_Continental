# Punto de entrada de la aplicacion FastAPI: monta archivos estaticos,
# registra los routers (en el orden correcto) y arranca uvicorn.
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from base_de_datos import crear_tablas
from configuracion import RUTA_STATIC, RUTA_VISTA
from routers import datos, paginas
from routers.exportacion import router as exportacion_router
from routers.alertas import router as alertas_router
from routers.facturacion_automatica import router as facturacion_automatica_router
from routers.adjuntos import router as adjuntos_router
from routers.auth import router as auth_router

# Se importan solo para que SQLAlchemy registre estos modelos en Base.metadata
# antes de crear_tablas(); no se usan directamente en este archivo.
from Modulos.Cartera import Cartera  # noqa: F401
from Modulos.Lecturas import Lecturas  # noqa: F401
from Modulos.Rentabilidad import Rentabilidad  # noqa: F401
from Modulos.Sedes import Sedes  # noqa: F401

crear_tablas()

app = FastAPI(title="Gestor de Datos Continental")
app.mount("/static", StaticFiles(directory=RUTA_STATIC), name="static")
# html=True permite servir index.html de una carpeta al pedir su ruta directorio.
app.mount("/vista", StaticFiles(directory=RUTA_VISTA, html=True), name="vista")
app.include_router(paginas.router)
# exportacion/alertas/facturacion_automatica van antes que datos.router porque
# datos.router define un catch-all GET /api/{tipo}: si se registrara primero,
# interceptaria rutas de 2 segmentos como /api/alertas antes de llegar a su
# propio router (Starlette resuelve las rutas en orden de registro).
app.include_router(exportacion_router)
app.include_router(alertas_router)
app.include_router(facturacion_automatica_router)
app.include_router(adjuntos_router)
app.include_router(auth_router)
app.include_router(datos.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)