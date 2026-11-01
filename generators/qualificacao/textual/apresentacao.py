"""
Apresentação e Quadro 1 da Resolução nº 009/2025-PPGSP/UFPA.
"""

from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from core.xml_utils import set_cell_border
from core.campos import adicionar_bookmark
from ..formato import adicionar_lacuna, adicionar_paragrafo, adicionar_titulo
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
_LARGURAS = [2.2, 2.4, 3.4, 2.8, 2.0, 1.6, 1.6]


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

    p_qtit = doc.add_paragraph()
    p_qtit.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_qtit.paragraph_format.space_before = Pt(18)
    p_qtit.paragraph_format.space_after = Pt(4)
    p_qtit.paragraph_format.line_spacing = 1.0
    r_qtit = p_qtit.add_run(legenda_quadro_1(metadata))
    r_qtit.bold = True
    r_qtit.font.name = "Times New Roman"
    r_qtit.font.size = Pt(12)
    adicionar_bookmark(p_qtit, BM_QUADRO_1)

    linhas = _preparar_linhas((dados_apresentacao or {}).get("quadro_1") or [], metadata)
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
    r_fonte = p_fonte.add_run(f"Fonte: Construção do autor ({ano}).")
    r_fonte.font.name = "Times New Roman"
    r_fonte.font.size = Pt(10)


def _preparar_linhas(linhas, metadata):
    titulo_pesquisa = ((metadata or {}).get("titulo_curto") or (metadata or {}).get("titulo") or "").strip()
    prontas = []
    for linha in linhas:
        if not isinstance(linha, (list, tuple)):
            continue
        cols = [str(c).strip() if c is not None else "" for c in linha]
        while len(cols) < 7:
            cols.append("")
        cols = cols[:7]
        titulo_linha = cols[0]
        if titulo_pesquisa and titulo_linha and titulo_linha != titulo_pesquisa and titulo_linha not in cols[3]:
            cols[3] = f"{titulo_linha}: {cols[3]}".strip(": ").strip() if cols[3] else titulo_linha
        cols[0] = titulo_pesquisa or titulo_linha
        if any(cols):
            prontas.append(cols)
    return prontas


def _texto_celula(celula, texto, negrito=False, centro=False):
    celula.text = texto
    p = celula.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centro else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    if p.runs:
        p.runs[0].font.name = "Times New Roman"
        p.runs[0].font.size = Pt(10)
        p.runs[0].bold = negrito
    set_cell_border(celula, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})


def _montar_quadro(doc, linhas):
    tabela = doc.add_table(rows=1 + len(linhas), cols=len(_COLUNAS))
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER

    for idx, nome in enumerate(_COLUNAS):
        celula = tabela.rows[0].cells[idx]
        celula.width = Cm(_LARGURAS[idx])
        _texto_celula(celula, nome, negrito=True, centro=True)

    for r_idx, linha in enumerate(linhas, start=1):
        for c_idx, valor in enumerate(linha):
            celula = tabela.rows[r_idx].cells[c_idx]
            celula.width = Cm(_LARGURAS[c_idx])
            centro = c_idx not in (2, 3)
            _texto_celula(celula, valor, centro=centro)

    if len(linhas) > 1:
        _mesclar(tabela, 0, linhas[0][0])
        objetivos = []
        for linha in linhas:
            if linha[1] and linha[1] not in objetivos:
                objetivos.append(linha[1])
        _mesclar(tabela, 1, "\n".join(objetivos))


def _mesclar(tabela, coluna, texto):
    topo = tabela.rows[1].cells[coluna]
    for linha in range(2, len(tabela.rows)):
        topo.merge(tabela.rows[linha].cells[coluna])
    topo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    _texto_celula(topo, texto, centro=True)
