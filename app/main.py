from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .api.routes import books, tts, annotations, audio


def create_app() -> FastAPI:
    Base.metadata.create_all(bind=engine)
    app = FastAPI(title=settings.app_name)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(books.router, prefix=settings.api_prefix, tags=["books"])
    app.include_router(tts.router, prefix=settings.api_prefix, tags=["tts"])
    app.include_router(audio.router, prefix=settings.api_prefix, tags=["audio"])
    app.include_router(annotations.router, prefix=settings.api_prefix, tags=["annotations"])

    @app.get("/")
    def read_root():
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
