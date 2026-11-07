"""
Orquestrador do Relatório de Qualificação com arquitetura de 3 seções Word formais
conforme a Resolução nº 009/2025-PPGSP/UFPA.
"""

import copy
import os

import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT, WD_SECTION

from core.styles import (
    apply_base_styles,
    aplicar_idioma_pt_br,
    aplicar_cabecalho_institucional,
    aplicar_rodape_local_ano,
    limpar_cabecalho,
    limpar_rodape,
    set_page_margins,
)
from core.xml_utils import configure_section_page_numbers, add_page_number_field, continuar_numeracao
from core.atualizar_campos import atualizar_campos_word

from .formato import adicionar_paragrafo, adicionar_titulo
from .parser import parse_projeto_docx
from .legendas import (
    BM_QUADRO_1,
    BM_QUADRO_2,
    BM_TABELA_1,
    BM_TABELA_2,
    LEGENDA_TABELA_1,
    LEGENDA_TABELA_2,
    legenda_quadro_1,
    legenda_quadro_2,
)
from .lacunas import coletar_lacunas, emitir_lacunas
from .simbolos_texto import simbolos_do_documento
from .pre_textual.capa import build_capa
from .pre_textual.folha_rosto import build_folha_rosto
from .pre_textual.folha_aprovacao import build_folha_aprovacao
from .pre_textual.listas_ilustracoes import build_lista_ilustracoes
from .pre_textual.listas_siglas import build_lista_siglas, normalizar_siglas
from .pre_textual.simbolos import build_lista_simbolos, normalizar_simbolos
from .pre_textual.sumario import build_sumario, preencher_sumario
from .estrutura import numeracao_secoes
from .textual.apresentacao import build_apresentacao, build_quadro_estrutura
from .projeto import build_projeto_secoes
from .textual.resultados_preliminares import build_resultados_preliminares
from .pos_textual.pos_textual import build_pos_textual, itens_com_corpo


def habilitar_atualizacao_campos(doc):
    """Pede ao Word que recalcule sumário e paginação ao abrir o arquivo."""
    from core.campos import habilitar_atualizacao_de_campos

    habilitar_atualizacao_de_campos(doc)


def _secao_sem_numero(doc, primeira=False):
    section = doc.sections[0] if primeira else doc.add_section(WD_SECTION.NEW_PAGE)
    set_page_margins(section)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    limpar_cabecalho(section)
    return section


def _fontes_padrao(projeto):
    fontes = projeto.get("metodologia_fontes") or []
    if isinstance(fontes, list):
        for item in fontes:
            texto = str(item or "").strip()
            if texto:
                return texto.split("\n")[0].strip()
    elif str(fontes or "").strip():
        return str(fontes).strip().split("\n")[0].strip()
    locus = str(projeto.get("metodologia_locus") or "").strip()
    return locus or "SIAC"


def _secao_paisagem(doc):
    """Página isolada em paisagem, herdando cabeçalho e numeração da seção anterior."""
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    set_page_margins(section)
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Cm(29.7)
    section.page_height = Cm(21.0)
    section.header.is_linked_to_previous = True
    section.footer.is_linked_to_previous = True
    continuar_numeracao(section)
    return section


def _secao_retrato_continua(doc):
    """Volta ao retrato sem reiniciar a numeração."""
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    set_page_margins(section)
    section.header.is_linked_to_previous = True
    section.footer.is_linked_to_previous = True
    continuar_numeracao(section)
    return section


def _paginar(section, formato, inicio):
    set_page_margins(section)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    limpar_cabecalho(section)
    limpar_rodape(section)
    configure_section_page_numbers(section, num_format=formato, start_at=inicio)
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run()
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    add_page_number_field(run)


_CHAVES_PROJETO = (
    "introducao",
    "justificativa",
    "problema",
    "revisao",
    "referencial_teorico",
    "objetivo_geral",
    "objetivos_especificos",
    "hipotese",
    "metodologia_natureza",
    "metodologia_locus",
    "metodologia_participantes",
    "metodologia_fontes",
    "metodologia_coleta",
    "metodologia_etica",
    "metodologia_analise",
    "tabela_1",
    "tabela_2",
)

_DADOS_VAZIOS = {
    "metadata": {},
    "apresentacao": {"texto_percurso": [], "quadro_1": []},
    "projeto": {
        "introducao": [],
        "justificativa": [],
        "problema": [],
        "revisao": [],
        "incluir_referencial_teorico": False,
        "referencial_teorico": [],
        "objetivo_geral": "",
        "objetivos_especificos": [],
        "incluir_hipoteses": False,
        "hipotese": [],
        "metodologia_natureza": [],
        "metodologia_locus": "",
        "metodologia_participantes": "",
        "metodologia_fontes": [],
        "metodologia_coleta": [],
        "metodologia_etica": "",
        "metodologia_analise": "",
        "tabela_1": {"linhas": []},
        "tabela_2": {"linhas": []},
        "ptts": [],
        "cronograma": [],
        "ano": "2026",
    },
    "resultados": {"artigos": []},
    "referencias": [],
    "pos_textual": {"apendices": [], "anexos": []},
    "secoes_nao_mapeadas": [],
}


def _valor_preenchido(valor):
    return valor is not None and valor != "" and valor != []


def _mesclar_revisao(dados, revisao):
    """Sobrepõe no documento os metadados e as seções confirmados no Passo 3."""
    if not revisao:
        return
    meta = dados.setdefault("metadata", {})
    for chave, valor in (revisao.get("metadata") or {}).items():
        if valor is None:
            continue
        meta[chave] = valor
    if "banca" in revisao:
        meta["banca"] = list(revisao.get("banca") or [])
    if "siglas" in revisao:
        meta["siglas"] = [list(par) for par in (revisao.get("siglas") or [])]
    secoes = revisao.get("sections") or {}
    if secoes:
        projeto = dados.setdefault("projeto", {})
        for chave in _CHAVES_PROJETO:
            if chave not in secoes or not _valor_preenchido(secoes[chave]):
                continue
            projeto[chave] = secoes[chave]
        if "incluir_hipoteses" in secoes:
            projeto["incluir_hipoteses"] = bool(secoes.get("incluir_hipoteses"))
        if "incluir_referencial_teorico" in secoes:
            projeto["incluir_referencial_teorico"] = bool(secoes.get("incluir_referencial_teorico"))
        if "referencial_teorico" in secoes:
            projeto["referencial_teorico"] = list(secoes.get("referencial_teorico") or [])
        if _valor_preenchido(secoes.get("apresentacao")):
            bloco = dados.setdefault("apresentacao", {})
            if not isinstance(bloco, dict):
                bloco = {}
                dados["apresentacao"] = bloco
            bloco["texto_percurso"] = list(secoes["apresentacao"])
        if _valor_preenchido(secoes.get("referencias")):
            dados["referencias"] = list(secoes["referencias"])
    if revisao.get("cronograma"):
        projeto = dados.setdefault("projeto", {})
        projeto["cronograma"] = list(revisao.get("cronograma") or [])
    if "ptts" in revisao:
        projeto = dados.setdefault("projeto", {})
        atuais = list(projeto.get("ptts") or [])
        fundidos = []
        for indice, item in enumerate(revisao.get("ptts") or []):
            base = dict(atuais[indice]) if indice < len(atuais) else {}
            for chave, valor in item.items():
                if valor is None or valor == "":
                    continue
                base[chave] = valor
            if item.get("titulo"):
                base["titulo"] = item["titulo"]
            fundidos.append(base)
        projeto["ptts"] = fundidos
    if "artigos" not in revisao:
        return
    from .estrutura import artigos_de

    resultados = dados.setdefault("resultados", {})
    atuais = artigos_de(resultados)
    fundidos_artigos = []
    for indice, item in enumerate(revisao.get("artigos") or []):
        base = dict(atuais[indice]) if indice < len(atuais) and isinstance(atuais[indice], dict) else {}
        for chave, valor in (item or {}).items():
            if valor is None or valor == "":
                continue
            base[chave] = valor
        fundidos_artigos.append(base)
    if fundidos_artigos:
        resultados["artigos"] = fundidos_artigos


def gerar_documento_qualificacao(
    caminho_entrada,
    caminho_saida,
    nivel="mestrado",
    assets_dir="assets",
    revisao=None,
):
    if not caminho_entrada or not os.path.exists(caminho_entrada):
        dados = copy.deepcopy(_DADOS_VAZIOS)
    else:
        dados = parse_projeto_docx(caminho_entrada)
    _mesclar_revisao(dados, revisao)
    nivel_norm = nivel.lower()
    dados["metadata"]["nivel"] = nivel_norm
    parte_quadro = "continua" if nivel_norm in ("doutorado", "tese") else None
    quadros = [
        (legenda_quadro_1(dados["metadata"]), BM_QUADRO_1),
        (legenda_quadro_2(nivel_norm, parte_quadro), BM_QUADRO_2),
    ]
    projeto = dados["projeto"]
    tabelas = []
    if (projeto.get("tabela_1") or {}).get("linhas"):
        tabelas.append((LEGENDA_TABELA_1, BM_TABELA_1))
    if (projeto.get("tabela_2") or {}).get("linhas"):
        tabelas.append((LEGENDA_TABELA_2, BM_TABELA_2))
    siglas = dados["metadata"].get("siglas") or dados.get("siglas") or []
    simbolos = simbolos_do_documento(dados)
    bruto_pos = dados.get("pos_textual") or {}
    apendices, apendices_omitidos = itens_com_corpo(bruto_pos.get("apendices"))
    anexos, anexos_omitidos = itens_com_corpo(bruto_pos.get("anexos"))

    doc = docx.Document()
    apply_base_styles(doc)

    # =========================================================================
    # Capa e folha de rosto: local e ano na base da página.
    # Folha de aprovação segue sem esse rodapé e sem número visível.
    # =========================================================================
    meta = dados["metadata"]
    local = (meta.get("local") or "Belém-Pará").strip()
    ano = (meta.get("ano") or "2026").strip()

    sec_capa = _secao_sem_numero(doc, primeira=True)
    aplicar_cabecalho_institucional(sec_capa, meta, assets_dir=assets_dir, space_after=24)
    build_capa(doc, meta, assets_dir=assets_dir)
    aplicar_rodape_local_ano(sec_capa, local, ano)

    sec_rosto = _secao_sem_numero(doc)
    aplicar_cabecalho_institucional(sec_rosto, meta, assets_dir=assets_dir, space_after=18)
    build_folha_rosto(doc, meta, assets_dir=assets_dir)
    aplicar_rodape_local_ano(sec_rosto, local, ano)

    sec_aprov = _secao_sem_numero(doc)
    aplicar_cabecalho_institucional(
        sec_aprov,
        meta,
        assets_dir=assets_dir,
        space_after=6,
        somente_primeira_pagina=True,
    )
    limpar_rodape(sec_aprov)
    build_folha_aprovacao(doc, dados["metadata"], assets_dir=assets_dir)

    # =========================================================================
    # SEÇÃO 2: Listas existentes e sumário (romana, a partir de iv)
    # =========================================================================
    sec_2 = doc.add_section(WD_SECTION.NEW_PAGE)
    _paginar(sec_2, "roman", 4)

    iniciado = False

    def abrir_elemento():
        nonlocal iniciado
        if iniciado:
            doc.add_page_break()
        iniciado = True

    ilustracoes = list(quadros) + list(tabelas)
    if ilustracoes:
        abrir_elemento()
        build_lista_ilustracoes(doc, ilustracoes)
        # A lista já encerra com uma quebra; o próximo elemento não deve inserir outra.
        iniciado = False
    if normalizar_siglas(siglas):
        abrir_elemento()
        build_lista_siglas(doc, siglas, quebrar=False)
        # A lista já encerra com uma quebra; o próximo elemento não deve inserir outra.
        iniciado = False
    if normalizar_simbolos(simbolos):
        abrir_elemento()
        build_lista_simbolos(doc, simbolos, quebrar=False)
        # A lista já encerra com uma quebra; o próximo elemento não deve inserir outra.
        iniciado = False

    abrir_elemento()
    build_sumario(
        doc,
        dados,
        apendices=apendices,
        anexos=anexos,
        quebrar=False,
    )

    # =========================================================================
    # SEÇÃO 3: Parte textual, a partir da Apresentação (arábica, a partir de 1).
    # O sumário já fecha com quebra de página; a seção contínua evita página em branco.
    # =========================================================================
    sec_3 = doc.add_section(WD_SECTION.CONTINUOUS)
    _paginar(sec_3, "decimal", 1)
    numeros = numeracao_secoes(dados["projeto"])

    build_apresentacao(doc, dados["apresentacao"], dados["metadata"])
    _secao_paisagem(doc)
    projeto_quadro = dados.get("projeto") or {}
    build_quadro_estrutura(
        doc,
        dados["apresentacao"],
        dados["metadata"],
        objetivo_geral=projeto_quadro.get("objetivo_geral", ""),
        objetivos_especificos=projeto_quadro.get("objetivos_especificos") or [],
        ptts=projeto_quadro.get("ptts") or [],
        artigos=(dados.get("resultados") or {}).get("artigos") or [],
        fontes_padrao=_fontes_padrao(projeto_quadro),
    )
    _secao_retrato_continua(doc)
    meta = dados.get("metadata") or {}
    projeto = dados["projeto"]
    for origem in ("autor", "area_concentracao", "linha_pesquisa", "titulo", "orientador", "coorientador"):
        if not str(projeto.get(origem) or "").strip():
            projeto[origem] = meta.get(origem) or ""
    if str(meta.get("ano") or "").strip():
        projeto["ano"] = meta["ano"]
    build_projeto_secoes(doc, projeto, nivel=nivel, numeros=numeros)
    build_resultados_preliminares(
        doc,
        dados["resultados"],
        numero=numeros["resultados"],
        metadata=meta,
    )
    for secao in dados.get("secoes_nao_mapeadas") or []:
        adicionar_titulo(doc, secao.get("titulo") or "Seção", primario=True, marcar=False)
        for paragrafo in secao.get("paragrafos") or []:
            adicionar_paragrafo(doc, paragrafo)
    build_pos_textual(doc, dados["referencias"], apendices=apendices, anexos=anexos)

    aplicar_idioma_pt_br(doc)
    preencher_sumario(doc)
    habilitar_atualizacao_campos(doc)
    doc.save(caminho_saida)
    atualizar_campos_word(caminho_saida)
    print(f"[CONCLUÍDO]: Relatório de Qualificação gerado em {caminho_saida}")
    emitir_lacunas(
        caminho_saida,
        coletar_lacunas(dados, siglas, apendices_omitidos, anexos_omitidos),
    )