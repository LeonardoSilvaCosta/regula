"""
Lista de abreviaturas e siglas.
Só é emitida quando o projeto informa ao menos um par.
"""

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.shared import Inches, Pt

from core.campos import adicionar_bookmark
from ..estrutura import BM_LISTA_SIGLAS


def normalizar_siglas(siglas_data):
    lista_siglas = []
    if isinstance(siglas_data, dict):
        lista_siglas = siglas_data.get("siglas", siglas_data.get("lista_siglas", []))
    elif isinstance(siglas_data, list):
        lista_siglas = siglas_data

    vistos = set()
    pares = []
    for item in lista_siglas or []:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            sigla = str(item[0]).strip()
            significado = str(item[1]).strip()
        elif isinstance(item, dict):
            sigla = str(item.get("sigla", "")).strip()
            significado = str(item.get("significado", item.get("descricao", ""))).strip()
        elif hasattr(item, "sigla"):
            sigla = str(getattr(item, "sigla", "")).strip()
            significado = str(getattr(item, "significado", getattr(item, "descricao", ""))).strip()
        elif isinstance(item, str) and ("–" in item or "-" in item):
            partes = item.replace("–", "-").split("-", 1)
            sigla, significado = partes[0].strip(), partes[1].strip()
        elif isinstance(item, str) and item.strip():
            sigla, significado = item.strip(), ""
        else:
            continue
        chave = sigla.upper()
        if not chave or chave in vistos:
            continue
        vistos.add(chave)
        pares.append((sigla, significado))
    pares.sort(key=lambda par: par[0].upper())
    return pares


def _titulo(doc):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run("LISTA DE ABREVIATURAS E SIGLAS")
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    adicionar_bookmark(p, BM_LISTA_SIGLAS)
    return p


def _linha(doc, sigla, significado):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.tab_stops.add_tab_stop(
        Inches(1.10),
        WD_TAB_ALIGNMENT.LEFT,
        WD_TAB_LEADER.SPACES,
    )
    r = p.add_run(f"{sigla}\t{significado}")
    r.bold = False
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def build_lista_siglas(doc, siglas_data, quebrar=True):
    pares = normalizar_siglas(siglas_data)
    if not pares:
        return None
    if quebrar:
        doc.add_page_break()

    _titulo(doc)
    for sigla, significado in pares:
        _linha(doc, sigla, significado)
    doc.add_page_break()
    return ("LISTA DE ABREVIATURAS E SIGLAS", BM_LISTA_SIGLAS)
