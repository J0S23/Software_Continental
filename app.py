# Punto de entrada de la aplicacion FastAPI: monta archivos estaticos,
# registra los routers (en el orden correcto) y arranca uvicorn.
import time

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

# --- Rate limiting (slowapi) ---
# _rate_limit_exceeded_handler: convierte la excepcion RateLimitExceeded (la que lanza el decorador @limiter.limit(...) 
# en routers/auth.py cuando se excede el limite) en una respuesta HTTP 429 limpia. Sin registrarlo, esa excepcion no tiene 
# quien la atrape y FastAPI la deja subir como un 500.
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from base_de_datos import crear_tablas, logger
from configuracion import ORIGENES_PERMITIDOS, RUTA_STATIC, RUTA_VISTA, limiter
from routers import datos, paginas
from routers.exportacion import router as exportacion_router
from routers.informes import router as informes_router
from routers.dashboard import router as dashboard_router
from routers.importacion import router as importacion_router
from routers.alertas import router as alertas_router
from routers.facturacion_automatica import router as facturacion_automatica_router
from routers.adjuntos import router as adjuntos_router
from routers.auth import router as auth_router
from routers.salud import router as salud_router

# Se importan solo para que SQLAlchemy registre estos modelos en Base.metadata
# antes de crear_tablas(); no se usan directamente en este archivo.
from Modulos.Cartera import Cartera  # noqa: F401
from Modulos.Lecturas import Lecturas  # noqa: F401
from Modulos.Rentabilidad import Rentabilidad  # noqa: F401
from Modulos.Sedes import Sedes  # noqa: F401

crear_tablas()

app = FastAPI(title="Gestor de Datos Continental")


# Estandariza la forma de toda respuesta de error HTTPException (usada en
# todos los routers) para que el frontend siempre reciba "success" ademas
# de "detail", sin cambiar los status_code ni los mensajes existentes.
# Se registra sobre la clase base de Starlette (no fastapi.HTTPException,
# que es una subclase) porque errores que el propio enrutador levanta
# internamente (404 por ruta inexistente, 405 por metodo no permitido) son
# instancias de la clase base: si el handler se registrara sobre la
# subclase de fastapi, esos casos no calzarian por MRO y caerian al
# handler por defecto de FastAPI, sin el campo "success".
@app.exception_handler(StarletteHTTPException)
async def manejador_http_exception(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "detail": exc.detail},
    )


# Red de seguridad para cualquier excepcion no anticipada (bugs, fallos de
# DB, etc.): se registra completa en el log para diagnostico, pero al
# cliente solo se le devuelve un mensaje generico (nunca str(exc)) para no
# filtrar detalles internos (rutas, queries, stack).
@app.exception_handler(Exception)
async def manejador_excepcion_no_controlada(request: Request, exc: Exception):
    logger.exception(
        "Error no controlado en %s %s", request.method, request.url.path, exc_info=exc
    )
    return JSONResponse(
        status_code=500,
        content={"success": False, "detail": "Ocurrió un error interno. Contacta al administrador."},
    )


# Log de accesos: un renglon por request con metodo, ruta, codigo de
# respuesta y duracion. A proposito NO se registra el body (puede traer
# contraseñas u otros datos sensibles, ej. /auth/login, /auth/registro).
@app.middleware("http")
async def middleware_log_accesos(request: Request, call_next):
    inicio = time.perf_counter()
    response = await call_next(request)
    duracion_ms = (time.perf_counter() - inicio) * 1000
    logger.info(
        "%s %s -> %s (%.1fms)",
        request.method, request.url.path, response.status_code, duracion_ms,
    )
    return response


# --- Rate limiting (slowapi), continuacion ---
# app.state.limiter: el decorador @limiter.limit(...) en routers/auth.py busca el Limiter aqui (en app.state) cuando corre; si no esta, revienta.
# add_exception_handler: conecta RateLimitExceeded con el handler de arriba.
# SlowAPIMiddleware: es lo que realmente cuenta las peticiones por IP y decide cuando disparar RateLimitExceeded 
# (sin este middleware el decorador no tiene efecto, aunque este puesto en el endpoint).
# Las 3 lineas van juntas y en este orden porque cada una depende de que la anterior ya haya corrido.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS: se agrega DESPUES de SlowAPIMiddleware a proposito. En Starlette el
# middleware agregado mas tarde envuelve (queda mas afuera) al agregado
# antes, y por lo tanto se ejecuta PRIMERO en cada request -- el orden de
# add_middleware() es el inverso al de ejecucion. Poniendolo aqui, CORS
# queda como la capa mas externa: responde el preflight OPTIONS antes de
# que la request llegue al rate limiter o a cualquier otro middleware.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGENES_PERMITIDOS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=RUTA_STATIC), name="static")
# html=True permite servir index.html de una carpeta al pedir su ruta directorio.
app.mount("/vista", StaticFiles(directory=RUTA_VISTA, html=True), name="vista")
app.include_router(paginas.router)
# exportacion/informes/dashboard/importacion/alertas/facturacion_automatica van
# antes que datos.router porque datos.router define un catch-all GET /api/{tipo}:
# si se registrara primero, interceptaria rutas de 2 segmentos como /api/alertas
# antes de llegar a su propio router (Starlette resuelve las rutas en orden de
# registro). Los routers nuevos usan rutas de 3+ segmentos (/api/informes/{periodo},
# /api/importar/{tipo}) asi que en realidad no colisionan con el catch-all de
# 2 segmentos, pero se registran aqui igual por consistencia con el resto.
app.include_router(exportacion_router)
app.include_router(informes_router)
app.include_router(dashboard_router)
app.include_router(importacion_router)
app.include_router(alertas_router)
app.include_router(facturacion_automatica_router)
app.include_router(adjuntos_router)
app.include_router(auth_router)
app.include_router(salud_router)
app.include_router(datos.router)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5000)