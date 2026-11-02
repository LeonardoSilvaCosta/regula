"""POST /api/v1/validate-ptts — carteira da Resolução 007."""

from fastapi import APIRouter

from app.schemas.document import ValidatePTTRequest
from app.schemas.ptt import PTTValidationResult
from app.services.builder_service import validar_ptts

router = APIRouter()


@router.post("/validate-ptts", response_model=PTTValidationResult)
def validate_ptts(pedido: ValidatePTTRequest) -> PTTValidationResult:
    return validar_ptts(pedido.ptts, pedido.nivel)
