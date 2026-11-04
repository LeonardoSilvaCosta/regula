"""
Lista de símbolos.
Só é emitida quando o documento informa ao menos um item.
"""

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.shared import Inches, Pt

from core.campos import adicionar_bookmark
from ..estrutura import BM_LISTA_SIMBOLOS


def normalizar_simbolos(simbolos_data):
    if isinstance(simbolos_data, dict):
        itens = simbolos_data.get("simbolos", [])
    else:
        itens = simbolos_data or []

    pares = []
    for item in itens:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            simbolo = str(item[0]).strip()
            significado = str(item[1]).strip()
        elif isinstance(item, dict):
            simbolo = str(item.get("simbolo", "")).strip()
            significado = str(item.get("significado", item.get("descricao", ""))).strip()
        elif hasattr(item, "simbolo"):
            simbolo = str(getattr(item, "simbolo", "")).strip()
            significado = str(getattr(item, "significado", "")).strip()
        elif isinstance(item, str) and item.strip():
            simbolo, significado = item.strip(), ""
        else:
            continue
        if simbolo:
            pares.append((simbolo, significado))
    return pares


def _titulo(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run("LISTA DE SÍMBOLOS")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    adicionar_bookmark(p, BM_LISTA_SIMBOLOS)
    return p


def _linha(doc, simbolo, significado):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.tab_stops.add_tab_stop(
        Inches(0.472),
        WD_TAB_ALIGNMENT.LEFT,
        WD_TAB_LEADER.SPACES,
    )
    r = p.add_run(f"{simbolo}\t{significado}")
    r.bold = False
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def build_lista_simbolos(doc, simbolos_data, quebrar=True):
    pares = normalizar_simbolos(simbolos_data)
    if not pares:
        return None
    if quebrar:
        doc.add_page_break()

    _titulo(doc)
    for simbolo, significado in pares:
        _linha(doc, simbolo, significado)
    doc.add_page_break()
    return ("LISTA DE SÍMBOLOS", BM_LISTA_SIMBOLOS)
