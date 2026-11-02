"""
Módulo granular para geração exclusiva da SEÇÃO 1 (CONSIDERAÇÕES GERAIS)
do Projeto de Qualificação conforme o Art. 1º, II, item 2 da Resolução nº 009/2025-PPGSP/UFPA.
Subseções:
  1.1. INTRODUÇÃO
  1.2. JUSTIFICATIVA
  1.3. PROBLEMA DE PESQUISA
  1.4. REVISÃO DA LITERATURA / REFERENCIAL TEÓRICO
"""

from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from ..formato import adicionar_titulo


def build_consideracoes_gerais(doc, dados_secao):
    """
    Renderiza a Seção 1 (Considerações Gerais) e suas 4 subseções obrigatórias.

    Parâmetros:
      - doc: Objeto Document do python-docx
      - dados_secao: Dicionário contendo as chaves:
          * 'introducao': Lista de parágrafos da introdução
          * 'justificativa': Lista de parágrafos da justificativa
          * 'problema': Lista de parágrafos ou string da pergunta problema
          * 'revisao': Lista de parágrafos da revisão / referencial teórico
    """

    def add_sec_title(txt, bookmark=None):
        adicionar_titulo(doc, txt, bookmark=bookmark, primario=True)

    def add_sub_title(txt, bookmark=None):
        adicionar_titulo(doc, txt, bookmark=bookmark, primario=False)

    def add_body_p(txt):
        """Parágrafo textual padrão: Times 12, recuo 1,27 cm, entrelinhas 1,5, espaçamento 0pt."""
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
        """Bloco destacado para preenchimento de seções pendentes."""
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
    # 1. CONSIDERAÇÕES GERAIS (Título Primário)
    # -------------------------------------------------------------------------
    add_sec_title("1. CONSIDERAÇÕES GERAIS", "sec_1")

    # -------------------------------------------------------------------------
    # 1.1. INTRODUÇÃO
    # -------------------------------------------------------------------------
    add_sub_title("1.1. INTRODUÇÃO", "sec_1_1")
    introducao_paragrafos = dados_secao.get("introducao", [])
    if introducao_paragrafos:
        for par in introducao_paragrafos:
            add_body_p(par)
    else:
        add_placeholder(
            "Conforme a Resolução nº 009/2025 (Art. 1º, II, 1.i), apresente a contextualização acerca do objeto investigado, "
            "podendo envolver delimitações conceituais e históricas para aproximação do leitor à temática. "
            "Inclua argumentações a partir de problematizações com dados concretos que caracterizem o objeto em foco e, "
            "caso pertinente, informações que caracterizem o lócus da pesquisa."
        )

    # -------------------------------------------------------------------------
    # 1.2. JUSTIFICATIVA
    # -------------------------------------------------------------------------
    add_sub_title("1.2. JUSTIFICATIVA", "sec_1_2")
    justificativa_paragrafos = dados_secao.get("justificativa", [])
    if justificativa_paragrafos:
        for par in justificativa_paragrafos:
            add_body_p(par)
    else:
        add_placeholder(
            "Conforme a Resolução nº 009/2025 (Art. 1º, II, 1.ii), indique de forma clara as razões teóricas ou práticas "
            "que justifiquem a realização da pesquisa ou o tema proposto. No caso de pesquisa científica ou acadêmica, "
            "deve indicar a relevância e as contribuições para a sociedade, abrangendo obrigatoriamente: "
            "(a) Relevância Científica ou Acadêmica (contribuições para o campo de estudo); e "
            "(b) Relevância Prática/Institucional (contribuições no âmbito social, categorias de participantes e instituições envolvidas)."
        )

    # -------------------------------------------------------------------------
    # 1.3. PROBLEMA DE PESQUISA
    # -------------------------------------------------------------------------
    add_sub_title("1.3. PROBLEMA DE PESQUISA", "sec_1_3")
    problema_dados = dados_secao.get("problema", [])
    if problema_dados:
        if isinstance(problema_dados, str):
            add_body_p(problema_dados)
        elif isinstance(problema_dados, list):
            for par in problema_dados:
                add_body_p(par)
    else:
        add_placeholder(
            "Conforme a Resolução nº 009/2025 (Art. 1º, II, 1.iii), a apresentação do problema de pesquisa "
            "deve ser obrigatoriamente em forma de uma pergunta, precisando estar estritamente articulada às discussões "
            "apresentadas na introdução e na justificativa."
        )

    # -------------------------------------------------------------------------
    # 1.4. REVISÃO DA LITERATURA / REFERENCIAL TEÓRICO
    # -------------------------------------------------------------------------
    add_sub_title("1.4. REVISÃO DA LITERATURA / REFERENCIAL TEÓRICO", "sec_1_4")
    revisao_paragrafos = dados_secao.get("revisao", [])
    if revisao_paragrafos:
        for par in revisao_paragrafos:
            add_body_p(par)
    else:
        add_placeholder(
            "Conforme a Resolução nº 009/2025 (Art. 1º, II, 1.iv), apresente o estado da arte a partir de fontes bibliográficas e/ou documentais atuais "
            "(preferencialmente dos últimos 10 anos), contemplando o panorama de estudos científicos no escopo do trabalho e o referencial teórico conceitual adotado.\n"
            "Diretrizes e vedações obrigatórias da resolução:\n"
            "(i) Plágio é inaceitável (citar todas as ideias e dados);\n"
            "(ii) Revisão clara, coerente e crítica;\n"
            "(iii) Relacionar a literatura ao problema e objetivos da pesquisa;\n"
            "(iv) O uso de notas de rodapé deve ser obrigatoriamente evitado;\n"
            "(v) Citações diretas longas (>3 linhas) devem ser obrigatoriamente evitadas, priorizando síntese interpretativa;\n"
            "(vi) A expressão 'apud' deve ser obrigatoriamente evitada, priorizando a citação direta da fonte original."
        )