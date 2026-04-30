from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import BASE_DIR
from app.routes.reinvite import router as reinvite_router

app = FastAPI(title="GitHub Classroom Reinvite Tool")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
app.include_router(reinvite_router)
