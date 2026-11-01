"""
Lista de símbolos, na ordem em que aparecem no trabalho.
"""

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from ..estrutura import BM_LISTA_SIMBOLOS
from ..formato import adicionar_titulo_lista


def _extrair(metadata):
    if isinstance(metadata, dict):
        simbolos_raw = metadata.get("simbolos", [])
    else:
        simbolos_raw = metadata or []
    pares = []
    for item in simbolos_raw:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            simbolo = str(item[0]).strip()
            significado = str(item[1]).strip()
        elif isinstance(item, str) and ("–" in item or "-" in item):
            delimitador = "–" if "–" in item else "-"
            partes = item.split(delimitador, 1)
            simbolo = partes[0].strip()
            significado = partes[1].strip()
        else:
            simbolo = str(item).strip()
            significado = ""
        if simbolo:
            pares.append((simbolo, significado))
    return pares


def build_lista_simbolos(doc, metadata, quebrar=True):
    pares = _extrair(metadata)
    if not pares:
        return None
    if quebrar:
        doc.add_page_break()

    adicionar_titulo_lista(doc, "LISTA DE SÍMBOLOS", BM_LISTA_SIMBOLOS)
    for simbolo, significado in pares:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        p.paragraph_format.first_line_indent = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r_linha = p.add_run(f"{simbolo} – {significado}" if significado else simbolo)
        r_linha.font.name = "Times New Roman"
        r_linha.font.size = Pt(12)
    return ("LISTA DE SÍMBOLOS", BM_LISTA_SIMBOLOS)
