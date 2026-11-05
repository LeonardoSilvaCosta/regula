"""
Módulo granular para geração exclusiva da SEÇÃO 4 (METODOLOGIA / MÉTODO)
do Projeto de Qualificação conforme o Art. 1º, II, item 4 da Resolução nº 009/2025-PPGSP/UFPA.
Suporta tanto Pesquisas de Campo/Empíricas (4.1) quanto Pesquisas Documentais/Bibliográficas (4.2).
"""

from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from ..estrutura import eh_documental
from ..formato import adicionar_titulo
from ..pre_textual.sumario import registrar_entrada
from ..legendas import BM_TABELA_1, BM_TABELA_2
from ...common.tabelas import inserir_tabela


def build_metodologia(doc, dados_projeto, numero=4):
    """
    Renderiza a Seção 4 (Metodologia), adaptando as subseções conforme o desenho da pesquisa
    (Campo/Empírica vs. Documental/Bibliográfica) e inserindo tabelas amostrais se fornecidas.

    Parâmetros:
      - doc: Objeto Document do python-docx
      - dados_projeto: Dicionário contendo as chaves metodológicas do projeto
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
    # 4. METODOLOGIA (Título Primário)
    # -------------------------------------------------------------------------
    add_sec_title(f"{numero}. METODOLOGIA", "sec_metodologia", toc="_TOC_METODOLOGIA")

    documental = eh_documental(dados_projeto)

    # -------------------------------------------------------------------------
    # 4.1. NATUREZA DA PESQUISA
    # -------------------------------------------------------------------------
    add_sub_title(f"{numero}.1. NATUREZA DA PESQUISA", "sec_met_1")
    natureza = dados_projeto.get("metodologia_natureza", [])
    if natureza:
        if isinstance(natureza, str):
            add_body_p(natureza)
        elif isinstance(natureza, list):
            for par in natureza:
                add_body_p(par)
    else:
        add_placeholder(
            "Conforme a Resolução nº 009/2025 (Art. 1º, II, 4), caracterize e conceitue o tipo de pesquisa abordado: "
            "quanto à finalidade (básica ou aplicada), quanto à abordagem do problema (quantitativa, qualitativa ou mista), "
            "e quanto aos objetivos (exploratória, descritiva ou explicativa)."
        )

    # -------------------------------------------------------------------------
    # 4.2. LÓCUS
    # -------------------------------------------------------------------------
    locus = dados_projeto.get("metodologia_locus", [])
    if locus or not documental:
        add_sub_title(f"{numero}.2. LÓCUS", "sec_met_2")
        if locus:
            if isinstance(locus, str):
                add_body_p(locus)
            elif isinstance(locus, list):
                for par in locus:
                    add_body_p(par)
        else:
            add_placeholder(
                "Conforme a Resolução nº 009/2025 (Art. 1º, II, 4), descreva detalhadamente o contexto, instituição, "
                "batalhão, diretoria, município ou território geográfico onde a investigação será realizada. "
                "(Nota: Este tópico pode ser dispensado caso o estudo seja estritamente bibliográfico)."
            )

    # -------------------------------------------------------------------------
    # 4.3. PARTICIPANTES (Empírica) OU FONTES DE DADOS (Documental)
    # -------------------------------------------------------------------------
    if documental:
        add_sub_title(f"{numero}.3. FONTES DE DADOS", "sec_met_3f")
        fontes = dados_projeto.get("metodologia_fontes", [])
        if fontes:
            if isinstance(fontes, str):
                add_body_p(fontes)
            elif isinstance(fontes, list):
                for par in fontes:
                    add_body_p(par)
        else:
            add_placeholder(
                "Conforme a Resolução nº 009/2025 (Art. 1º, II, 4.2.iii), indique: "
                "(a) As formas de acesso ao acervo ou bases de dados; "
                "(b) O tipo da fonte (primária ou secundária); "
                "(c) Os critérios de inclusão e exclusão adotados para composição do corpus documental."
            )
    else:
        add_sub_title(f"{numero}.3. PARTICIPANTES E COORTE POPULACIONAL", "sec_met_3p")
        participantes = dados_projeto.get("metodologia_participantes", [])
        if participantes:
            if isinstance(participantes, str):
                add_body_p(participantes)
            elif isinstance(participantes, list):
                for par in participantes:
                    add_body_p(par)
        else:
            add_placeholder(
                "Conforme a Resolução nº 009/2025 (Art. 1º, II, 4.1.iii), apresente a caracterização dos participantes, "
                "a descrição dos processos de amostragem probabilística ou não probabilística, o dimensionamento da população (N) "
                "e o cálculo do tamanho amostral representativo (n)."
            )

        # Inserção da Tabela 1 (Amostral), se disponível
        t1_dados = dados_projeto.get("tabela_1", {}).get("linhas", [])
        if t1_dados:
            _inserir_tabela_amostral(doc, dados_projeto["tabela_1"])

        # Inserção da Tabela 2 (Tokens / Tukey), se disponível
        t2_dados = dados_projeto.get("tabela_2", {}).get("linhas", [])
        if t2_dados:
            add_body_p(
                "Para mitigar o viés de comprimento de sequência em modelos Transformer (BERTimbau), realizou-se auditoria "
                "estatística da distribuição de tokens através do método clássico de Tukey, conforme sistematizado na Tabela 2:"
            )
            _inserir_tabela_tokens(doc, dados_projeto["tabela_2"])

    # -------------------------------------------------------------------------
    # 4.4. FONTES DE DADOS (empírica com acervo informacional explícito)
    # -------------------------------------------------------------------------
    sub = 4
    if not documental:
        fontes_empiricas = dados_projeto.get("metodologia_fontes", [])
        if fontes_empiricas:
            add_sub_title(f"{numero}.{sub}. FONTES DE DADOS", "sec_met_3f_emp")
            if isinstance(fontes_empiricas, str):
                add_body_p(fontes_empiricas)
            else:
                for par in fontes_empiricas:
                    add_body_p(par)
            sub += 1

    # -------------------------------------------------------------------------
    # PROCEDIMENTOS DE COLETA
    # -------------------------------------------------------------------------
    add_sub_title(f"{numero}.{sub}. PROCEDIMENTOS DE COLETA", "sec_met_4")
    coleta = dados_projeto.get("metodologia_coleta", [])
    if coleta:
        if isinstance(coleta, str):
            add_body_p(coleta)
        elif isinstance(coleta, list):
            for par in coleta:
                add_body_p(par)
    else:
        if documental:
            add_placeholder(
                "Conforme a Resolução nº 009/2025 (Art. 1º, II, 4.2.iv), apresente as variáveis e categorias que serão "
                "extraídas do corpus textual, detalhando a estratégia de busca booleana, termos de indexação e fichamento dos documentos."
            )
        else:
            add_placeholder(
                "Conforme a Resolução nº 009/2025 (Art. 1º, II, 4.1.iv), indique de forma detalhada e clara todas as etapas "
                "da coleta de dados e apresente os instrumentos que serão utilizados (entrevistas, formulários, inventários, escalas). "
                "Recomenda-se anexar a íntegra destes instrumentos para avaliação da banca examinadora."
            )

    # -------------------------------------------------------------------------
    # 4.5. PROCEDIMENTOS ÉTICOS (Obrigatório em Pesquisas com Seres Humanos)
    # -------------------------------------------------------------------------
    sub += 1
    if not documental or dados_projeto.get("metodologia_etica"):
        add_sub_title(f"{numero}.{sub}. PROCEDIMENTOS ÉTICOS", "sec_met_5")
        etica = dados_projeto.get("metodologia_etica", [])
        if etica:
            if isinstance(etica, str):
                add_body_p(etica)
            elif isinstance(etica, list):
                for par in etica:
                    add_body_p(par)
        else:
            add_placeholder(
                "Conforme a Resolução nº 009/2025 (Art. 1º, II, 4.1.v), descreva os cuidados éticos adotados, "
                "a menção formal ao Termo de Consentimento Livre e Esclarecido - TCLE (a ser inserido em anexo), "
                "o enquadramento às Resoluções CNS nº 466/2012 e nº 510/2016, à LGPD (Lei nº 13.709/2018) "
                "e a comprovação de submissão ao Comitê de Ética em Pesquisa (CEP/UFPA)."
            )

    # -------------------------------------------------------------------------
    # 4.6. ANÁLISE DE DADOS
    # -------------------------------------------------------------------------
    sub += 1
    add_sub_title(f"{numero}.{sub}. ANÁLISE DE DADOS", "sec_met_6")
    analise = dados_projeto.get("metodologia_analise", [])
    if analise:
        if isinstance(analise, str):
            add_body_p(analise)
        elif isinstance(analise, list):
            for par in analise:
                add_body_p(par)
    else:
        add_placeholder(
            "Conforme a Resolução nº 009/2025 (Art. 1º, II, 4.1.vi e 4.2.v), explicite conceitual e operacionalmente "
            "as técnicas adotadas para tratamento dos dados (estatística descritiva/inferencial, testes de hipóteses, "
            "modelagem preditiva de machine learning, PLN, análise de conteúdo ou análise de discurso)."
        )


def _inserir_tabela_amostral(doc, dados):
    colunas = [
        "Macroestrato Metodológico",
        "População Real (Nh)",
        "Proporção (%)",
        "Amostra Proporcional (nh)",
        "Amostra Otimizada Balanceada (nh)",
        "Papel na Escala EVRP / Spans",
    ]
    alinhamentos = [
        WD_ALIGN_PARAGRAPH.LEFT,
        WD_ALIGN_PARAGRAPH.RIGHT,
        WD_ALIGN_PARAGRAPH.RIGHT,
        WD_ALIGN_PARAGRAPH.RIGHT,
        WD_ALIGN_PARAGRAPH.RIGHT,
        WD_ALIGN_PARAGRAPH.LEFT,
    ]
    inserir_tabela(
        doc,
        numero=1,
        titulo="Distribuição Populacional da Coorte Viva e Alocação Amostral (n = 360)",
        colunas=colunas,
        linhas=dados.get("linhas", []),
        fonte="Dados da pesquisa extraídos do banco analítico ciap_pesquisa (2026).",
        alinhamentos=alinhamentos,
        bookmark=BM_TABELA_1,
    )


def _inserir_tabela_tokens(doc, dados):
    colunas = [
        "Macroestrato",
        "Total (N)",
        "Mín",
        "P10",
        "Q1",
        "Mediana",
        "Q3",
        "P90",
        "Máx",
        "Limiar Tukey",
        "Outliers (%)",
    ]
    alinhamentos = [WD_ALIGN_PARAGRAPH.LEFT] + [WD_ALIGN_PARAGRAPH.RIGHT] * (len(colunas) - 1)
    inserir_tabela(
        doc,
        numero=2,
        titulo="Métricas de Dispersão de Tokens por Prontuário e Limiares de Outliers (Método de Tukey)",
        colunas=colunas,
        linhas=dados.get("linhas", []),
        fonte="Dados da pesquisa extraídos do banco analítico ciap_pesquisa (2026).",
        alinhamentos=alinhamentos,
        bookmark=BM_TABELA_2,
    )