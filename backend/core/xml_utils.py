"""Utilitários XML para controle avançado de paginação e bordas de tabelas."""
import re

from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn

_WML = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_BOOKMARK_ID_COUNTER = 100


def adicionar_bookmark(p, nome_bookmark: str):
    """Insere bookmarkStart/End com w:id inteiro sequencial único no documento."""
    global _BOOKMARK_ID_COUNTER
    _BOOKMARK_ID_COUNTER += 1
    bm_id = str(_BOOKMARK_ID_COUNTER)

    start_elem = parse_xml(
        f'<w:bookmarkStart xmlns:w="{_WML}" w:id="{bm_id}" w:name="{nome_bookmark}"/>'
    )
    end_elem = parse_xml(
        f'<w:bookmarkEnd xmlns:w="{_WML}" w:id="{bm_id}"/>'
    )

    p_pr = p._p.find(qn("w:pPr"))
    if p_pr is not None:
        p_pr.addnext(start_elem)
    else:
        p._p.insert(0, start_elem)
    p._p.append(end_elem)

_ILLEGAL_OOXML = re.compile(r"[\x00-\x08\x0B-\x0C\x0E-\x1F\uFFFE\uFFFF]")
_FRAC_LATEX = re.compile(r"(?:\\frac|\x0crac|rac)\{([^}]*)\}\{([^}]*)\}")


def sanitizar_texto_ooxml(texto: str) -> str:
    """Remove caracteres proibidos em XML 1.0 (exigência do python-docx)."""
    if not isinstance(texto, str) or not texto:
        return texto
    out = texto
    while True:
        novo, n = _FRAC_LATEX.subn(r"(\1)/(\2)", out)
        out = novo
        if n == 0:
            break
    out = out.replace("\x0barepsilon", "ε").replace("\x0bdelta", "δ")
    out = out.replace("\\varepsilon", "ε").replace("\\delta", "δ")
    out = out.replace("arepsilon", "ε")
    return _ILLEGAL_OOXML.sub("", out)


def sanitizar_estrutura(dados):
    """Aplica sanitizar_texto_ooxml recursivamente em dicts/listas."""
    if isinstance(dados, str):
        return sanitizar_texto_ooxml(dados)
    if isinstance(dados, dict):
        return {chave: sanitizar_estrutura(valor) for chave, valor in dados.items()}
    if isinstance(dados, list):
        return [sanitizar_estrutura(item) for item in dados]
    return dados

def aplicar_estilo_tabela_ibge(tabela):
    """Tabela aberta (IBGE/ABNT): topo, base do cabeçalho e fecho. Sem verticais nem grades internas."""
    tblPr = tabela._tbl.tblPr
    for filho in list(tblPr):
        if filho.tag == qn("w:tblBorders"):
            tblPr.remove(filho)

    bordas = OxmlElement("w:tblBorders")
    for aresta, valor in (
        ("top", "single"),
        ("left", "nil"),
        ("bottom", "single"),
        ("right", "nil"),
        ("insideH", "nil"),
        ("insideV", "nil"),
    ):
        elemento = OxmlElement(f"w:{aresta}")
        elemento.set(qn("w:val"), valor)
        if valor == "single":
            elemento.set(qn("w:sz"), "4")
            elemento.set(qn("w:space"), "0")
            elemento.set(qn("w:color"), "000000")
        bordas.append(elemento)
    tblPr.append(bordas)

    for celula in tabela.rows[0].cells:
        tcPr = celula._tc.get_or_add_tcPr()
        for filho in list(tcPr):
            if filho.tag == qn("w:tcBorders"):
                tcPr.remove(filho)
        tcBorders = OxmlElement("w:tcBorders")
        inferior = OxmlElement("w:bottom")
        inferior.set(qn("w:val"), "single")
        inferior.set(qn("w:sz"), "4")
        inferior.set(qn("w:space"), "0")
        inferior.set(qn("w:color"), "000000")
        tcBorders.append(inferior)
        tcPr.append(tcBorders)


def set_cell_border(cell, **kwargs):
    """Configura bordas finas para tabelas e quadros ABNT."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        edge_data = kwargs.get(edge)
        if edge_data:
            tag = f'w:{edge}'
            element = OxmlElement(tag)
            element.set(qn('w:val'), edge_data.get('val', 'single'))
            element.set(qn('w:sz'), str(edge_data.get('sz', 4)))
            element.set(qn('w:space'), '0')
            element.set(qn('w:color'), edge_data.get('color', 'auto'))
            tcBorders.append(element)
    tcPr.append(tcBorders)

def add_page_number_field(run):
    """Insere o campo PAGE como irmão do run, no parágrafo do cabeçalho."""
    fld_simple = OxmlElement("w:fldSimple")
    fld_simple.set(qn("w:instr"), " PAGE ")
    interno = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    fontes = OxmlElement("w:rFonts")
    fontes.set(qn("w:ascii"), "Times New Roman")
    fontes.set(qn("w:hAnsi"), "Times New Roman")
    tamanho = OxmlElement("w:sz")
    tamanho.set(qn("w:val"), "24")
    rpr.append(fontes)
    rpr.append(tamanho)
    interno.append(rpr)
    texto = OxmlElement("w:t")
    texto.text = "1"
    interno.append(texto)
    fld_simple.append(interno)
    run._r.addnext(fld_simple)

def configure_section_page_numbers(section, num_format='roman', start_at=None):
    """Configura numeração romana (lowerRoman) ou arábica (decimal) no XML da seção."""
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is None:
        pgNumType = OxmlElement('w:pgNumType')
        sectPr.append(pgNumType)
    pgNumType.set(qn('w:fmt'), 'lowerRoman' if num_format == 'roman' else 'decimal')
    if start_at is not None:
        pgNumType.set(qn('w:start'), str(start_at))
    else:
        start = pgNumType.get(qn('w:start'))
        if start is not None:
            del pgNumType.attrib[qn('w:start')]


def continuar_numeracao(section):
    """Mantém o formato da seção anterior e deixa a numeração seguir, sem reiniciar."""
    sectPr = section._sectPr
    pgNumType = sectPr.find(qn('w:pgNumType'))
    if pgNumType is None:
        return
    start = pgNumType.get(qn('w:start'))
    if start is not None:
        del pgNumType.attrib[qn('w:start')]