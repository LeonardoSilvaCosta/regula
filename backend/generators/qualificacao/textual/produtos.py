"""
Módulo granular para geração exclusiva da SEÇÃO 5 (PROPOSTA DE PRODUTO)
do Projeto de Qualificação conforme o Art. 1º, II, item 5 da Resolução nº 009/2025
e as normas da Resolução nº 007/2025-PPGSP/UFPA (Art. 7º e modelo das págs. 18 e 19).
"""

from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.ptt_schema import formatar_ficha_22_itens
from ..formato import adicionar_titulo, adicionar_titulo_produto
from ..legendas import titulo_produto


def build_produtos(doc, dados_projeto, numero=5):
    """
    Renderiza a Seção 5 (Proposta de Produto) em tópicos corridos numerados em romanos,
    com subtítulos específicos para cada produto e validação dos 22 itens obrigatórios.

    Parâmetros:
      - doc: Objeto Document do python-docx
      - dados_projeto: Dicionário contendo a chave 'ptts' (lista de dicionários dos produtos)
    """

    def add_sec_title(txt, bookmark=None):
        adicionar_titulo(doc, txt, bookmark=bookmark, primario=True)

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
    add_sec_title(f"{numero}. PROPOSTA DE PRODUTOS", "sec_produtos")
    add_body_p(
        "Em cumprimento à Resolução nº 007/2025-PPGSP e ao Art. 1º, II, item 5 da Resolução nº 009/2025, "
        "apresentam-se as propostas dos produtos técnicos e tecnológicos a serem desenvolvidos:"
    )

    ptts = dados_projeto.get("ptts", [])

    if ptts:
        for idx_p, ptt in enumerate(ptts, start=1):
            adicionar_titulo_produto(
                doc,
                titulo_produto(idx_p, ptt, numero),
                numero,
                bookmark=f"sec_prod_{idx_p}",
            )

            ficha = formatar_ficha_22_itens(ptt)
            for campo, valor in ficha:
                p_item = doc.add_paragraph()
                p_item.alignment = WD_ALIGN_PARAGRAPH.LEFT
                p_item.paragraph_format.left_indent = Cm(0)
                p_item.paragraph_format.first_line_indent = Cm(0)
                p_item.paragraph_format.line_spacing = 1.0
                p_item.paragraph_format.space_before = Pt(2)
                p_item.paragraph_format.space_after = Pt(2)

                if "Justificativa" in campo:
                    rotulo = f"{campo}\n"
                elif "Coautoria" in campo or "Co-autoria" in campo:
                    rotulo = f"{campo}:\n"
                else:
                    rotulo = f"{campo}: "
                r_c = p_item.add_run(rotulo)
                r_c.bold = False
                r_c.font.name = "Times New Roman"
                r_c.font.size = Pt(12)

                r_v = p_item.add_run(f"{valor}")
                r_v.bold = True
                r_v.font.name = "Times New Roman"
                r_v.font.size = Pt(12)

            p_esp = doc.add_paragraph()
            p_esp.paragraph_format.space_before = Pt(0)
            p_esp.paragraph_format.space_after = Pt(12)
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