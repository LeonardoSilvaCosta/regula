"""
Módulo granular para geração exclusiva da APRESENTAÇÃO
conforme o Art. 1º, II, item 1 e modelo das páginas 3 a 5 da Resolução nº 009/2025-PPGSP/UFPA.
"""

from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

# Importação da função granular dedicada à construção do Quadro 1
from .quadro_apresentacao import build_quadro_apresentacao


def build_apresentacao(doc, dados_apresentacao, metadata):
    """
    Renderiza a seção APRESENTAÇÃO e encerra invocando a função granular do Quadro 1.

    Parâmetros:
      - doc: Objeto Document do python-docx
      - dados_apresentacao: Dicionário contendo:
          * 'texto_percurso': Lista de parágrafos reflexivos sobre trajetória profissional/acadêmica
          * 'quadro_1': Lista de itens/linhas para montagem estruturada do Quadro 1
      - metadata: Dicionário contendo metadados gerais ('titulo', 'titulo_curto', 'nivel', 'ano', etc.)
    """
    # -------------------------------------------------------------
    # 1. Título da Seção (Centralizado, Maiúsculas, Negrito, Times 12)
    # -------------------------------------------------------------
    p_header = doc.add_paragraph()
    p_header.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_header.paragraph_format.space_before = Pt(0)
    p_header.paragraph_format.space_after = Pt(18)

    r_hdr = p_header.add_run("APRESENTAÇÃO\n")
    r_hdr.bold = True
    r_hdr.font.name = "Times New Roman"
    r_hdr.font.size = Pt(12)

    # -------------------------------------------------------------
    # 2. Texto Pessoal: Percurso Profissional e Acadêmico
    # -------------------------------------------------------------
    texto_percurso = dados_apresentacao.get("texto_percurso", [])

    if texto_percurso:
        for par in texto_percurso:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Cm(1.27)
            p.paragraph_format.line_spacing = 1.5
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)

            r_p = p.add_run(par)
            r_p.font.name = "Times New Roman"
            r_p.font.size = Pt(12)
    else:
        # Placeholder pedagógico estruturado com os itens obrigatórios do Art. 1º, II, 1
        p_aviso = doc.add_paragraph()
        p_aviso.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_aviso.paragraph_format.first_line_indent = Cm(1.27)
        p_aviso.paragraph_format.line_spacing = 1.5
        p_aviso.paragraph_format.space_before = Pt(2)
        p_aviso.paragraph_format.space_after = Pt(6)

        r_aviso = p_aviso.add_run(
            "[ORIENTAÇÃO DE PREENCHIMENTO: A Apresentação é obrigatória segundo o Art. 1º, II, item 1 da Resolução nº 009/2025. "
            "Elabore um texto em perspetiva pessoal abordando: "
            "(i) Seu percurso profissional vinculado ao objeto de pesquisa e atuação institucional; "
            "(ii) Seu percurso acadêmico no curso (disciplinas concluídas, grupos de pesquisa, seminários, publicações e resumo do currículo Lattes). "
            "Ao final deste texto reflexivo, apresente a síntese da arquitetura da pesquisa através do Quadro 1.]"
        )
        r_aviso.italic = True
        r_aviso.font.name = "Times New Roman"
        r_aviso.font.size = Pt(11)
        r_aviso.font.color.rgb = RGBColor(115, 115, 115)

    # -------------------------------------------------------------
    # 3. Construção do Quadro 1 Oficial
    # -------------------------------------------------------------
    build_quadro_apresentacao(doc, dados_apresentacao.get("quadro_1", []), metadata)