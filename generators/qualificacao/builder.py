"""
Orquestrador do Relatório de Qualificação com arquitetura de 3 seções Word formais
conforme a Resolução nº 009/2025-PPGSP/UFPA.
"""

import docx
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT, WD_SECTION

from core.styles import apply_base_styles, aplicar_idioma_pt_br, aplicar_rodape_local_ano, limpar_rodape, set_page_margins
from core.xml_utils import configure_section_page_numbers, add_page_number_field, continuar_numeracao
from core.campos import habilitar_atualizacao_de_campos
from core.atualizar_campos import atualizar_campos_word

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
from .pre_textual.listas_simbolos import build_lista_simbolos
from .pre_textual.sumario import build_sumario
from .estrutura import numeracao_secoes
from .textual.apresentacao import build_apresentacao, build_quadro_estrutura
from .projeto import build_projeto_secoes
from .textual.resultados_preliminares import build_resultados_preliminares
from .pos_textual.pos_textual import build_pos_textual, itens_com_corpo


def _secao_sem_numero(doc, primeira=False):
    section = doc.sections[0] if primeira else doc.add_section(WD_SECTION.NEW_PAGE)
    set_page_margins(section)
    section.header.is_linked_to_previous = False
    section.footer.is_linked_to_previous = False
    return section


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
    limpar_rodape(section)
    configure_section_page_numbers(section, num_format=formato, start_at=inicio)
    header = section.header.paragraphs[0]
    header.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = header.add_run()
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    add_page_number_field(run)


def gerar_documento_qualificacao(caminho_entrada, caminho_saida, nivel="mestrado", assets_dir="assets"):
    dados = parse_projeto_docx(caminho_entrada)
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
    # Capa e folha de rosto: local e ano no extremo inferior (rodapé da seção)
    # Folha de aprovação segue sem esse rodapé e sem número visível
    # =========================================================================
    local = dados["metadata"].get("local", "Belém-Pará")
    ano = dados["metadata"].get("ano", "2026")

    sec_capa = _secao_sem_numero(doc, primeira=True)
    build_capa(doc, dados["metadata"], assets_dir=assets_dir)
    aplicar_rodape_local_ano(sec_capa, local, ano)

    sec_rosto = _secao_sem_numero(doc)
    build_folha_rosto(doc, dados["metadata"], assets_dir=assets_dir)
    aplicar_rodape_local_ano(sec_rosto, local, ano)

    sec_aprov = _secao_sem_numero(doc)
    limpar_rodape(sec_aprov)
    build_folha_aprovacao(doc, dados["metadata"], assets_dir=assets_dir)

    # =========================================================================
    # SEÇÃO 2: Listas existentes e sumário (romana, a partir de iv)
    # =========================================================================
    sec_2 = doc.add_section(WD_SECTION.NEW_PAGE)
    _paginar(sec_2, "roman", 4)

    listas_sumario = []
    iniciado = False

    def abrir_elemento():
        nonlocal iniciado
        if iniciado:
            doc.add_page_break()
        iniciado = True

    ilustracoes = list(quadros) + list(tabelas)
    if ilustracoes:
        abrir_elemento()
        listas_sumario.extend(build_lista_ilustracoes(doc, ilustracoes, quebrar=False))
    if normalizar_siglas(siglas):
        abrir_elemento()
        entrada = build_lista_siglas(doc, siglas, quebrar=False)
        if entrada:
            listas_sumario.append(entrada)
    if simbolos:
        abrir_elemento()
        entrada = build_lista_simbolos(doc, simbolos, quebrar=False)
        if entrada:
            listas_sumario.append(entrada)

    abrir_elemento()
    build_sumario(
        doc,
        dados,
        apendices=apendices,
        anexos=anexos,
        listas=listas_sumario,
        quebrar=False,
    )

    # =========================================================================
    # SEÇÃO 3: Parte textual, a partir da Apresentação (arábica, a partir de 1)
    # =========================================================================
    sec_3 = doc.add_section(WD_SECTION.NEW_PAGE)
    _paginar(sec_3, "decimal", 1)
    numeros = numeracao_secoes(dados["projeto"])

    build_apresentacao(doc, dados["apresentacao"], dados["metadata"])
    _secao_paisagem(doc)
    build_quadro_estrutura(
        doc,
        dados["apresentacao"],
        dados["metadata"],
        objetivo_geral=(dados.get("projeto") or {}).get("objetivo_geral", ""),
    )
    _secao_retrato_continua(doc)
    build_projeto_secoes(doc, dados["projeto"], nivel=nivel, numeros=numeros)
    build_resultados_preliminares(doc, dados["resultados"], numero=numeros["resultados"])
    build_pos_textual(doc, dados["referencias"], apendices=apendices, anexos=anexos)

    aplicar_idioma_pt_br(doc)
    habilitar_atualizacao_de_campos(doc)
    doc.save(caminho_saida)
    atualizar_campos_word(caminho_saida)
    print(f"[CONCLUÍDO]: Relatório de Qualificação gerado em {caminho_saida}")
    emitir_lacunas(
        caminho_saida,
        coletar_lacunas(dados, siglas, apendices_omitidos, anexos_omitidos),
    )