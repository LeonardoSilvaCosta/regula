"""
Cronograma no modelo mensal da Resolução nº 009/2025.
Sem dados do projeto, as atividades do modelo ficam com os meses em branco.
"""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from core.xml_utils import set_cell_border
from core.campos import adicionar_bookmark
from ..formato import adicionar_lacuna, adicionar_paragrafo, adicionar_titulo, escrever_fonte, escrever_legenda
from ..legendas import BM_QUADRO_2, legenda_quadro_2


# Larguras do modelo (twips). A primeira coluna cede 50 twips para caber nos 16 cm úteis.
_LARGURAS = [
    2727, 240, 240, 240, 240, 240, 240, 240, 240, 240, 338, 340, 340,
    239, 239, 239, 239, 240, 239, 239, 239, 239, 337, 339, 339,
]
_CINZA_MES = "BEBEBE"


NOMES_MESTRADO = [
    "Pesquisa Bibliográfica",
    "Redação Preliminar do Projeto",
    "Qualificação do Projeto",
    "Coleta de Dados",
    "Análise de Dados",
    "Discussão Teórica",
    "Redação da Dissertação",
    "Revisão da redação da Dissertação",
    "Defesa da Dissertação",
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


def build_cronograma(doc, dados_projeto, nivel="mestrado", ano_referencia="2026", numero=6):
    is_doutorado = str(nivel).strip().lower() in ["doutorado", "tese"]
    adicionar_titulo(doc, f"{numero}. CRONOGRAMA", bookmark="sec_cronograma")
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

    if not informado:
        adicionar_lacuna(doc, "[Meses de execução não informados no projeto.]")

    p_f = doc.add_paragraph()
    p_f.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_f.paragraph_format.space_before = Pt(2)
    p_f.paragraph_format.space_after = Pt(18)
    p_f.paragraph_format.line_spacing = 1.0
    escrever_fonte(p_f, f"Fonte: Elaborado pelo autor, {ano_referencia}.")


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
    nomes = NOMES_DOUTORADO if doutorado else NOMES_MESTRADO
    return [(nome, []) for nome in nomes], False


def _meses(valor):
    meses = []
    for item in valor or []:
        try:
            meses.append(int(item))
        except (TypeError, ValueError):
            continue
    return meses


def _bloco(doc, legenda, bookmark, atividades, anos):
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_tit.paragraph_format.space_before = Pt(12)
    p_tit.paragraph_format.space_after = Pt(4)
    p_tit.paragraph_format.line_spacing = 1.0
    escrever_legenda(p_tit, legenda)
    if bookmark:
        adicionar_bookmark(p_tit, bookmark)

    tabela = doc.add_table(rows=2 + len(atividades), cols=25)
    tabela.alignment = WD_TABLE_ALIGNMENT.LEFT
    tabela.autofit = False
    _grade_fixa(tabela)
    _margem_celulas(tabela)
    _bordas_tabela(tabela)

    _celula(tabela.rows[0].cells[0], "Atividades", 0, centro=True)
    tabela.rows[0].cells[0].merge(tabela.rows[1].cells[0])
    _celula(tabela.rows[0].cells[0], "Atividades", 0, centro=True)

    inicio_ano = [1, 13]
    for indice, (rotulo, _) in enumerate(anos):
        primeira = inicio_ano[indice]
        tabela.rows[0].cells[primeira].merge(tabela.rows[0].cells[primeira + 11])
        _celula(tabela.rows[0].cells[primeira], rotulo, primeira, centro=True)
        for mes in range(12):
            _celula(
                tabela.rows[1].cells[primeira + mes],
                str(mes + 1),
                primeira + mes,
                centro=True,
                tamanho=8,
            )

    for r_idx, (nome, meses) in enumerate(atividades, start=2):
        _celula(tabela.rows[r_idx].cells[0], nome, 0, centro=False)
        presentes = set(meses)
        for indice, (_, inicio) in enumerate(anos):
            primeira = inicio_ano[indice]
            for mes in range(12):
                coluna = primeira + mes
                absoluto = inicio + mes
                _celula(tabela.rows[r_idx].cells[coluna], "", coluna, centro=True)
                if absoluto in presentes:
                    _pintar(tabela.rows[r_idx].cells[coluna])


def _grade_fixa(tabela):
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
    tbl_w.set(qn("w:w"), str(sum(_LARGURAS)))
    tbl_w.set(qn("w:type"), "dxa")
    grade = tbl.find(qn("w:tblGrid"))
    if grade is None:
        grade = OxmlElement("w:tblGrid")
        tbl_pr.addnext(grade)
    for filho in list(grade):
        grade.remove(filho)
    for largura in _LARGURAS:
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


def _celula(celula, texto, coluna, centro=False, tamanho=10):
    celula.width = Twips(_LARGURAS[coluna])
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
        p.runs[0].bold = False
    set_cell_border(celula, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})


def _pintar(celula):
    tc_pr = celula._tc.get_or_add_tcPr()
    sombreado = OxmlElement("w:shd")
    sombreado.set(qn("w:val"), "clear")
    sombreado.set(qn("w:color"), "auto")
    sombreado.set(qn("w:fill"), _CINZA_MES)
    tc_pr.append(sombreado)
