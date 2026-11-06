"""Tabelas estatísticas no padrão IBGE / ABNT NBR 14724.

Sequência obrigatória: título acima, grade e fonte abaixo.
Bordas só no topo, sob o cabeçalho e no fecho; laterais abertas.
"""

from __future__ import annotations

import re

from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor

_FONTE = "Times New Roman"
_CINZA_CABECALHO = "F2F2F2"
_BORDA_PT_OITAVOS = "4"  # 0,5 pt
_NUMERO = re.compile(
    r"^[\s\d.,%‰+\-–—/()nN=<>≤≥]+$",
)


def inserir_tabela(
    doc,
    numero,
    titulo,
    colunas,
    linhas,
    fonte,
    alinhamentos=None,
    bookmark=None,
    fundo_cabecalho=True,
):
    """Insere título, grade IBGE e fonte.

    ``numero`` entra em ``Tabela {numero} – {titulo}``.
    ``fonte`` é o crédito, sem o prefixo ``Fonte:``.
    ``alinhamentos`` é opcional; se omitido, a primeira coluna fica à
    esquerda e colunas numéricas à direita.
    """
    paragrafo_titulo = doc.add_paragraph()
    paragrafo_titulo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragrafo_titulo.paragraph_format.space_before = Pt(12)
    paragrafo_titulo.paragraph_format.space_after = Pt(3)
    paragrafo_titulo.paragraph_format.line_spacing = 1.0
    _run(paragrafo_titulo, f"Tabela {numero} – {titulo}", tamanho=12, negrito=False)
    catalogo = getattr(doc, "_catalogo", None)
    if catalogo is not None:
        catalogo.registrar_ilustracao("Tabela", numero, titulo, "Tabela", "Metodologia")
    if bookmark:
        from core.campos import adicionar_bookmark

        adicionar_bookmark(paragrafo_titulo, bookmark)

    colunas = [str(coluna) for coluna in colunas]
    linhas = [["" if valor is None else str(valor) for valor in linha] for linha in linhas]
    if alinhamentos is None:
        alinhamentos = _alinhamentos_automaticos(colunas, linhas)
    else:
        alinhamentos = list(alinhamentos)

    tabela = doc.add_table(rows=1, cols=len(colunas))
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER
    tabela.autofit = True
    _marcar_cabecalho_repetivel(tabela.rows[0])

    for indice, nome in enumerate(colunas):
        alinhamento = alinhamentos[indice] if indice < len(alinhamentos) else WD_ALIGN_PARAGRAPH.LEFT
        if indice == 0:
            alinhamento = WD_ALIGN_PARAGRAPH.LEFT
        _preencher_celula(
            tabela.rows[0].cells[indice],
            nome,
            alinhamento,
            negrito=True,
            fundo=_CINZA_CABECALHO if fundo_cabecalho else None,
        )

    for linha in linhas:
        celulas = tabela.add_row().cells
        total = _eh_total(linha)
        for indice, valor in enumerate(linha):
            if indice >= len(celulas):
                break
            alinhamento = (
                alinhamentos[indice] if indice < len(alinhamentos) else WD_ALIGN_PARAGRAPH.LEFT
            )
            _preencher_celula(celulas[indice], valor, alinhamento, negrito=total)

    aplicar_bordas_ibge(tabela)

    paragrafo_fonte = doc.add_paragraph()
    paragrafo_fonte.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragrafo_fonte.paragraph_format.space_before = Pt(3)
    paragrafo_fonte.paragraph_format.space_after = Pt(12)
    paragrafo_fonte.paragraph_format.line_spacing = 1.0
    credito = fonte.strip()
    if credito.lower().startswith("fonte:"):
        credito = credito.split(":", 1)[1].strip()
    _run(paragrafo_fonte, "Fonte:", tamanho=10, negrito=True)
    if credito:
        _run(paragrafo_fonte, f" {credito}", tamanho=10, negrito=False)
    return tabela


def aplicar_bordas_ibge(tabela):
    """Topo, linha sob o cabeçalho e fecho em 0,5 pt. Sem laterais nem grade interna."""
    tbl_pr = tabela._tbl.tblPr
    for filho in list(tbl_pr):
        if filho.tag == qn("w:tblBorders"):
            tbl_pr.remove(filho)

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
        elemento.set(qn("w:sz"), _BORDA_PT_OITAVOS if valor == "single" else "0")
        elemento.set(qn("w:space"), "0")
        elemento.set(qn("w:color"), "000000" if valor == "single" else "auto")
        bordas.append(elemento)
    tbl_pr.append(bordas)

    if not tabela.rows:
        return
    for celula in tabela.rows[0].cells:
        tc_pr = celula._tc.get_or_add_tcPr()
        for filho in list(tc_pr):
            if filho.tag == qn("w:tcBorders"):
                tc_pr.remove(filho)
        tc_borders = OxmlElement("w:tcBorders")
        for aresta in ("top", "left", "right"):
            vazio = OxmlElement(f"w:{aresta}")
            vazio.set(qn("w:val"), "nil")
            vazio.set(qn("w:sz"), "0")
            vazio.set(qn("w:space"), "0")
            tc_borders.append(vazio)
        inferior = OxmlElement("w:bottom")
        inferior.set(qn("w:val"), "single")
        inferior.set(qn("w:sz"), _BORDA_PT_OITAVOS)
        inferior.set(qn("w:space"), "0")
        inferior.set(qn("w:color"), "000000")
        tc_borders.append(inferior)
        tc_pr.append(tc_borders)


def _marcar_cabecalho_repetivel(linha):
    tr_pr = linha._tr.get_or_add_trPr()
    if tr_pr.find(qn("w:tblHeader")) is None:
        tr_pr.append(OxmlElement("w:tblHeader"))


def _preencher_celula(celula, texto, alinhamento, negrito=False, fundo=None):
    celula.text = ""
    celula.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    paragrafo = celula.paragraphs[0]
    if hasattr(paragrafo, "clear"):
        paragrafo.clear()
    else:
        for run in list(paragrafo.runs):
            run._element.getparent().remove(run._element)
    paragrafo.alignment = alinhamento
    paragrafo.paragraph_format.line_spacing = 1.0
    paragrafo.paragraph_format.space_before = Pt(0)
    paragrafo.paragraph_format.space_after = Pt(0)
    _run(paragrafo, texto, tamanho=10, negrito=negrito)
    if fundo:
        _sombrear(celula, fundo)
    _margem_celula(celula)


def _run(paragrafo, texto, tamanho, negrito):
    run = paragrafo.add_run(texto)
    run.font.name = _FONTE
    run.font.size = Pt(tamanho)
    run.bold = negrito
    run.font.color.rgb = RGBColor(0, 0, 0)
    r_pr = run._element.get_or_add_rPr()
    fontes = r_pr.find(qn("w:rFonts"))
    if fontes is None:
        fontes = OxmlElement("w:rFonts")
        r_pr.append(fontes)
    for atributo in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fontes.set(qn(atributo), _FONTE)
    return run


def _sombrear(celula, preenchimento):
    tc_pr = celula._tc.get_or_add_tcPr()
    for filho in list(tc_pr):
        if filho.tag == qn("w:shd"):
            tc_pr.remove(filho)
    sombra = OxmlElement("w:shd")
    sombra.set(qn("w:val"), "clear")
    sombra.set(qn("w:color"), "auto")
    sombra.set(qn("w:fill"), preenchimento)
    tc_pr.append(sombra)


def _margem_celula(celula):
    tc_pr = celula._tc.get_or_add_tcPr()
    margens = tc_pr.find(qn("w:tcMar"))
    if margens is not None:
        tc_pr.remove(margens)
    margens = OxmlElement("w:tcMar")
    for aresta, twips in (("top", 40), ("left", 60), ("bottom", 40), ("right", 60)):
        elemento = OxmlElement(f"w:{aresta}")
        elemento.set(qn("w:w"), str(twips))
        elemento.set(qn("w:type"), "dxa")
        margens.append(elemento)
    tc_pr.append(margens)


def _eh_total(linha):
    if not linha:
        return False
    rotulo = linha[0].strip().casefold().rstrip(":.")
    return rotulo == "total"


def _alinhamentos_automaticos(colunas, linhas):
    alinhamentos = []
    for indice in range(len(colunas)):
        if indice == 0:
            alinhamentos.append(WD_ALIGN_PARAGRAPH.LEFT)
            continue
        valores = []
        for linha in linhas:
            if indice >= len(linha):
                continue
            texto = linha[indice].strip()
            if not texto or _eh_total(linha):
                continue
            valores.append(texto)
        if valores and all(_NUMERO.match(valor) for valor in valores):
            alinhamentos.append(WD_ALIGN_PARAGRAPH.RIGHT)
        else:
            alinhamentos.append(WD_ALIGN_PARAGRAPH.LEFT)
    return alinhamentos
