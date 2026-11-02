"""POST /api/v1/generate — JSON de metadados para download do DOCX."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.schemas.document import GenerateRequest
from app.services.builder_service import gerar_buffer

router = APIRouter()

_MEDIA_TYPE = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
_FILENAME = "Documento_Padronizado_PPGSP.docx"


@router.post("/generate")
def generate_documento(pedido: GenerateRequest) -> StreamingResponse:
    try:
        buffer = gerar_buffer(pedido)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Falha ao gerar o documento: {exc}") from exc
    return StreamingResponse(
        buffer,
        media_type=_MEDIA_TYPE,
        headers={"Content-Disposition": f'attachment; filename="{_FILENAME}"'},
    )
