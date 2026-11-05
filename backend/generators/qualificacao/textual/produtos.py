"""
Módulo granular para geração exclusiva da SEÇÃO 5 (PROPOSTA DE PRODUTO)
do Projeto de Qualificação conforme o Art. 1º, II, item 5 da Resolução nº 009/2025
e as normas da Resolução nº 007/2025-PPGSP/UFPA (Art. 7º e modelo das págs. 18 e 19).
"""

from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.campos import ancorar_paragrafo
from core.ptt_schema import formatar_ficha_22_itens
from ..formato import adicionar_titulo
from ..pre_textual.sumario import registrar_entrada

_ROTULOS_JUSTIFICATIVA = {
    "XIV. Justificativa do Impacto": "Justificativa do Impacto – até 50 palavras",
    "XVI. Justificativa da Inovação": "Justificativa da Inovação – até 50 palavras",
    "XVIII. Justificativa da Complexidade": "Justificativa da Complexidade – até 50 palavras",
}


def _titulo_produto_ficha(indice, ptt):
    ptt = ptt or {}
    subtipo = str(ptt.get("subtipo") or ptt.get("subtipo_producao") or "").strip()
    titulo = str(ptt.get("titulo") or "").strip()
    base = f"PRODUTO {indice}."
    if subtipo and titulo:
        return f"{base} {subtipo} – {titulo}"
    if subtipo:
        return f"{base} {subtipo}"
    if titulo:
        return f"{base} {titulo}"
    return base


def _run_times(run, negrito):
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = negrito


def build_produtos(doc, dados_projeto, numero=5):
    """
    Renderiza a Seção 5 (Proposta de Produto) em tópicos corridos numerados em romanos,
    com subtítulos específicos para cada produto e validação dos 22 itens obrigatórios.

    Parâmetros:
      - doc: Objeto Document do python-docx
      - dados_projeto: Dicionário contendo a chave 'ptts' (lista de dicionários dos produtos)
    """

    def add_sec_title(txt, bookmark=None, toc=None):
        paragrafo = adicionar_titulo(doc, txt, bookmark=bookmark, primario=True)
        if toc:
            registrar_entrada(doc, txt, 1, toc, paragrafo)
        return paragrafo

    def add_sub_title(txt, bookmark=None):
        adicionar_titulo(doc, txt, bookmark=bookmark, primario=False)

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
    # 5. PROPOSTA DE PRODUTOS
    # -------------------------------------------------------------------------
    add_sec_title(f"{numero}. PROPOSTA DE PRODUTOS", "sec_produtos", toc="_TOC_PRODUTOS")
    add_body_p(
        "Em cumprimento à Resolução nº 007/2025-PPGSP e ao Art. 1º, II, item 5 da Resolução nº 009/2025, "
        "apresentam-se as propostas dos produtos técnicos e tecnológicos a serem desenvolvidos:"
    )

    ptts = dados_projeto.get("ptts", [])

    if ptts:
        for idx_p, ptt in enumerate(ptts, start=1):
            if idx_p > 1:
                separador = doc.add_paragraph()
                separador.paragraph_format.space_before = Pt(0)
                separador.paragraph_format.space_after = Pt(18)
                separador.paragraph_format.line_spacing = 1.0

            cabecalho = _titulo_produto_ficha(idx_p, ptt)
            p_titulo = doc.add_paragraph()
            p_titulo.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p_titulo.paragraph_format.space_before = Pt(12)
            p_titulo.paragraph_format.space_after = Pt(6)
            p_titulo.paragraph_format.line_spacing = 1.0
            p_titulo.paragraph_format.first_line_indent = Pt(0)
            _run_times(p_titulo.add_run(cabecalho), True)
            ancorar_paragrafo(p_titulo, cabecalho, bookmark=f"sec_prod_{idx_p}")

            ficha = formatar_ficha_22_itens(ptt, dados_projeto)
            for campo, valor in ficha:
                rotulo_justificativa = _ROTULOS_JUSTIFICATIVA.get(campo)
                if rotulo_justificativa:
                    p_rotulo = doc.add_paragraph()
                    p_rotulo.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    p_rotulo.paragraph_format.space_before = Pt(0)
                    p_rotulo.paragraph_format.space_after = Pt(3)
                    p_rotulo.paragraph_format.line_spacing = 1.0
                    p_rotulo.paragraph_format.first_line_indent = Pt(0)
                    _run_times(p_rotulo.add_run(rotulo_justificativa), True)

                    p_texto = doc.add_paragraph()
                    p_texto.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    p_texto.paragraph_format.space_before = Pt(0)
                    p_texto.paragraph_format.space_after = Pt(6)
                    p_texto.paragraph_format.line_spacing = 1.5
                    p_texto.paragraph_format.first_line_indent = Cm(1.27)
                    _run_times(p_texto.add_run(str(valor)), False)
                    continue

                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(3)
                p.paragraph_format.line_spacing = 1.0
                p.paragraph_format.first_line_indent = Pt(0)

                run_label = p.add_run(campo + " ")
                _run_times(run_label, True)

                run_val = p.add_run(str(valor))
                _run_times(run_val, False)
    else:
        add_placeholder(
            "Conforme a Resolução nº 007/2025-PPGSP e o modelo das páginas 18 e 19 da Resolução nº 009/2025, "
            "apresente a proposta detalhada de cada produto técnico e tecnológico com os 22 itens canônicos "
            "(I. Autoria; II. Tipo; III. Subtipo; IV. Título; V. Ano; VI. Co-autoria e Categoria; "
            "VII. Área de concentração; VIII. Linha de pesquisa; IX. Projeto vinculado; X. Financiamento; "
            "XI. Financiador; XII. Demanda; XIII. Impacto; XIV. Justificativa do Impacto – até 50 palavras; "
            "XV. Inovação; XVI. Justificativa da Inovação – até 50 palavras; XVII. Complexidade; "
            "XVIII. Justificativa da Complexidade – até 50 palavras; XIX. Validação do Produto; "
            "XX. Modo de Divulgação; XXI. Abrangência ou Inserção Social; XXII. Público Usuário)."
        )