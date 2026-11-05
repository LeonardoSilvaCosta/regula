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
    DocumentSections,
    DocumentType,
    LacunaItem,
    ParseResponse,
)
from app.schemas.ptt import ArtigoQuadro, PTTItem
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


def _linhas(valor: Any) -> list[str]:
    if valor is None:
        return []
    if isinstance(valor, str):
        texto = valor.strip()
        return [texto] if texto else []
    if isinstance(valor, dict):
        if "texto_percurso" in valor:
            return _linhas(valor.get("texto_percurso"))
        return []
    if isinstance(valor, list):
        linhas: list[str] = []
        for item in valor:
            linhas.extend(_linhas(item))
        return linhas
    texto = str(valor).strip()
    return [texto] if texto else []


def _texto(valor: Any) -> str:
    if isinstance(valor, str):
        return valor.strip()
    return "\n\n".join(_linhas(valor))


def _sections(dados: dict[str, Any]) -> DocumentSections:
    projeto = dict(dados.get("projeto") or {})
    return DocumentSections(
        apresentacao=_linhas(dados.get("apresentacao")),
        introducao=_linhas(projeto.get("introducao")),
        justificativa=_linhas(projeto.get("justificativa")),
        problema=_linhas(projeto.get("problema")),
        revisao=_linhas(projeto.get("revisao")),
        objetivo_geral=_texto(projeto.get("objetivo_geral")),
        objetivos_especificos=_linhas(projeto.get("objetivos_especificos")),
        hipotese=_linhas(projeto.get("hipotese")),
        metodologia_natureza=_linhas(projeto.get("metodologia_natureza")),
        metodologia_locus=_texto(projeto.get("metodologia_locus")),
        metodologia_participantes=_linhas(projeto.get("metodologia_participantes")),
        metodologia_fontes=_linhas(projeto.get("metodologia_fontes")),
        metodologia_coleta=_linhas(projeto.get("metodologia_coleta")),
        metodologia_etica=_linhas(projeto.get("metodologia_etica")),
        metodologia_analise=_linhas(projeto.get("metodologia_analise")),
        referencias=_linhas(dados.get("referencias")),
    )


def _artigos(dados: dict[str, Any]) -> list[ArtigoQuadro]:
    from generators.qualificacao.estrutura import artigos_de

    itens: list[ArtigoQuadro] = []
    for artigo in artigos_de(dados.get("resultados") or {}):
        itens.append(
            ArtigoQuadro(
                titulo=str(artigo.get("titulo") or ""),
                objetivo_especifico=str(
                    artigo.get("objetivo_especifico") or artigo.get("objetivo") or ""
                ),
                tipo_estudo=str(artigo.get("tipo_estudo") or "")
                or "Qualitativo/Quantitativo Exploratório Descritivo",
                fontes=str(artigo.get("fontes") or ""),
                status=str(artigo.get("status") or "") or "Em produção",
                subtipo=str(artigo.get("subtipo") or "Artigo"),
            )
        )
    return itens


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


def _metadata(metadata: dict[str, Any], banca_bruta: list[dict[str, Any]]) -> DocumentMetadata:
    """Campos vazios no Word preservam os defaults canônicos do schema."""
    informado = {
        "titulo": str(metadata.get("titulo") or ""),
        "subtitulo": str(metadata.get("subtitulo") or ""),
        "autor": str(metadata.get("autor") or ""),
        "orientador": str(metadata.get("orientador") or ""),
        "coorientador": _coorientador(metadata, banca_bruta),
        "coordenador": str(metadata.get("coordenador") or ""),
        "ano": str(metadata.get("ano") or ""),
        "local": str(metadata.get("local") or ""),
        "area_concentracao": str(metadata.get("area_concentracao") or ""),
        "linha_pesquisa": str(metadata.get("linha_pesquisa") or ""),
        "data_aprovacao": str(metadata.get("data_aprovacao") or ""),
    }
    return DocumentMetadata(**{chave: valor for chave, valor in informado.items() if valor})


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
        metadata=_metadata(metadata, banca_bruta),
        sections=_sections(dados),
        banca=_banca(metadata),
        siglas=siglas,
        ptts=ptts,
        artigos=_artigos(dados),
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
