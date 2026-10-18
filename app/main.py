from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, admin, films, media

app = FastAPI(title="Dilitafi API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(films.router)
app.include_router(media.router)


@app.get("/")
def root():
    return {"app": "Dilitafi", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}