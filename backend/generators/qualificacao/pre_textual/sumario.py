"""
Sumário do Relatório de Qualificação (modelo PPGSP/UFPA).

Capa, folha de rosto, folha de aprovação e listas ficam de fora.
Os números de página são campos PAGEREF, atualizados pelo Word ao abrir o arquivo.
"""

import re

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.shared import Inches, Pt

from core.campos import adicionar_campo_pageref
from ..estrutura import itens_do_sumario

_RE_SUBSECAO = re.compile(r"^\d+\.\d+")
_RE_PRIMARIA_NUM = re.compile(r"^\d+\.\s+\S")
_RE_NUMERO_SUB = re.compile(r"^(\d+(?:\.\d+)+)\.\s+")
_PRIMARIAS_FIXAS = {"APRESENTAÇÃO", "REFERÊNCIAS"}


def build_sumario(doc, dados, apendices=None, anexos=None, listas=None, quebrar=True):
    """Monta o sumário. `listas` permanece na assinatura e não entra no índice."""
    del listas
    if quebrar:
        doc.add_page_break()

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(0)
    p_tit.paragraph_format.space_after = Pt(12)
    p_tit.paragraph_format.line_spacing = 1.0

    r_tit = p_tit.add_run("SUMÁRIO")
    r_tit.bold = True
    r_tit.font.name = "Times New Roman"
    r_tit.font.size = Pt(12)

    origem = dados if isinstance(dados, dict) and "projeto" in dados else {"projeto": {}, "resultados": {}}
    itens = itens_do_sumario(origem, apendices, anexos, listas=None)
    if not itens or itens[0][0] != "APRESENTAÇÃO":
        itens = [("APRESENTAÇÃO", "sec_apresentacao")] + [
            item for item in itens if item[0] != "APRESENTAÇÃO"
        ]

    for rotulo, bookmark in itens:
        _linha_sumario(doc, _exibir(rotulo), bookmark)

    doc.add_page_break()


def _exibir(rotulo):
    texto = str(rotulo or "").strip()
    texto = _RE_NUMERO_SUB.sub(r"\1 ", texto)
    if texto.upper().startswith("APÊNDICE"):
        return "Apêndice" + texto[len("APÊNDICE"):]
    if texto.upper().startswith("ANEXO"):
        return "Anexo" + texto[len("ANEXO"):]
    return texto


def _primaria(rotulo):
    if rotulo in _PRIMARIAS_FIXAS:
        return True
    if _RE_SUBSECAO.match(rotulo):
        return False
    return bool(_RE_PRIMARIA_NUM.match(rotulo))


def _linha_sumario(doc, titulo, bookmark):
    """Uma entrada: título, tabulação pontilhada à direita (16 cm) e página."""
    apresentacao = bookmark == "sec_apresentacao"
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.tab_stops.add_tab_stop(
        Inches(6.299),
        WD_TAB_ALIGNMENT.RIGHT,
        WD_TAB_LEADER.DOTS,
    )

    r_txt = p.add_run(f"{titulo}\t")
    r_txt.bold = _primaria(titulo)
    r_txt.font.name = "Times New Roman"
    r_txt.font.size = Pt(12)

    adicionar_campo_pageref(
        p,
        bookmark,
        italico=apresentacao,
        formato="roman" if apresentacao else None,
    )
    return p
