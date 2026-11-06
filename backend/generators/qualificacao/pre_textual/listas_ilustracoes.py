"""
Lista de ilustrações unificada do modelo PPGSP/UFPA:
LISTA DE FIGURAS, LISTA DE GRÁFICOS, LISTA DE QUADROS e LISTA DE TABELAS
na mesma página, com uma única quebra ao final.
"""
import re

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.shared import Inches, Pt

from core.campos import adicionar_bookmark, adicionar_campo_pageref
from ..estrutura import BM_LISTA_ILUSTRACOES, tipo_ilustracao


_CATEGORIAS = (
    "LISTA DE FIGURAS",
    "LISTA DE GRÁFICOS",
    "LISTA DE QUADROS",
    "LISTA DE TABELAS",
)

_RE_ITEM = re.compile(
    r"^(?P<rotulo>[A-Za-zÀ-ÿ]+)\s+(?P<numero>\d+)\s*[-–—.:]\s*(?P<titulo>.*)$"
)

_CHAVES_LISTA = (
    "figuras",
    "graficos",
    "quadros",
    "tabelas",
    "ilustracoes",
    "lista_quadros",
    "lista_tabelas",
)


def build_lista_ilustracoes(doc, ilustracoes_data, quebrar=False):
    """Renderiza a lista contínua. `quebrar` permanece na assinatura e não abre página antes."""
    del quebrar
    grupos = _agrupar(_extrair_entradas(ilustracoes_data))
    if not grupos:
        return []

    _titulo_mestre(doc, "LISTA DE ILUSTRAÇÕES", BM_LISTA_ILUSTRACOES)
    for titulo, entradas in grupos:
        _subtitulo_categoria(doc, titulo)
        origem_anterior = None
        for item in entradas:
            origem = item.get("origem") or ""
            if origem and origem != origem_anterior:
                _agrupador_origem(doc, origem)
            origem_anterior = origem or None
            _linha_item(doc, item)
    doc.add_page_break()
    return [("LISTA DE ILUSTRAÇÕES", BM_LISTA_ILUSTRACOES)]


def _titulo_mestre(doc, texto, bookmark):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    if bookmark:
        adicionar_bookmark(p, bookmark)
    return p


def _subtitulo_categoria(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(str(texto).upper())
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def _agrupador_origem(doc, texto):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(str(texto).strip().upper())
    r.bold = False
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def _linha_item(doc, item):
    rotulo = str(item.get("rotulo") or "").strip()
    numero = str(item.get("numero") or "").strip()
    titulo = str(item.get("titulo") or "").strip()
    texto = f"{rotulo} {numero} - {titulo}".strip()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(3)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.tab_stops.add_tab_stop(
        Inches(6.299),
        WD_TAB_ALIGNMENT.RIGHT,
        WD_TAB_LEADER.DOTS,
    )

    pagina = item.get("pagina")
    if pagina is not None and str(pagina).strip() != "":
        r_txt = p.add_run(f"{rotulo} {numero} - {titulo}\t{pagina}")
        r_txt.bold = False
        r_txt.font.name = "Times New Roman"
        r_txt.font.size = Pt(12)
        return p

    r_txt = p.add_run(texto)
    r_txt.bold = False
    r_txt.font.name = "Times New Roman"
    r_txt.font.size = Pt(12)

    r_tab = p.add_run("\t")
    r_tab.font.name = "Times New Roman"
    r_tab.font.size = Pt(12)

    if item.get("bookmark"):
        adicionar_campo_pageref(p, item["bookmark"])
    return p


def _agrupar(entradas):
    grupos = {titulo: [] for titulo in _CATEGORIAS}
    for item in entradas:
        titulo, _bookmark = tipo_ilustracao(f"{item.get('rotulo', '')} {item.get('numero', '')}")
        if titulo in grupos:
            grupos[titulo].append(item)
    return [(titulo, grupos[titulo]) for titulo in _CATEGORIAS if grupos[titulo]]


def _extrair_entradas(ilustracoes_data):
    bruto = ilustracoes_data
    if isinstance(ilustracoes_data, dict):
        bruto = []
        for chave in _CHAVES_LISTA:
            bruto.extend(ilustracoes_data.get(chave) or [])
    entradas = []
    for item in bruto or []:
        normalizado = _normalizar_item(item)
        if normalizado:
            entradas.append(normalizado)
    return entradas


def _normalizar_item(item):
    if isinstance(item, dict):
        bookmark = str(item.get("bookmark") or "").strip()
        pagina = item.get("pagina")
        if not bookmark and (pagina is None or str(pagina).strip() == ""):
            return None
        rotulo = str(item.get("rotulo") or item.get("tipo") or "").strip()
        numero = item.get("numero")
        titulo = str(item.get("titulo") or item.get("legenda") or "").strip()
        if not rotulo or numero is None or str(numero).strip() == "":
            partes = _partir_legenda(titulo or rotulo)
            if not partes:
                return None
            rotulo, numero, titulo = partes
        origem = item.get("origem") or item.get("capitulo") or item.get("agrupador") or ""
        return {
            "rotulo": rotulo,
            "numero": str(numero).strip(),
            "titulo": titulo,
            "bookmark": bookmark,
            "pagina": None if pagina is None else str(pagina).strip(),
            "origem": str(origem).strip(),
        }

    if isinstance(item, (tuple, list)) and len(item) >= 2:
        legenda, ref = item[0], item[1]
        if not _parece_bookmark(ref):
            return None
        partes = _partir_legenda(legenda)
        if not partes:
            return None
        rotulo, numero, titulo = partes
        origem = ""
        if len(item) >= 3 and not _parece_bookmark(item[2]):
            origem = str(item[2] or "").strip()
        return {
            "rotulo": rotulo,
            "numero": numero,
            "titulo": titulo,
            "bookmark": str(ref).strip(),
            "pagina": None,
            "origem": origem,
        }
    return None


def _partir_legenda(texto):
    achado = _RE_ITEM.match(str(texto or "").strip())
    if not achado:
        return None
    return (
        achado.group("rotulo").strip(),
        achado.group("numero").strip(),
        achado.group("titulo").strip(),
    )


def _parece_bookmark(valor):
    texto = str(valor or "").strip()
    if not texto or " " in texto:
        return False
    return texto.startswith("leg_") or texto.startswith("sec_") or texto.startswith("pos_")
