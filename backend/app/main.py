"""Instância FastAPI do Regula."""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.api import api_router

app = FastAPI(
    title="Regula API",
    description="Motor de Conformidade e Estruturação de Documentos Acadêmicos (PPGSP/UFPA)",
    version="1.0.0",
)

cors_origins_env = os.getenv(
    "CORS_ORIGINS",
    "https://regula.leadcode.com.br,http://localhost:3000,http://127.0.0.1:3000",
)
origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    return {"status": "ok"}
