"""Conecta o upload de .docx ao parser de qualificação e ao validador de PTTs."""

from __future__ import annotations

import os
import tempfile
from typing import Any

from generators.qualificacao.lacunas import coletar_lacunas
from generators.qualificacao.parser import parse_projeto_docx

from app.schemas.document import (
    AcademicLevel,
    BancaMember,
    DocumentMetadata,
    DocumentType,
    LacunaItem,
    ParseResponse,
)
from app.schemas.ptt import PTTItem
from app.services.builder_service import validar_ptts
from app.services.upload_store import guardar


def _coorientador(metadata: dict[str, Any], banca: list[dict[str, Any]]) -> str:
    informado = str(metadata.get("coorientador") or "").strip()
    if informado:
        return informado
    for membro in banca:
        funcao = str(membro.get("funcao") or "").lower()
        if "coorient" in funcao:
            return str(membro.get("nome") or "").strip()
    return ""


def _siglas(metadata: dict[str, Any]) -> list[tuple[str, str]]:
    pares: list[tuple[str, str]] = []
    for item in metadata.get("siglas") or []:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            pares.append((str(item[0]), str(item[1])))
    return pares


def _banca(metadata: dict[str, Any]) -> list[BancaMember]:
    membros = []
    for membro in metadata.get("banca") or []:
        membros.append(
            BancaMember(
                nome=str(membro.get("nome") or ""),
                titulacao=membro.get("titulacao"),
                instituicao=str(membro.get("instituicao") or ""),
                funcao=str(membro.get("funcao") or "Avaliador"),
            )
        )
    return membros


def estruturar_parse(
    dados: dict[str, Any],
    nivel: AcademicLevel,
    documento_id: str = "",
) -> ParseResponse:
    metadata = dict(dados.get("metadata") or {})
    ptts_brutos = list((dados.get("projeto") or {}).get("ptts") or [])
    ptts = [PTTItem.model_validate(item) for item in ptts_brutos]
    siglas = _siglas(metadata)
    banca_bruta = list(metadata.get("banca") or [])
    conformidade = validar_ptts(ptts, nivel)
    lacunas_brutas = coletar_lacunas(dados, siglas, [], [])
    return ParseResponse(
        documento_id=documento_id,
        tipo_documento=DocumentType.qualificacao,
        nivel=nivel,
        metadata=DocumentMetadata(
            titulo=str(metadata.get("titulo") or ""),
            subtitulo=str(metadata.get("subtitulo") or ""),
            autor=str(metadata.get("autor") or ""),
            orientador=str(metadata.get("orientador") or ""),
            coorientador=_coorientador(metadata, banca_bruta),
            coordenador=str(metadata.get("coordenador") or ""),
            ano=str(metadata.get("ano") or ""),
            local=str(metadata.get("local") or ""),
            area_concentracao=str(metadata.get("area_concentracao") or ""),
            linha_pesquisa=str(metadata.get("linha_pesquisa") or ""),
        ),
        banca=_banca(metadata),
        siglas=siglas,
        ptts=ptts,
        lacunas=[LacunaItem.model_validate(item) for item in lacunas_brutas],
        conformidade_ptt=conformidade,
    )


def parse_upload(conteudo: bytes, nivel: AcademicLevel) -> ParseResponse:
    """Grava o .docx em arquivo temporário e devolve o JSON estruturado."""
    temporario = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
    try:
        temporario.write(conteudo)
        temporario.close()
        dados = parse_projeto_docx(temporario.name)
    finally:
        temporario.close()
        if os.path.exists(temporario.name):
            os.remove(temporario.name)
    return estruturar_parse(dados, nivel, documento_id=guardar(conteudo))
