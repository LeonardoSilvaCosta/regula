"""Padrões tipográficos e margens normativas do PPGSP/UFPA."""
import os
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

IDIOMA_PT_BR = "pt-BR"

# Modelo PPGSP/UFPA — brasão na capa e folhas pré-textuais
BRASAO_UFPA_LARGURA = Cm(2.11)
BRASAO_UFPA_ALTURA = Cm(2.52)


def _elemento_idioma(elemento_rpr, idioma=IDIOMA_PT_BR):
    lang = elemento_rpr.find(qn("w:lang"))
    if lang is None:
        lang = OxmlElement("w:lang")
        elemento_rpr.append(lang)
    lang.set(qn("w:val"), idioma)
    lang.set(qn("w:eastAsia"), idioma)
    lang.set(qn("w:bidi"), "ar-SA")


def _idioma_no_run(run, idioma=IDIOMA_PT_BR):
    _elemento_idioma(run._element.get_or_add_rPr(), idioma)


def aplicar_idioma_pt_br(doc):
    """Marca o documento e todos os trechos como português do Brasil (revisão do Word)."""
    styles = doc.styles.element
    doc_defaults = styles.find(qn("w:docDefaults"))
    if doc_defaults is None:
        doc_defaults = OxmlElement("w:docDefaults")
        styles.insert(0, doc_defaults)
    rpr_default = doc_defaults.find(qn("w:rPrDefault"))
    if rpr_default is None:
        rpr_default = OxmlElement("w:rPrDefault")
        doc_defaults.append(rpr_default)
    rpr = rpr_default.find(qn("w:rPr"))
    if rpr is None:
        rpr = OxmlElement("w:rPr")
        rpr_default.append(rpr)
    _elemento_idioma(rpr)

    settings = doc.settings.element
    theme_lang = settings.find(qn("w:themeFontLang"))
    if theme_lang is None:
        theme_lang = OxmlElement("w:themeFontLang")
        settings.append(theme_lang)
    theme_lang.set(qn("w:val"), IDIOMA_PT_BR)
    theme_lang.set(qn("w:eastAsia"), IDIOMA_PT_BR)

    style_normal = doc.styles["Normal"]
    rpr_normal = style_normal.element.find(qn("w:rPr"))
    if rpr_normal is None:
        rpr_normal = OxmlElement("w:rPr")
        style_normal.element.append(rpr_normal)
    _elemento_idioma(rpr_normal)

    for paragrafo in doc.paragraphs:
        for run in paragrafo.runs:
            _idioma_no_run(run)
    for tabela in doc.tables:
        for linha in tabela.rows:
            for celula in linha.cells:
                for paragrafo in celula.paragraphs:
                    for run in paragrafo.runs:
                        _idioma_no_run(run)
    for secao in doc.sections:
        for bloco in (secao.header, secao.footer):
            for paragrafo in bloco.paragraphs:
                for run in paragrafo.runs:
                    _idioma_no_run(run)


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
    aplicar_idioma_pt_br(doc)

def set_page_margins(section):
    """Margens ABNT/PPGSP: 3 cm Superior e Esquerda, 2 cm Inferior e Direita."""
    section.top_margin = Cm(3.0)
    section.left_margin = Cm(3.0)
    section.bottom_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)


def _limpar_paragrafo(paragrafo):
    for run in list(paragrafo.runs):
        run._element.getparent().remove(run._element)


def aplicar_rodape_local_ano(section, local="Belém-Pará", ano="2026"):
    """Local e ano no rodapé, três linhas acima da borda inferior."""
    section.footer_distance = Cm(2.1)
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    _limpar_paragrafo(p)
    r = p.add_run(f"{local}\n{ano}")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)


def limpar_rodape(section):
    """Esvazia o rodapé e desvincula da seção anterior (capa não leva local/ano aqui)."""
    footer = section.footer
    footer.is_linked_to_previous = False
    for paragrafo in footer.paragraphs:
        _limpar_paragrafo(paragrafo)
        paragrafo.paragraph_format.space_before = Pt(0)
        paragrafo.paragraph_format.space_after = Pt(0)
        paragrafo.paragraph_format.line_spacing = 1.0

def insert_brasao(doc, assets_dir="assets"):
    """Insere a imagem do Brasão da UFPA centralizada."""
    caminho = os.path.join(assets_dir, "brasao_ufpa.png")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(6)
    if os.path.exists(caminho):
        p.add_run().add_picture(
            caminho, width=BRASAO_UFPA_LARGURA, height=BRASAO_UFPA_ALTURA
        )
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