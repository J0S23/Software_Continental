# Sirve la pagina principal (SPA/HTML) de la app; el resto de assets estaticos
# los sirve el mount de /static y /vista en app.py.
from fastapi import APIRouter
from fastapi.responses import FileResponse

from configuracion import RUTA_TEMPLATES

router = APIRouter()


@router.get("/")
async def index():
    return FileResponse(RUTA_TEMPLATES / "index.html")
