import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from base_de_datos import crear_tablas
from configuracion import RUTA_STATIC
from routers.datos import router as datos_router
from routers.paginas import router as paginas_router


def crear_app():
    aplicacion = FastAPI(title="Gestor de Datos Continental")
    aplicacion.mount("/static", StaticFiles(directory=RUTA_STATIC), name="static")
    aplicacion.include_router(paginas_router)
    aplicacion.include_router(datos_router)

    crear_tablas()
    return aplicacion


app = crear_app()


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)
