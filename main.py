from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (registra las tablas en Base.metadata)
from app.database import Base, engine
from app.routers import auth, tareas, usuarios


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Tareas API", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(tareas.router)


@app.get("/")
async def read_root():
    return {"Hello": "World"}
