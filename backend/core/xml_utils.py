"""Utilitários XML para controle avançado de paginação e bordas de tabelas."""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

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
    """Insere o campo dinâmico nativo de paginação do Word (PAGE)."""
    fldSimple = OxmlElement('w:fldSimple')
    fldSimple.set(qn('w:instr'), 'PAGE')
    run._r.append(fldSimple)

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