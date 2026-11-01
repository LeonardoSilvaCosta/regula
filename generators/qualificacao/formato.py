"""Títulos e parágrafos da Resolução nº 009/2025."""
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.campos import adicionar_bookmark, ancorar_paragrafo


def adicionar_titulo(doc, texto, bookmark=None, primario=True, marcar=True):
    """Título justificado, em negrito, com uma linha em branco antes do texto."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(18 if primario else 12)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(texto)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    if marcar:
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
