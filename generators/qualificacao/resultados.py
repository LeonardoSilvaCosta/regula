"""
Módulo de Resultados Preliminares e Pós-Textual conforme a página 20 da Resolução nº 009/2025-PPGSP/UFPA.
Renderiza a estrutura formal do primeiro artigo (minuta ou árvore de 'Em construção'),
os blocos indicativos de Apêndice e Anexo, e a lista de Referências ABNT.
"""

from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


def build_resultados_e_pos_textual(doc, dados_resultados, referencias):
    """
    Renderiza a Seção 7 (Resultados Preliminares) e a Parte III (Pós-Textual).
    """
    def add_sec_title(txt):
        """Título em maiúsculas negrito com espaçamento padrão."""
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(18)
        p.paragraph_format.space_after = Pt(12)
        r = p.add_run(txt)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    def add_sub_title(txt):
        """Subtítulo de segundo nível."""
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(txt)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    def add_body_p(txt):
        """Parágrafo regular justificado com recuo de 1,27 cm e espaçamento 1,5."""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(txt)
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    def add_construcao(rotulo=""):
        """Insere o texto em itálico '[Em construção]' conforme o modelo oficial da página 20."""
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.line_spacing = 1.5
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        if rotulo:
            r1 = p.add_run(f"{rotulo}: ")
            r1.bold = True
            r1.font.name = "Times New Roman"
            r1.font.size = Pt(12)
        r2 = p.add_run("Em construção")
        r2.italic = True
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(12)
        r2.font.color.rgb = RGBColor(115, 115, 115)

    # -------------------------------------------------------------------------
    # 7. RESULTADOS PRELIMINARES (pág. 20 da Resolução 009/2025)
    # -------------------------------------------------------------------------
    add_sec_title("7. RESULTADOS PRELIMINARES")

    art = dados_resultados.get("artigo_1", {})
    tit_art = art.get("titulo", "7.1. Produto Bibliográfico I - Artigo 1 –")
    add_sub_title(tit_art)

    # Autores do artigo alinhados à direita (conforme modelo da pág. 20)
    p_aut = doc.add_paragraph()
    p_aut.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_aut.paragraph_format.space_before = Pt(0)
    p_aut.paragraph_format.space_after = Pt(12)
    autores = art.get("autores", "Autor 1\nAutor 2\nAutor 3")
    r_a = p_aut.add_run(autores)
    r_a.font.name = "Times New Roman"
    r_a.font.size = Pt(12)

    # Bloco Resumo
    p_res = doc.add_paragraph()
    p_res.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_res.paragraph_format.space_before = Pt(6)
    p_res.paragraph_format.space_after = Pt(6)
    r_res = p_res.add_run("Resumo")
    r_res.bold = True
    r_res.font.name = "Times New Roman"
    r_res.font.size = Pt(12)

    topicos_resumo = art.get("resumo_topicos", [])
    if topicos_resumo:
        for rotulo, texto in topicos_resumo:
            p_t = doc.add_paragraph()
            p_t.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_t.paragraph_format.first_line_indent = Cm(0)
            p_t.paragraph_format.line_spacing = 1.0
            p_t.paragraph_format.space_before = Pt(0)
            p_t.paragraph_format.space_after = Pt(3)
            r1 = p_t.add_run(f"{rotulo}: ")
            r1.bold = True
            r1.font.name = "Times New Roman"
            r1.font.size = Pt(12)
            r2 = p_t.add_run(texto)
            r2.font.name = "Times New Roman"
            r2.font.size = Pt(12)
    else:
        add_construcao("Importância do Estudo")
        add_construcao("Objetivo")
        add_construcao("Materiais e Métodos")
        add_construcao("Resultados e Discussões")
        add_construcao("Conclusões")
        add_construcao("Palavras-chave")

    # Subseções estruturais do Artigo 1 (pág. 20 do modelo)
    add_sub_title("INTRODUÇÃO")
    if art.get("introducao"):
        add_body_p(art["introducao"])
    else:
        add_construcao()

    add_sub_title("MATERIAL E MÉTODO")
    subsecoes_metodo = [
        "Natureza da Pesquisa",
        "Lócus",
        "Fonte de Dados",
        "Procedimento de Coleta",
        "Análise dos Dados"
    ]
    for sub in subsecoes_metodo:
        p_s = doc.add_paragraph()
        p_s.paragraph_format.space_before = Pt(4)
        p_s.paragraph_format.space_after = Pt(2)
        r = p_s.add_run(sub)
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)
        add_construcao()

    add_sub_title("RESULTADOS E DISCUSSÕES")
    if art.get("resultados_preliminares"):
        add_body_p(art["resultados_preliminares"])
    else:
        add_construcao()

    add_sub_title("CONSIDERAÇÕES FINAIS")
    add_construcao()

    add_sub_title("REFERÊNCIAS")
    add_construcao()

    # -------------------------------------------------------------------------
    # APÊNDICE E ANEXO INDICATIVOS (conforme pág. 20 do modelo da Resolução)
    # -------------------------------------------------------------------------
    p_ap_tit = doc.add_paragraph()
    p_ap_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ap_tit.paragraph_format.space_before = Pt(18)
    p_ap_tit.paragraph_format.space_after = Pt(4)
    r_ap = p_ap_tit.add_run("APÊNDICE")
    r_ap.bold = True
    r_ap.font.name = "Times New Roman"
    r_ap.font.size = Pt(12)

    p_ap_desc = doc.add_paragraph()
    p_ap_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ap_desc.paragraph_format.space_before = Pt(0)
    p_ap_desc.paragraph_format.space_after = Pt(12)
    r_apd = p_ap_desc.add_run("Apêndice 1: Plano Amostral – Pesquisa Metodológica")
    r_apd.font.name = "Times New Roman"
    r_apd.font.size = Pt(12)

    p_an_tit = doc.add_paragraph()
    p_an_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_an_tit.paragraph_format.space_before = Pt(12)
    p_an_tit.paragraph_format.space_after = Pt(4)
    r_an = p_an_tit.add_run("ANEXO")
    r_an.bold = True
    r_an.font.name = "Times New Roman"
    r_an.font.size = Pt(12)

    p_an_desc = doc.add_paragraph()
    p_an_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_an_desc.paragraph_format.space_before = Pt(0)
    p_an_desc.paragraph_format.space_after = Pt(18)
    r_and = p_an_desc.add_run("Anexo 1: Instrumento de Coleta de Dados / Termo Institucional")
    r_and.font.name = "Times New Roman"
    r_and.font.size = Pt(12)

    # -------------------------------------------------------------------------
    # PARTE III: PÓS-TEXTUAL (Referências Gerais do Trabalho - ABNT NBR 6023)
    # -------------------------------------------------------------------------
    doc.add_page_break()
    p_rt = doc.add_paragraph()
    p_rt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rt.paragraph_format.space_before = Pt(0)
    p_rt.paragraph_format.space_after = Pt(18)
    r_rt = p_rt.add_run("REFERÊNCIAS\n")
    r_rt.bold = True
    r_rt.font.name = "Times New Roman"
    r_rt.font.size = Pt(12)

    if referencias:
        for ref in referencias:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Cm(0)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            r = p.add_run(ref)
            r.font.name = "Times New Roman"
            r.font.size = Pt(12)
    else:
        p_aviso = doc.add_paragraph()
        p_aviso.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_aviso.paragraph_format.first_line_indent = Cm(0)
        p_aviso.paragraph_format.line_spacing = 1.5
        r_av = p_aviso.add_run(
            "[ORIENTAÇÃO DE PREENCHIMENTO: Apresente aqui a relação em ordem alfabética de todas as obras citadas "
            "no corpo do relatório de qualificação, em espaçamento simples entre linhas e com espaçamento de 6 pt "
            "entre cada referência, conforme a norma ABNT NBR 6023 e o Art. 1º, III da Resolução nº 009/2025.]"
        )
        r_av.italic = True
        r_av.font.name = "Times New Roman"
        r_av.font.size = Pt(11)
        r_av.font.color.rgb = RGBColor(115, 115, 115)