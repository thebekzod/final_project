from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .db import Base, engine
from .routes_api_auth import router as auth_router
from .routes_pages import router as pages_router

app = FastAPI(title="NEONHIRE (Clean)")

Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages_router)
app.include_router(auth_router)
