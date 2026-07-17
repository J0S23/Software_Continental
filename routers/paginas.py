from fastapi import APIRouter
from fastapi.responses import FileResponse

from configuracion import RUTA_TEMPLATES

router = APIRouter()


@router.get("/")
async def index():
    return FileResponse(RUTA_TEMPLATES / "index.html")
