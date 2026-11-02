"""
Apresentação e Quadro 1 da Resolução nº 009/2025-PPGSP/UFPA.
"""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from core.xml_utils import set_cell_border
from core.campos import adicionar_bookmark
from ..formato import (
    adicionar_lacuna,
    adicionar_paragrafo,
    adicionar_titulo,
    escrever_fonte,
    escrever_legenda_quadro_1,
)
from ..legendas import BM_QUADRO_1, legenda_quadro_1


_COLUNAS = [
    "Título",
    "Objetivo Geral",
    "Objetivos Específicos",
    "Tipo de Produto",
    "Tipo de Estudo",
    "Fontes",
    "Status",
]
# Larguras do quadro modelo, em twips. Cabem na área útil da página paisagem.
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
    adicionar_titulo(doc, "APRESENTAÇÃO", bookmark="sec_apresentacao")

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


def build_quadro_estrutura(doc, dados_apresentacao, metadata, objetivo_geral=""):
    p_qtit = doc.add_paragraph()
    p_qtit.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_qtit.paragraph_format.space_before = Pt(18)
    p_qtit.paragraph_format.space_after = Pt(4)
    p_qtit.paragraph_format.line_spacing = 1.0
    escrever_legenda_quadro_1(p_qtit, legenda_quadro_1(metadata))
    adicionar_bookmark(p_qtit, BM_QUADRO_1)

    linhas = _preparar_linhas(
        (dados_apresentacao or {}).get("quadro_1") or [],
        metadata,
        objetivo_geral,
    )
    if not linhas:
        adicionar_lacuna(doc, "[Quadro 1 não informado no projeto.]")
        return

    _montar_quadro(doc, linhas)
    ano = (metadata or {}).get("ano", "2026")
    p_fonte = doc.add_paragraph()
    p_fonte.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_fonte.paragraph_format.space_before = Pt(2)
    p_fonte.paragraph_format.space_after = Pt(18)
    p_fonte.paragraph_format.line_spacing = 1.0
    escrever_fonte(p_fonte, f"Fonte: Construção do(a) Autor(a). {ano}.")


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
    p.alignment = alinhamento
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    if p.runs:
        p.runs[0].font.name = "Times New Roman"
        p.runs[0].font.size = Pt(10)
        p.runs[0].bold = negrito
    set_cell_border(celula, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})


def _grade_fixa(tabela):
    tbl = tabela._tbl
    tbl_pr = tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(_LARGURAS)))
    tbl_w.set(qn("w:type"), "dxa")
    grade = tbl.find(qn("w:tblGrid"))
    if grade is None:
        grade = OxmlElement("w:tblGrid")
        tbl_pr.addnext(grade)
    for filho in list(grade):
        grade.remove(filho)
    for largura in _LARGURAS:
        coluna = OxmlElement("w:gridCol")
        coluna.set(qn("w:w"), str(largura))
        grade.append(coluna)


def _montar_quadro(doc, linhas):
    tabela = doc.add_table(rows=1 + len(linhas), cols=len(_COLUNAS))
    tabela.alignment = WD_TABLE_ALIGNMENT.LEFT
    tabela.autofit = False
    _grade_fixa(tabela)

    for idx, nome in enumerate(_COLUNAS):
        celula = tabela.rows[0].cells[idx]
        celula.width = Twips(_LARGURAS[idx])
        _texto_celula(celula, nome, negrito=True, alinhamento=WD_ALIGN_PARAGRAPH.CENTER)

    for r_idx, linha in enumerate(linhas, start=1):
        for c_idx, valor in enumerate(linha):
            celula = tabela.rows[r_idx].cells[c_idx]
            celula.width = Twips(_LARGURAS[c_idx])
            _texto_celula(celula, valor, alinhamento=_ALINHAMENTO[c_idx])

    if len(linhas) > 1:
        _mesclar(tabela, 0, linhas[0][0])
        objetivo = next((linha[1] for linha in linhas if linha[1]), "")
        _mesclar(tabela, 1, objetivo)


def _mesclar(tabela, coluna, texto):
    topo = tabela.rows[1].cells[coluna]
    for linha in range(2, len(tabela.rows)):
        topo.merge(tabela.rows[linha].cells[coluna])
    topo.width = Twips(_LARGURAS[coluna])
    _texto_celula(topo, texto, alinhamento=_ALINHAMENTO[coluna])
