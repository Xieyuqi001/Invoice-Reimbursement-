from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import init_db
from app.routers import records
import os

app = FastAPI(title="Fapiao Manager", description="Invoice and Order Image Management Tool")

app.include_router(records.router, prefix="/api")

static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.on_event("startup")
def startup():
    init_db()

@app.get("/")
async def root():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Fapiao Manager API"}
