"""Validação da carteira de PTTs e geração do DOCX em buffer."""

from __future__ import annotations

import os
import tempfile
from io import BytesIO
from pathlib import Path

from core.ptt_schema import validar_carteira_produtos
from core.xml_utils import sanitizar_estrutura
from generators.dissertacao.builder import gerar_documento_dissertacao
from generators.protocolo_cep.builder import gerar_documento_protocolo_cep
from generators.projeto_completo_cep.builder import gerar_documento_projeto_completo_cep
from generators.qualificacao.builder import gerar_documento_qualificacao
from generators.tese.builder import gerar_documento_tese

from app.schemas.document import AcademicLevel, DocumentType, GenerateRequest
from app.schemas.ptt import PTTItem, PTTValidationResult
from app.services.upload_store import caminho as caminho_upload

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


def _revisao(pedido: GenerateRequest) -> dict:
    """Metadados, seções, banca, siglas e PTTs confirmados no Passo 3."""
    return sanitizar_estrutura(
        {
            "metadata": pedido.metadata.model_dump(),
            "sections": pedido.sections.model_dump(),
            "banca": [membro.model_dump() for membro in pedido.banca],
            "siglas": [list(par) for par in pedido.siglas],
            "ptts": [item.model_dump() for item in pedido.ptts],
            "artigos": [item.model_dump() for item in pedido.artigos],
            "cronograma": [item.model_dump() for item in pedido.cronograma],
            "protocolo_cep": pedido.protocolo_cep.model_dump(),
        }
    )


def gerar_buffer(pedido: GenerateRequest) -> BytesIO:
    """
    Aciona o builder do tipo pedido e devolve o DOCX em memória.

    Com documento_id, o corpo parte do .docx enviado. Sem ele, capa, seções,
    banca, siglas e fichas de PTT saem só dos dados revisados no Passo 3.
    """
    entrada = caminho_upload(pedido.documento_id) if pedido.documento_id.strip() else None
    caminho_entrada = str(entrada) if entrada is not None else None

    assets = BACKEND_DIR / "assets"
    revisao = _revisao(pedido)
    temporario = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    temporario.close()
    saida = temporario.name
    try:
        if pedido.tipo_documento == DocumentType.qualificacao:
            gerar_documento_qualificacao(
                caminho_entrada,
                saida,
                nivel=pedido.nivel.value,
                assets_dir=str(assets),
                revisao=revisao,
            )
        elif pedido.tipo_documento == DocumentType.protocolo_cep:
            gerar_documento_protocolo_cep(
                saida,
                protocolo=revisao["protocolo_cep"],
            )
        elif pedido.tipo_documento == DocumentType.projeto_completo_cep:
            gerar_documento_projeto_completo_cep(
                saida,
                revisao=revisao,
                nivel=pedido.nivel.value,
                assets_dir=str(assets),
            )
        elif pedido.tipo_documento == DocumentType.dissertacao:
            gerar_documento_dissertacao(
                caminho_entrada,
                saida,
                assets_dir=str(assets),
                metadata=revisao["metadata"],
                revisao=revisao,
            )
        else:
            gerar_documento_tese(
                caminho_entrada,
                saida,
                assets_dir=str(assets),
                metadata=revisao["metadata"],
                revisao=revisao,
            )
        buffer = BytesIO(Path(saida).read_bytes())
    finally:
        if os.path.exists(saida):
            os.remove(saida)
    buffer.seek(0)
    return buffer
