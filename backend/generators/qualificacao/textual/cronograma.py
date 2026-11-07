"""
Cronograma no modelo mensal da Resolução nº 009/2025.
Sem atividades informadas no projeto, entra o quadro canônico do PPGSP.
"""

from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from core.styles import set_page_margins
from core.xml_utils import continuar_numeracao, set_cell_border

from core.campos import adicionar_bookmark
from ..formato import adicionar_lacuna, adicionar_paragrafo, escrever_fonte, escrever_legenda
from ..pre_textual.sumario import registrar_entrada
from ..legendas import BM_QUADRO_2, legenda_quadro_2


_LARGURA_ATIVIDADE = Inches(1.9)
_LARGURA_MES = Inches(0.18)
_N_MESES = 24
_CINZA_MES = "BEBEBE"

# Nove atividades do mestrado. Só os meses fixados no modelo oficial
# (pesquisa ao longo do curso, qualificação no mês 12 e defesa no mês 24).
ATIVIDADES_MESTRADO = [
    ("Pesquisa Bibliográfica", list(range(1, 25))),
    ("Redação Preliminar", []),
    ("Qualificação", [12]),
    ("Coleta", []),
    ("Análise", []),
    ("Discussão", []),
    ("Redação da Dissertação", []),
    ("Revisão", []),
    ("Defesa", [24]),
]

NOMES_DOUTORADO = [
    "Disciplinas Obrigatórias e Optativas",
    "Pesquisa Documental",
    "Redação Preliminar",
    "Qualificação",
    "Coleta de Dados",
    "Análise de Dados",
    "Discussão Teórica",
    "Desenvolvimento dos Produtos Técnicos/Tecnológicos",
    "Redação da Tese",
    "Revisão da Redação da Tese",
    "Defesa da Tese",
]


def _secao_paisagem(doc):
    """A4 deitado para o quadro de 24 ou 48 meses. Cabeçalho segue a seção anterior."""
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    set_page_margins(section)
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width = Cm(29.7)
    section.page_height = Cm(21.0)
    section.header.is_linked_to_previous = True
    section.footer.is_linked_to_previous = True
    continuar_numeracao(section)
    return section


def _secao_retrato(doc):
    section = doc.add_section(WD_SECTION.NEW_PAGE)
    set_page_margins(section)
    section.header.is_linked_to_previous = True
    section.footer.is_linked_to_previous = True
    continuar_numeracao(section)
    return section


def build_cronograma(doc, dados_projeto, nivel="mestrado", ano_referencia="2026", numero=6):
    _secao_paisagem(doc)
    is_doutorado = str(nivel).strip().lower() in ["doutorado", "tese"]
    titulo = _titulo_secao(doc, f"{numero}. CRONOGRAMA", bookmark="sec_cronograma")
    registrar_entrada(doc, f"{numero}. CRONOGRAMA", 1, "_TOC_CRONOGRAMA", titulo)
    adicionar_paragrafo(
        doc,
        "O cronograma a seguir sistematiza a distribuição temporal estimada para a execução "
        "das principais etapas da pesquisa até a qualificação do projeto e a defesa final:",
    )

    atividades, informado = _atividades(dados_projeto.get("cronograma"), is_doutorado)
    if is_doutorado:
        _bloco(
            doc,
            legenda_quadro_2("doutorado", parte="continua"),
            BM_QUADRO_2,
            atividades,
            [("Ano 1", 1), ("Ano 2", 13)],
        )
        _bloco(
            doc,
            legenda_quadro_2("doutorado", parte="conclusao"),
            None,
            atividades,
            [("Ano 3", 25), ("Ano 4", 37)],
        )
    else:
        _bloco(
            doc,
            legenda_quadro_2("mestrado"),
            BM_QUADRO_2,
            atividades,
            [("Ano 1", 1), ("Ano 2", 13)],
        )

    if not informado and not any(meses for _, meses in atividades):
        adicionar_lacuna(doc, "[Meses de execução não informados no projeto.]")

    p_f = doc.add_paragraph()
    p_f.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_f.paragraph_format.space_before = Pt(3)
    p_f.paragraph_format.space_after = Pt(12)
    p_f.paragraph_format.line_spacing = 1.0
    escrever_fonte(p_f, f"Fonte: Elaborado pelo(a) autor(a), {ano_referencia}.")
    _secao_retrato(doc)


def _titulo_secao(doc, texto, bookmark=None):
    p = doc.add_paragraph(style="Heading 1")
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(texto.upper())
    r.bold = False
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    if bookmark:
        adicionar_bookmark(p, bookmark)
    return p


def _atividades(bruto, doutorado):
    atividades = []
    for item in bruto or []:
        if isinstance(item, (list, tuple)) and item:
            nome = str(item[0]).strip()
            meses = _meses(item[1] if len(item) > 1 else [])
        elif isinstance(item, dict):
            nome = str(item.get("atividade") or item.get("nome") or "").strip()
            meses = _meses(item.get("meses") or [])
        else:
            continue
        if nome:
            atividades.append((nome, meses))
    if atividades:
        return atividades, True
    if doutorado:
        return [(nome, []) for nome in NOMES_DOUTORADO], False
    return list(ATIVIDADES_MESTRADO), False


def _meses(valor):
    meses = []
    for item in valor or []:
        try:
            meses.append(int(item))
        except (TypeError, ValueError):
            continue
    return meses


def _larguras():
    return [_LARGURA_ATIVIDADE] + [_LARGURA_MES] * _N_MESES


def _bloco(doc, legenda, bookmark, atividades, anos):
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_tit.paragraph_format.space_before = Pt(0)
    p_tit.paragraph_format.space_after = Pt(6)
    p_tit.paragraph_format.line_spacing = 1.0
    escrever_legenda(p_tit, legenda, tamanho=12)
    if bookmark:
        adicionar_bookmark(p_tit, bookmark)
    catalogo = getattr(doc, "_catalogo", None)
    if catalogo is not None:
        catalogo.registrar_legenda(legenda, "Cronograma")

    tabela = doc.add_table(rows=2 + len(atividades), cols=25)
    tabela.alignment = WD_TABLE_ALIGNMENT.LEFT
    tabela.autofit = False
    _grade_fixa(tabela)
    _margem_celulas(tabela)
    _bordas_tabela(tabela)

    tabela.rows[0].cells[0].merge(tabela.rows[1].cells[0])
    _celula(tabela.rows[0].cells[0], "Atividades", 0, centro=True, tamanho=9, negrito=True)

    inicio_ano = [1, 13]
    for indice, (rotulo, _) in enumerate(anos):
        primeira = inicio_ano[indice]
        tabela.rows[0].cells[primeira].merge(tabela.rows[0].cells[primeira + 11])
        _celula(tabela.rows[0].cells[primeira], rotulo, primeira, centro=True, tamanho=9, negrito=True)
        for mes in range(12):
            _celula(
                tabela.rows[1].cells[primeira + mes],
                str(mes + 1),
                primeira + mes,
                centro=True,
                tamanho=8,
                negrito=True,
            )

    for r_idx, (nome, meses) in enumerate(atividades, start=2):
        _celula(tabela.rows[r_idx].cells[0], nome, 0, centro=False, tamanho=9)
        presentes = set(meses)
        for indice, (_, inicio) in enumerate(anos):
            primeira = inicio_ano[indice]
            for mes in range(12):
                coluna = primeira + mes
                absoluto = inicio + mes
                _celula(tabela.rows[r_idx].cells[coluna], "", coluna, centro=True, tamanho=8)
                if absoluto in presentes:
                    colorir_celula(tabela.rows[r_idx].cells[coluna], _CINZA_MES)


def colorir_celula(cell, cor_hex="BEBEBE"):
    shading = parse_xml(
        f'<w:shd xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        f'w:val="clear" w:color="auto" w:fill="{cor_hex}"/>'
    )
    cell._tc.get_or_add_tcPr().append(shading)


def _grade_fixa(tabela):
    larguras = [int(round(item.twips)) for item in _larguras()]
    tbl = tabela._tbl
    tbl_pr = tbl.tblPr
    layout = tbl_pr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tbl_pr.append(layout)
    layout.set(qn("w:type"), "fixed")
    tbl_w = tbl_pr.find(qn("w:tblW"))
    if tbl_w is None:
        tbl_w = OxmlElement("w:tblW")
        tbl_pr.append(tbl_w)
    tbl_w.set(qn("w:w"), str(sum(larguras)))
    tbl_w.set(qn("w:type"), "dxa")
    grade = tbl.find(qn("w:tblGrid"))
    if grade is None:
        grade = OxmlElement("w:tblGrid")
        tbl_pr.addnext(grade)
    for filho in list(grade):
        grade.remove(filho)
    for largura in larguras:
        coluna = OxmlElement("w:gridCol")
        coluna.set(qn("w:w"), str(largura))
        grade.append(coluna)


def _margem_celulas(tabela):
    tbl_pr = tabela._tbl.tblPr
    margem = tbl_pr.find(qn("w:tblCellMar"))
    if margem is None:
        margem = OxmlElement("w:tblCellMar")
        tbl_pr.append(margem)
    for lado in ("top", "left", "bottom", "right"):
        atual = margem.find(qn(f"w:{lado}"))
        if atual is None:
            atual = OxmlElement(f"w:{lado}")
            margem.append(atual)
        atual.set(qn("w:w"), "20")
        atual.set(qn("w:type"), "dxa")


def _bordas_tabela(tabela):
    tbl_pr = tabela._tbl.tblPr
    bordas = tbl_pr.find(qn("w:tblBorders"))
    if bordas is None:
        bordas = OxmlElement("w:tblBorders")
        tbl_pr.append(bordas)
    for lado in ("top", "left", "bottom", "right", "insideH", "insideV"):
        atual = bordas.find(qn(f"w:{lado}"))
        if atual is None:
            atual = OxmlElement(f"w:{lado}")
            bordas.append(atual)
        atual.set(qn("w:val"), "single")
        atual.set(qn("w:sz"), "4")
        atual.set(qn("w:space"), "0")
        atual.set(qn("w:color"), "000000")


def _celula(celula, texto, coluna, centro=False, tamanho=10, negrito=False):
    larguras = _larguras()
    celula.width = larguras[coluna]
    celula.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    celula.text = texto
    p = celula.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centro else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    if p.runs:
        p.runs[0].font.name = "Times New Roman"
        p.runs[0].font.size = Pt(tamanho)
        p.runs[0].bold = negrito
    set_cell_border(
        celula,
        top={"sz": 4, "val": "single", "color": "000000"},
        bottom={"sz": 4, "val": "single", "color": "000000"},
        left={"sz": 4, "val": "single", "color": "000000"},
        right={"sz": 4, "val": "single", "color": "000000"},
    )
