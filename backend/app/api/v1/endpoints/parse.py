"""POST /api/v1/parse — upload de .docx para JSON estruturado."""

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.schemas.document import AcademicLevel, ParseResponse
from app.services.parser_service import parse_upload

router = APIRouter()


@router.post("/parse", response_model=ParseResponse)
async def parse_documento(
    file: UploadFile = File(...),
    nivel: AcademicLevel = Form(AcademicLevel.mestrado),
) -> ParseResponse:
    nome = (file.filename or "").lower()
    if not nome.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Envie um arquivo .docx.")
    conteudo = await file.read()
    if not conteudo:
        raise HTTPException(status_code=400, detail="O arquivo enviado está vazio.")
    try:
        return parse_upload(conteudo, nivel)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Falha ao interpretar o documento: {exc}") from exc
