"""
Lista de abreviaturas e siglas.
Só é emitida quando o projeto informa ao menos um par.
"""

from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from ..estrutura import BM_LISTA_SIGLAS
from ..formato import adicionar_titulo_lista


def normalizar_siglas(siglas_data):
    lista_siglas = []
    if isinstance(siglas_data, dict):
        lista_siglas = siglas_data.get("siglas", siglas_data.get("lista_siglas", []))
    elif isinstance(siglas_data, list):
        lista_siglas = siglas_data

    pares = []
    for item in lista_siglas or []:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            sigla = str(item[0]).strip()
            significado = str(item[1]).strip()
        elif isinstance(item, dict):
            sigla = str(item.get("sigla", "")).strip()
            significado = str(item.get("significado", item.get("descricao", ""))).strip()
        elif isinstance(item, str) and ("–" in item or "-" in item):
            partes = item.replace("–", "-").split("-", 1)
            sigla, significado = partes[0].strip(), partes[1].strip()
        elif isinstance(item, str) and item.strip():
            sigla, significado = item.strip(), ""
        else:
            continue
        if sigla:
            pares.append((sigla, significado))
    pares.sort(key=lambda par: par[0].upper())
    return pares


def build_lista_siglas(doc, siglas_data, quebrar=True):
    pares = normalizar_siglas(siglas_data)
    if not pares:
        return None
    if quebrar:
        doc.add_page_break()

    adicionar_titulo_lista(doc, "LISTA DE ABREVIATURAS E SIGLAS", BM_LISTA_SIGLAS)
    for sigla, significado in pares:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(0)
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)

        r_sigla = p.add_run(sigla)
        r_sigla.bold = True
        r_sigla.font.name = "Times New Roman"
        r_sigla.font.size = Pt(12)

        if significado:
            r_sep = p.add_run(" – ")
            r_sep.font.name = "Times New Roman"
            r_sep.font.size = Pt(12)
            r_sig = p.add_run(significado)
            r_sig.font.name = "Times New Roman"
            r_sig.font.size = Pt(12)
    return ("LISTA DE ABREVIATURAS E SIGLAS", BM_LISTA_SIGLAS)
