"""Padrões tipográficos e margens normativas do PPGSP/UFPA."""
import os
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

def apply_base_styles(doc):
    """Aplica o padrão gráfico básico: Times 12, entrelinhas 1.5, parágrafos 0 pt."""
    style_normal = doc.styles['Normal']
    font = style_normal.font
    font.name = 'Times New Roman'
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    style_normal.paragraph_format.line_spacing = 1.5
    style_normal.paragraph_format.space_before = Pt(0)
    style_normal.paragraph_format.space_after = Pt(0)

def set_page_margins(section):
    """Margens ABNT/PPGSP: 3 cm Superior e Esquerda, 2 cm Inferior e Direita."""
    section.top_margin = Cm(3.0)
    section.left_margin = Cm(3.0)
    section.bottom_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)

def insert_brasao(doc, assets_dir="assets"):
    """Insere a imagem do Brasão da UFPA centralizada."""
    caminho = os.path.join(assets_dir, "brasao_ufpa.png")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    if os.path.exists(caminho):
        p.add_run().add_picture(caminho, width=Cm(2.5))
    else:
        r = p.add_run("[BRASÃO DA UFPA]\n")
        r.font.size = Pt(10)
        r.italic = True

def insert_cabecalho_institucional(doc):
    """Cabeçalho formal de 5 linhas em maiúsculas negrito, Times 12."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(18)
    r = p.add_run(
        "UNIVERSIDADE FEDERAL DO PARÁ\n"
        "INSTITUTO DE CIÊNCIAS EXATAS E NATURAIS\n"
        "PROGRAMA DE PÓS-GRADUAÇÃO EM SEGURANÇA PÚBLICA\n"
        "MESTRADO OU DOUTORADO EM SEGURANÇA PÚBLICA\n"
    )
    r.bold = True
    r.font.size = Pt(12)