"""
Apresentação e Quadro 1 da Resolução nº 009/2025-PPGSP/UFPA.
"""

import re

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from core.xml_utils import aplicar_autoajuste_janela, set_cell_border
from core.campos import adicionar_bookmark
from ..formato import (
    adicionar_lacuna,
    adicionar_paragrafo,
    adicionar_titulo,
    escrever_fonte,
    escrever_legenda_quadro_1,
)
from ..legendas import BM_QUADRO_1, legenda_quadro_1
from ..pre_textual.sumario import registrar_entrada


_COLUNAS = [
    "Título",
    "Objetivo Geral",
    "Objetivos Específicos",
    "Tipo de Produto",
    "Tipo de Estudo",
    "Fontes",
    "Status",
]
# Proporções das colunas do Quadro 1 (pesos relativos; a tabela usa autoajuste à janela).
_LARGURAS = [1731, 2276, 3502, 3121, 1416, 857, 1092]
_ALINHAMENTO = [
    WD_ALIGN_PARAGRAPH.LEFT,
    WD_ALIGN_PARAGRAPH.LEFT,
    WD_ALIGN_PARAGRAPH.LEFT,
    WD_ALIGN_PARAGRAPH.LEFT,
    WD_ALIGN_PARAGRAPH.JUSTIFY,
    WD_ALIGN_PARAGRAPH.CENTER,
    WD_ALIGN_PARAGRAPH.CENTER,
]


def build_apresentacao(doc, dados_apresentacao, metadata):
    titulo = adicionar_titulo(doc, "APRESENTAÇÃO", bookmark="sec_apresentacao")
    registrar_entrada(doc, "APRESENTAÇÃO", 1, "_TOC_APRESENTACAO", titulo)

    texto_percurso = (dados_apresentacao or {}).get("texto_percurso", [])
    if texto_percurso:
        for par in texto_percurso:
            adicionar_paragrafo(doc, par)
    else:
        adicionar_lacuna(
            doc,
            "[ORIENTAÇÃO DE PREENCHIMENTO: A Apresentação é obrigatória segundo o Art. 1º, II, item 1 da Resolução nº 009/2025. "
            "Elabore um texto em perspectiva pessoal abordando o percurso profissional vinculado ao objeto e o percurso acadêmico no curso.]",
        )


_TIPO_ESTUDO = "Qualitativo/Quantitativo Exploratório Descritivo"
_STATUS = "Em produção"
_ROMANOS = (
    "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
    "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx",
)


def _romano(indice):
    if 1 <= indice <= len(_ROMANOS):
        return _ROMANOS[indice - 1]
    return str(indice)


def _texto_item(item, chave):
    if isinstance(item, dict):
        return str(item.get(chave) or "").strip()
    return str(getattr(item, chave, "") or "").strip()


def _aplicar_lista_objetivos(linhas, objetivos):
    """A coluna de objetivos específicos repete a lista numerada da seção 2.2."""
    itens = []
    for item in objetivos or []:
        texto = re.sub(
            r"^\s*\(?\s*(?:i{1,3}|iv|vi{0,3}|ix|x|\d+)\s*[\).\]]\s*",
            "",
            str(item or "").strip(),
            flags=re.IGNORECASE,
        ).strip()
        if texto:
            itens.append(texto)
    for indice, linha in enumerate(linhas):
        if indice >= len(itens):
            break
        linha[2] = f"({_romano(indice + 1)}) {itens[indice]}"
    return linhas


def _linhas_produtos(metadata, objetivo_geral, artigos, ptts, fontes_padrao):
    titulo = str((metadata or {}).get("titulo") or (metadata or {}).get("titulo_curto") or "").strip()
    objetivo = str(objetivo_geral or "").strip()
    fontes_base = str(fontes_padrao or "").strip() or "SIAC"
    linhas = []
    ordem = 1
    for artigo in artigos or []:
        titulo_item = _texto_item(artigo, "titulo")
        linhas.append([
            titulo,
            objetivo,
            f"({_romano(ordem)}) {_texto_item(artigo, 'objetivo_especifico')}",
            f"Artigo {ordem}: {titulo_item}",
            _texto_item(artigo, "tipo_estudo") or _TIPO_ESTUDO,
            _texto_item(artigo, "fontes") or fontes_base,
            _texto_item(artigo, "status") or _STATUS,
        ])
        ordem += 1
    numero_ptt = 1
    for item in ptts or []:
        titulo_item = _texto_item(item, "titulo") or _texto_item(item, "nome")
        subtipo = _texto_item(item, "subtipo") or _texto_item(item, "tipo") or "PTT"
        num = _texto_item(item, "num") or str(numero_ptt)
        linhas.append([
            titulo,
            objetivo,
            f"({_romano(ordem)}) {_texto_item(item, 'objetivo_especifico')}",
            f"{subtipo} {num} – {titulo_item}",
            _texto_item(item, "tipo_estudo") or _TIPO_ESTUDO,
            _texto_item(item, "fontes") or fontes_base,
            _texto_item(item, "status") or _STATUS,
        ])
        ordem += 1
        numero_ptt += 1
    return linhas


def build_quadro_estrutura(
    doc,
    dados_apresentacao,
    metadata,
    objetivo_geral="",
    objetivos_especificos=None,
    ptts=None,
    artigos=None,
    fontes_padrao="",
):
    p_qtit = doc.add_paragraph()
    p_qtit.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_qtit.paragraph_format.space_before = Pt(18)
    p_qtit.paragraph_format.space_after = Pt(4)
    p_qtit.paragraph_format.line_spacing = 1.0
    escrever_legenda_quadro_1(p_qtit, legenda_quadro_1(metadata))
    adicionar_bookmark(p_qtit, BM_QUADRO_1)

    linhas = _linhas_produtos(metadata, objetivo_geral, artigos, ptts, fontes_padrao)
    if not linhas:
        linhas = _preparar_linhas(
            (dados_apresentacao or {}).get("quadro_1") or [],
            metadata,
            objetivo_geral,
        )
    if not linhas:
        adicionar_lacuna(doc, "[Quadro 1 não informado no projeto.]")
        return
    _aplicar_lista_objetivos(linhas, objetivos_especificos)

    _montar_quadro(doc, linhas)
    mes_ano = str((metadata or {}).get("mes_ano") or (metadata or {}).get("ano") or "2026").strip()
    p_fonte = doc.add_paragraph()
    p_fonte.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_fonte.paragraph_format.space_before = Pt(2)
    p_fonte.paragraph_format.space_after = Pt(18)
    p_fonte.paragraph_format.line_spacing = 1.0
    escrever_fonte(p_fonte, f"Fonte: Construção do(a) Autor(a). {mes_ano}.")


def _preparar_linhas(linhas, metadata, objetivo_geral=""):
    titulo_dissertacao = (
        ((metadata or {}).get("titulo") or "").strip()
        or ((metadata or {}).get("titulo_curto") or "").strip()
    )
    objetivo = str(objetivo_geral or "").strip()
    prontas = []
    for linha in linhas:
        if not isinstance(linha, (list, tuple)):
            continue
        cols = [str(c).strip() if c is not None else "" for c in linha]
        while len(cols) < 7:
            cols.append("")
        cols = cols[:7]
        if titulo_dissertacao:
            cols[0] = titulo_dissertacao
        if objetivo:
            cols[1] = objetivo
        if any(cols):
            prontas.append(cols)
    return prontas


def _texto_celula(celula, texto, negrito=False, alinhamento=WD_ALIGN_PARAGRAPH.LEFT):
    celula.text = texto
    celula.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = celula.paragraphs[0]
    p.style = "Conteúdo de Quadro"
    p.alignment = alinhamento
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    if p.runs:
        p.runs[0].font.name = "Times New Roman"
        p.runs[0].font.size = Pt(10)
        p.runs[0].bold = negrito
    set_cell_border(celula, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})


def _montar_quadro(doc, linhas):
    tabela = doc.add_table(rows=1 + len(linhas), cols=len(_COLUNAS))
    tabela.alignment = WD_TABLE_ALIGNMENT.LEFT
    aplicar_autoajuste_janela(tabela, _LARGURAS)

    for idx, nome in enumerate(_COLUNAS):
        celula = tabela.rows[0].cells[idx]
        _texto_celula(celula, nome, negrito=True, alinhamento=WD_ALIGN_PARAGRAPH.CENTER)

    for r_idx, linha in enumerate(linhas, start=1):
        for c_idx, valor in enumerate(linha):
            celula = tabela.rows[r_idx].cells[c_idx]
            _texto_celula(celula, valor, alinhamento=_ALINHAMENTO[c_idx])

    if len(linhas) > 1:
        _mesclar(tabela, 0, linhas[0][0])
        objetivo = next((linha[1] for linha in linhas if linha[1]), "")
        _mesclar(tabela, 1, objetivo)


def _mesclar(tabela, coluna, texto):
    topo = tabela.rows[1].cells[coluna]
    for linha in range(2, len(tabela.rows)):
        topo.merge(tabela.rows[linha].cells[coluna])
    _texto_celula(topo, texto, alinhamento=_ALINHAMENTO[coluna])
