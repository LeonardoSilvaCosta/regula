"""
Sumário do Relatório de Qualificação.
Os números de página são campos PAGEREF, atualizados pelo Word ao abrir o arquivo.
"""

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.campos import adicionar_linha_indice
from ..estrutura import itens_do_sumario


def build_sumario(doc, dados, apendices=None, anexos=None, listas=None, quebrar=True):
    if quebrar:
        doc.add_page_break()

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(0)
    p_tit.paragraph_format.space_after = Pt(18)
    p_tit.paragraph_format.line_spacing = 1.0

    r_tit = p_tit.add_run("SUMÁRIO")
    r_tit.bold = True
    r_tit.font.name = "Times New Roman"
    r_tit.font.size = Pt(12)

    origem = dados if isinstance(dados, dict) and "projeto" in dados else {"projeto": {}, "resultados": {}}
    for rotulo, bookmark in itens_do_sumario(origem, apendices, anexos, listas):
        adicionar_linha_indice(doc, rotulo, bookmark)
