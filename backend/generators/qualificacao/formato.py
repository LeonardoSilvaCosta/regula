"""Títulos e parágrafos da Resolução nº 009/2025."""
import re

from docx.shared import Cm, Pt, RGBColor, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.campos import adicionar_bookmark, ancorar_paragrafo, aplicar_tabulacao_coluna


def adicionar_titulo(doc, texto, bookmark=None, primario=True, marcar=True):
    """Título justificado, sem negrito, com uma linha em branco antes do texto."""
    p = doc.add_paragraph(style="Heading 1" if primario else "Heading 2")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(18 if primario else 12)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.5
    r = p.add_run(texto)
    r.bold = False
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    if marcar:
        ancorar_paragrafo(p, texto, bookmark=bookmark)
    return p


def adicionar_titulo_produto(doc, texto, secao, bookmark=None):
    """Até 'PRODUTO N.' regular; depois do ponto, tipo e título em negrito."""
    chave = "PRODUTO "
    pos = texto.find(chave)
    if pos >= 0:
        depois = texto[pos + len(chave) :]
        ponto = depois.find(".")
        if ponto >= 0:
            corte = pos + len(chave) + ponto + 1
            inicio, resto = texto[:corte], texto[corte:]
        else:
            inicio, resto = texto, ""
    else:
        inicio, resto = texto, ""
    p = doc.add_paragraph(style="Título de Produto")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.5
    r_rotulo = p.add_run(inicio)
    r_rotulo.bold = False
    r_rotulo.font.name = "Times New Roman"
    r_rotulo.font.size = Pt(12)
    if resto:
        r_tit = p.add_run(resto)
        r_tit.bold = True
        r_tit.font.name = "Times New Roman"
        r_tit.font.size = Pt(12)
    if bookmark:
        ancorar_paragrafo(p, texto, bookmark=bookmark)
    return p


def adicionar_titulo_lista(doc, texto, bookmark):
    """Título de lista pré-textual: centralizado, Times 12, espaço simples."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(18)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    if bookmark:
        adicionar_bookmark(p, bookmark)
    return p


def adicionar_linha_par_alinhado(doc, rotulo, descricao, pos_twips):
    """Sigla/símbolo e forma por extenso em colunas, sem negrito e sem travessão."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.left_indent = Twips(pos_twips)
    p.paragraph_format.first_line_indent = Twips(-pos_twips)
    aplicar_tabulacao_coluna(p, pos_twips)

    r_rotulo = p.add_run(rotulo)
    r_rotulo.bold = False
    r_rotulo.font.name = "Times New Roman"
    r_rotulo.font.size = Pt(12)
    if descricao:
        r_desc = p.add_run("\t" + descricao)
        r_desc.bold = False
        r_desc.font.name = "Times New Roman"
        r_desc.font.size = Pt(12)
    return p


def adicionar_subtitulo_lista(doc, texto):
    """Sublista da lista de ilustrações: à esquerda, Times 12 negrito."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto)
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


_RE_ROTULO_LEGENDA = re.compile(
    r"^((?:Quadro|Tabela|Figura|Gráfico|Grafico)\s+\d+)\.\s*",
    re.IGNORECASE,
)


def partir_legenda(texto):
    """Separa 'Quadro 1.' do restante da legenda."""
    texto = texto or ""
    achado = _RE_ROTULO_LEGENDA.match(texto)
    if achado:
        return achado.group(1) + ".", texto[achado.end() :]
    ponto = texto.find(".")
    if ponto >= 0:
        return texto[: ponto + 1], texto[ponto + 1 :].lstrip()
    return texto, ""


def escrever_legenda(paragrafo, texto, tamanho=12):
    """Negrito até o ponto do rótulo; o título descritivo fica sem negrito."""
    rotulo, resto = partir_legenda(texto)
    r_rotulo = paragrafo.add_run(rotulo)
    r_rotulo.bold = True
    r_rotulo.font.name = "Times New Roman"
    r_rotulo.font.size = Pt(tamanho)
    if resto:
        r_resto = paragrafo.add_run(" " + resto if not resto.startswith(" ") else resto)
        r_resto.bold = False
        r_resto.font.name = "Times New Roman"
        r_resto.font.size = Pt(tamanho)
    return paragrafo


def escrever_legenda_quadro_1(paragrafo, texto, tamanho=11):
    """Modelo oficial: 'Quadro 1 - ' e o título entre aspas em negrito; o miolo, sem."""
    texto = texto or ""
    marca = "Quadro 1 - "
    abre = texto.find("“")
    fecha = texto.rfind("”")
    if texto.startswith(marca) and abre > len(marca) and fecha > abre:
        trechos = [
            (texto[: len(marca)], True),
            (texto[len(marca) : abre + 1], False),
            (texto[abre + 1 : fecha], True),
            (texto[fecha:], False),
        ]
    else:
        trechos = [(texto, True)]
    for parte, negrito in trechos:
        if not parte:
            continue
        run = paragrafo.add_run(parte)
        run.bold = negrito
        run.font.name = "Times New Roman"
        run.font.size = Pt(tamanho)
    return paragrafo


def escrever_fonte(paragrafo, texto, tamanho=10):
    """Negrito até os dois-pontos de 'Fonte:'; o crédito fica sem negrito."""
    texto = texto or ""
    corte = texto.find(":")
    if corte >= 0:
        rotulo, resto = texto[: corte + 1], texto[corte + 1 :]
    else:
        rotulo, resto = texto, ""
    r_rotulo = paragrafo.add_run(rotulo)
    r_rotulo.bold = True
    r_rotulo.font.name = "Times New Roman"
    r_rotulo.font.size = Pt(tamanho)
    if resto:
        r_resto = paragrafo.add_run(resto)
        r_resto.bold = False
        r_resto.font.name = "Times New Roman"
        r_resto.font.size = Pt(tamanho)
    return paragrafo


def adicionar_paragrafo(doc, texto):
    p = doc.add_paragraph(style="Corpo de Texto")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(texto)
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    return p


def adicionar_lacuna(doc, texto):
    p = doc.add_paragraph(style="Corpo de Texto")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.first_line_indent = Cm(1.27)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(texto)
    r.italic = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    r.font.color.rgb = RGBColor(115, 115, 115)
    return p
