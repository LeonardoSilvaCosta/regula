"""Agregador das rotas da versão 1."""

from fastapi import APIRouter

from app.api.v1.endpoints import generate, parse, validate

api_router = APIRouter()
api_router.include_router(parse.router, tags=["parse"])
api_router.include_router(validate.router, tags=["validacao"])
api_router.include_router(generate.router, tags=["generate"])
