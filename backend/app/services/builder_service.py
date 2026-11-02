"""Validação da carteira de PTTs e geração do DOCX em buffer."""

from __future__ import annotations

import os
import tempfile
from io import BytesIO
from pathlib import Path

from core.ptt_schema import validar_carteira_produtos
from generators.dissertacao.builder import gerar_documento_dissertacao
from generators.qualificacao.builder import gerar_documento_qualificacao
from generators.tese.builder import gerar_documento_tese

from app.schemas.document import AcademicLevel, DocumentType, GenerateRequest
from app.schemas.ptt import PTTItem, PTTValidationResult

BACKEND_DIR = Path(__file__).resolve().parents[2]
_MIN_PRODUTOS = {
    AcademicLevel.mestrado: 4,
    AcademicLevel.doutorado: 8,
}


def proporcao_impacto_alto(ptts: list[PTTItem] | list[dict]) -> float:
    total = len(ptts)
    if total == 0:
        return 0.0
    altos = 0
    for item in ptts:
        impacto = item.get("impacto") if isinstance(item, dict) else item.impacto
        if str(impacto or "").strip().lower() == "alto":
            altos += 1
    return altos / total


def validar_ptts(ptts: list[PTTItem], nivel: AcademicLevel) -> PTTValidationResult:
    payload = [item.model_dump() for item in ptts]
    minimo = _MIN_PRODUTOS[nivel]
    valido, mensagem = validar_carteira_produtos(payload, min_produtos=minimo)
    return PTTValidationResult(
        valido=bool(valido),
        total=len(ptts),
        prop_alta=proporcao_impacto_alto(ptts),
        mensagem=mensagem,
    )


def _entrada_canonica(tipo: DocumentType) -> Path:
    return BACKEND_DIR / "inputs" / tipo.value / "projeto.docx"


def gerar_buffer(pedido: GenerateRequest) -> BytesIO:
    """
    Aciona o builder do tipo pedido e devolve o DOCX em memória.

    Os geradores atuais leem o projeto .docx canônico em inputs/ e aplicam o
    nível informado. O JSON do pedido permanece o contrato do frontend para
    metadados já revisados; a montagem normativa continua nos builders.
    """
    entrada = _entrada_canonica(pedido.tipo_documento)
    if not entrada.is_file():
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {entrada}")

    assets = BACKEND_DIR / "assets"
    temporario = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    temporario.close()
    saida = temporario.name
    try:
        if pedido.tipo_documento == DocumentType.qualificacao:
            gerar_documento_qualificacao(
                str(entrada),
                saida,
                nivel=pedido.nivel.value,
                assets_dir=str(assets),
            )
        elif pedido.tipo_documento == DocumentType.dissertacao:
            gerar_documento_dissertacao(str(entrada), saida, assets_dir=str(assets))
        else:
            gerar_documento_tese(str(entrada), saida, assets_dir=str(assets))
        buffer = BytesIO(Path(saida).read_bytes())
    finally:
        if os.path.exists(saida):
            os.remove(saida)
    buffer.seek(0)
    return buffer
