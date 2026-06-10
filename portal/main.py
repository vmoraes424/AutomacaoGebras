"""Aplicação FastAPI do portal Gebras (interfaces HTTP)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from portal.interfaces.http.routers import forms, health, pipedrive


def create_app() -> FastAPI:
    app = FastAPI(
        title="Gebras Portal API",
        description="API do formulário web — DDD pragmático (formulario + crm)",
        version="0.2.0",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(pipedrive.router)
    app.include_router(forms.router)
    return app


app = create_app()
