"""
Cronograma no modelo mensal da Resolução nº 009/2025.
Sem dados do projeto, as atividades do modelo ficam com os meses em branco.
"""

from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from core.xml_utils import set_cell_border
from core.campos import adicionar_bookmark
from ..formato import adicionar_lacuna, adicionar_paragrafo, adicionar_titulo
from ..legendas import BM_QUADRO_2, legenda_quadro_2


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
            [("Ano 1 (Mês 1 a 12)", 1), ("Ano 2 (Mês 13 a 24)", 13)],
        )
        _bloco(
            doc,
            legenda_quadro_2("doutorado", parte="conclusao"),
            None,
            atividades,
            [("Ano 3 (Mês 25 a 36)", 25), ("Ano 4 (Mês 37 a 48)", 37)],
        )
    else:
        _bloco(
            doc,
            legenda_quadro_2("mestrado"),
            BM_QUADRO_2,
            atividades,
            [("Ano 1 (Mês 1 a 12)", 1), ("Ano 2 (Mês 13 a 24)", 13)],
        )

    if not informado:
        adicionar_lacuna(doc, "[Meses de execução não informados no projeto.]")

    p_f = doc.add_paragraph()
    p_f.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_f.paragraph_format.space_before = Pt(2)
    p_f.paragraph_format.space_after = Pt(18)
    p_f.paragraph_format.line_spacing = 1.0
    r_f = p_f.add_run(f"Fonte: Elaborado pelo autor, {ano_referencia}.")
    r_f.font.name = "Times New Roman"
    r_f.font.size = Pt(10)


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


def _meses_na_janela(meses, inicio):
    locais = [str(mes - inicio + 1) for mes in meses if inicio <= mes <= inicio + 11]
    return " ".join(locais)


def _bloco(doc, legenda, bookmark, atividades, anos):
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_tit.paragraph_format.space_before = Pt(12)
    p_tit.paragraph_format.space_after = Pt(4)
    p_tit.paragraph_format.line_spacing = 1.0
    r_t = p_tit.add_run(legenda)
    r_t.bold = True
    r_t.font.name = "Times New Roman"
    r_t.font.size = Pt(12)
    if bookmark:
        adicionar_bookmark(p_tit, bookmark)

    larguras = [5.2, 5.4, 5.4]
    tabela = doc.add_table(rows=1 + len(atividades), cols=3)
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER

    cabecalhos = ["Atividades", anos[0][0], anos[1][0]]
    for idx, texto in enumerate(cabecalhos):
        _celula(tabela.rows[0].cells[idx], texto, larguras[idx], negrito=True, centro=idx > 0)

    for r_idx, (nome, meses) in enumerate(atividades, start=1):
        _celula(tabela.rows[r_idx].cells[0], nome, larguras[0], centro=False)
        _celula(tabela.rows[r_idx].cells[1], _meses_na_janela(meses, anos[0][1]), larguras[1], centro=True)
        _celula(tabela.rows[r_idx].cells[2], _meses_na_janela(meses, anos[1][1]), larguras[2], centro=True)


def _celula(celula, texto, largura, negrito=False, centro=False):
    celula.width = Cm(largura)
    celula.text = texto
    p = celula.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if centro else WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(1)
    if p.runs:
        p.runs[0].font.name = "Times New Roman"
        p.runs[0].font.size = Pt(10)
        p.runs[0].bold = negrito
    set_cell_border(celula, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})
