"""
Módulo granular para geração exclusiva da SEÇÃO 2 (OBJETIVOS)
do Projeto de Qualificação conforme o Art. 1º, II, item 2 da Resolução nº 009/2025-PPGSP/UFPA.
Subseções:
  2.1. OBJETIVO GERAL
  2.2. OBJETIVOS ESPECÍFICOS
"""

import re

from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.xml_utils import adicionar_bookmark
from ..formato import adicionar_titulo
from ..pre_textual.sumario import registrar_entrada

_ROMANOS = (
    "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
    "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx",
)
_RE_MARCADOR = re.compile(
    r"^\s*\(?\s*(?:i{1,3}|iv|vi{0,3}|ix|x|\d+)\s*[\).\]]\s*",
    re.IGNORECASE,
)


def build_objetivos(doc, dados_projeto):
    """
    Renderiza a Seção 2 (Objetivos) e suas subseções (2.1 Geral e 2.2 Específicos).

    Parâmetros:
      - doc: Objeto Document do python-docx
      - dados_projeto: Dicionário contendo:
          * 'objetivo_geral': String com o texto do objetivo geral
          * 'objetivos_especificos': Lista de strings com os objetivos específicos
    """

    def add_sec_title(txt, bookmark=None):
        return adicionar_titulo(doc, txt, bookmark=bookmark, primario=True)

    def add_sub_title(txt, bookmark=None):
        return adicionar_titulo(doc, txt, bookmark=bookmark, primario=False)

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

    def add_placeholder(dica_normativa):
        """Insere parágrafo destacado em itálico orientando o preenchimento."""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(2)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(f"[ORIENTAÇÃO DE PREENCHIMENTO: {dica_normativa}]")
        r.italic = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(11)
        r.font.color.rgb = RGBColor(115, 115, 115)

    # -------------------------------------------------------------------------
    # 2. OBJETIVOS (Título Primário)
    # -------------------------------------------------------------------------
    p_obj = add_sec_title("2. OBJETIVOS", "sec_2")
    adicionar_bookmark(p_obj, "_TOC_OBJETIVOS")
    registrar_entrada(doc, "2. OBJETIVOS", 1, "_TOC_OBJETIVOS")

    # -------------------------------------------------------------------------
    # 2.1. OBJETIVO GERAL
    # -------------------------------------------------------------------------
    p_obj_geral = add_sub_title("2.1. OBJETIVO GERAL", "sec_2_1")
    adicionar_bookmark(p_obj_geral, "_TOC_OBJETIVO_GERAL")
    registrar_entrada(doc, "2.1. OBJETIVO GERAL", 2, "_TOC_OBJETIVO_GERAL")
    objetivo_geral = dados_projeto.get("objetivo_geral", "")
    if objetivo_geral and str(objetivo_geral).strip():
        add_body_p(str(objetivo_geral).strip())
    else:
        add_placeholder(
            "Conforme a Resolução nº 009/2025 (Art. 1º, II, 2.i), o Objetivo Geral deve sintetizar "
            "claramente o propósito central da pesquisa, iniciando obrigatoriamente com verbo de abrangência ampla "
            "no infinitivo (ex.: Desenvolver, Avaliar, Analisar, Caracterizar), respondendo ao que se vai buscar com o projeto."
        )

    # -------------------------------------------------------------------------
    # 2.2. OBJETIVOS ESPECÍFICOS
    # -------------------------------------------------------------------------
    p_obj_esp = add_sub_title("2.2. OBJETIVOS ESPECÍFICOS", "sec_2_2")
    adicionar_bookmark(p_obj_esp, "_TOC_OBJETIVOS_ESPECIFICOS")
    registrar_entrada(doc, "2.2. OBJETIVOS ESPECÍFICOS", 2, "_TOC_OBJETIVOS_ESPECIFICOS")
    objetivos_especificos = _itens_numerados(dados_projeto.get("objetivos_especificos", []))
    if objetivos_especificos:
        for indice, oe in enumerate(objetivos_especificos, start=1):
            _item_numerado(doc, indice, oe)
    else:
        add_placeholder(
            "Conforme a Resolução nº 009/2025 (Art. 1º, II, 2.ii e item 1), liste os objetivos específicos "
            "operacionais que desdobram a pesquisa. Regra obrigatória do PPGSP: Cada objetivo específico DEVE iniciar "
            "obrigatoriamente com um verbo diferente no infinitivo (ex.: Identificar, Mapear, Comparar, Estruturar, "
            "Conceber, Auditar, Propor), articulando as etapas metodológicas aos produtos e artigos previstos."
        )


def _romano(indice):
    if 1 <= indice <= len(_ROMANOS):
        return _ROMANOS[indice - 1]
    return str(indice)


def _itens_numerados(objetivos):
    itens = []
    for item in objetivos or []:
        texto = _RE_MARCADOR.sub("", str(item or "").strip()).strip()
        if texto:
            itens.append(texto)
    return itens


def _item_numerado(doc, indice, texto):
    """Item da lista (i), (ii), (iii), alinhado ao recuo do corpo."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.paragraph_format.left_indent = Cm(1.27)
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run(f"({_romano(indice)}) {texto}")
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)