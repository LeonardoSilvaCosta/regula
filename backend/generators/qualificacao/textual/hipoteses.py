"""
Módulo granular para geração exclusiva da SEÇÃO 3 (HIPÓTESES OU QUESTÕES NORTEADORAS)
do Projeto de Qualificação conforme o Art. 1º, II, item 3 da Resolução nº 009/2025-PPGSP/UFPA.
"""

from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from ..formato import adicionar_titulo


def build_hipoteses(doc, dados_projeto, numero=3):
    """
    Renderiza a Seção 3 (Hipóteses ou Questões Norteadoras).

    Parâmetros:
      - doc: Objeto Document do python-docx
      - dados_projeto: Dicionário contendo a chave 'hipotese' (string ou lista de strings/parágrafos)
    """

    def add_sec_title(txt, bookmark=None):
        adicionar_titulo(doc, txt, bookmark=bookmark, primario=True)

    def add_body_p(txt):
        """Parágrafo regular: Times 12, recuo 1,27 cm, entrelinhas 1,5, espaçamento 0pt."""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(txt)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    hipotese_dados = dados_projeto.get("hipotese", [])
    if isinstance(hipotese_dados, str):
        paragrafos = [hipotese_dados.strip()] if hipotese_dados.strip() else []
    elif isinstance(hipotese_dados, list):
        paragrafos = [str(par).strip() for par in hipotese_dados if str(par).strip()]
    else:
        paragrafos = []
    if not paragrafos:
        return

    add_sec_title(
        f"{numero}. HIPÓTESES OU QUESTÕES NORTEADORAS",
        bookmark="sec_hipoteses",
    )
    for par in paragrafos:
        add_body_p(par)