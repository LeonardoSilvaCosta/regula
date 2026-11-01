"""Títulos e parágrafos da Resolução nº 009/2025."""
from docx.shared import Cm, Pt, RGBColor, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.campos import adicionar_bookmark, ancorar_paragrafo, aplicar_tabulacao_coluna


def adicionar_titulo(doc, texto, bookmark=None, primario=True, marcar=True):
    """Título justificado, sem negrito, com uma linha em branco antes do texto."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(18 if primario else 12)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(texto)
    r.bold = False
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    if marcar:
        ancorar_paragrafo(p, texto, bookmark=bookmark)
    return p


def adicionar_titulo_produto(doc, texto, secao, bookmark=None):
    """Até 'PRODUTO N.' regular; depois do ponto, tipo e título em negrito."""
    chave = "PRODUTO "
    pos = texto.find(chave)
    if pos >= 0:
        depois = texto[pos + len(chave) :]
        ponto = depois.find(".")
        if ponto >= 0:
            corte = pos + len(chave) + ponto + 1
            inicio, resto = texto[:corte], texto[corte:]
        else:
            inicio, resto = texto, ""
    else:
        inicio, resto = texto, ""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.5
    r_rotulo = p.add_run(inicio)
    r_rotulo.bold = False
    r_rotulo.font.name = "Times New Roman"
    r_rotulo.font.size = Pt(12)
    if resto:
        r_tit = p.add_run(resto)
        r_tit.bold = True
        r_tit.font.name = "Times New Roman"
        r_tit.font.size = Pt(12)
    if bookmark:
        ancorar_paragrafo(p, texto, bookmark=bookmark)
    return p


def adicionar_titulo_lista(doc, texto, bookmark):
    """Título de lista pré-textual: centralizado, Times 12, espaço simples."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    if bookmark:
        adicionar_bookmark(p, bookmark)
    return p


def adicionar_linha_par_alinhado(doc, rotulo, descricao, pos_twips):
    """Sigla/símbolo e forma por extenso em colunas, sem negrito e sem travessão."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.left_indent = Twips(pos_twips)
    p.paragraph_format.first_line_indent = Twips(-pos_twips)
    aplicar_tabulacao_coluna(p, pos_twips)

    r_rotulo = p.add_run(rotulo)
    r_rotulo.bold = False
    r_rotulo.font.name = "Times New Roman"
    r_rotulo.font.size = Pt(12)
    if descricao:
        r_desc = p.add_run("\t" + descricao)
        r_desc.bold = False
        r_desc.font.name = "Times New Roman"
        r_desc.font.size = Pt(12)
    return p


def adicionar_subtitulo_lista(doc, texto):
    """Sublista da lista de ilustrações: à esquerda, Times 12 negrito."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def adicionar_paragrafo(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(texto)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def adicionar_lacuna(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(texto)
    r.italic = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(115, 115, 115)
    return p
