import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from base_de_datos import crear_tablas
from configuracion import RUTA_STATIC
from routers import datos, paginas
from routers.exportacion import router as exportacion_router
from routers.alertas import router as alertas_router

# Importados solo para registrar sus tablas en Base.metadata antes de
# crear_tablas(); catalogo_modelos.py no cubre estos modelos porque no
# tienen CRUD generico expuesto (los usan Informes_mensuales/Dashboard).
from Modulos.Cartera import Cartera  # noqa: F401
from Modulos.Lecturas import Lecturas  # noqa: F401
from Modulos.Rentabilidad import Rentabilidad  # noqa: F401
from Modulos.Sedes import Sedes  # noqa: F401

crear_tablas()

app = FastAPI(title="Gestor de Datos Continental")
app.mount("/static", StaticFiles(directory=RUTA_STATIC), name="static")
app.include_router(paginas.router)
app.include_router(datos.router)
app.include_router(exportacion_router)  # Exportación CSV/Excel
app.include_router(alertas_router)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
