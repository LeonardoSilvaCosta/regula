"""
Módulo granular para construção exclusiva do QUADRO 1 da Apresentação
conforme o modelo oficial da Resolução nº 009/2025-PPGSP/UFPA (página 5).
"""

from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from core.xml_utils import set_cell_border
from ..formato import escrever_fonte, escrever_legenda


def build_quadro_apresentacao(doc, dados_quadro, metadata):
    is_doutorado = metadata.get("nivel", "mestrado").strip().lower() in ["doutorado", "tese"]
    tipo_trabalho = "tese" if is_doutorado else "dissertação"
    titulo_curto = metadata.get("titulo_curto", metadata.get("titulo", "Título da Pesquisa"))
    obj_geral = metadata.get("objetivo_geral", "Desenvolver esteira computacional de suporte assistencial.")

    # Título do Quadro
    p_titulo = doc.add_paragraph()
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_titulo.paragraph_format.space_before = Pt(18)
    p_titulo.paragraph_format.space_after = Pt(4)
    p_titulo.paragraph_format.line_spacing = 1.0

    escrever_legenda(
        p_titulo,
        f'Quadro 1. Estrutura dos principais itens da {tipo_trabalho} “{titulo_curto}”.',
    )

    colunas = ["Título", "Objetivo Geral", "Objetivos Específicos", "Tipo de Produto", "Tipo de Estudo", "Fontes", "Status"]
    larguras_cm = [2.2, 2.5, 3.8, 3.0, 2.2, 1.4, 1.5]

    itens = dados_quadro if dados_quadro else []
    total_linhas = len(itens)

    tabela = doc.add_table(rows=total_linhas + 1, cols=len(colunas))
    tabela.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Cabeçalho
    for idx_c, nome_c in enumerate(colunas):
        cell_hdr = tabela.rows[0].cells[idx_c]
        cell_hdr.width = Cm(larguras_cm[idx_c])
        cell_hdr.text = nome_c
        cell_hdr.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p_hdr = cell_hdr.paragraphs[0]
        p_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_hdr.paragraph_format.line_spacing = 1.0
        p_hdr.paragraph_format.space_before = Pt(3)
        p_hdr.paragraph_format.space_after = Pt(3)
        r_hdr = p_hdr.runs[0]
        r_hdr.font.bold = True
        r_hdr.font.name = "Times New Roman"
        r_hdr.font.size = Pt(10)
        set_cell_border(cell_hdr, top={'sz': 4}, bottom={'sz': 4}, left={'sz': 4}, right={'sz': 4})

    # Preenchimento
    for r_idx, linha in enumerate(itens, start=1):
        row_cells = tabela.rows[r_idx].cells
        for c_idx, valor in enumerate(linha):
            cell = row_cells[c_idx]
            cell.width = Cm(larguras_cm[c_idx])
            cell.text = str(valor)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p_c = cell.paragraphs[0]
            p_c.paragraph_format.line_spacing = 1.0
            p_c.paragraph_format.space_before = Pt(3)
            p_c.paragraph_format.space_after = Pt(3)

            if c_idx in [0, 1]:
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif c_idx in [2, 3]:
                p_c.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER

            if p_c.runs:
                p_c.runs[0].font.name = "Times New Roman"
                p_c.runs[0].font.size = Pt(10)

            set_cell_border(cell, top={'sz': 4}, bottom={'sz': 4}, left={'sz': 4}, right={'sz': 4})

    # MESCLAGEM VERTICAL: Coluna 0 (Título) e Coluna 1 (Objetivo Geral)
    if total_linhas > 1:
        # Mesclagem Título
        c_tit_topo = tabela.rows[1].cells[0]
        for r in range(2, total_linhas + 1):
            c_tit_topo.merge(tabela.rows[r].cells[0])
        c_tit_topo.text = titulo_curto
        c_tit_topo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p_t = c_tit_topo.paragraphs[0]
        p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_t.paragraph_format.line_spacing = 1.0
        if p_t.runs:
            p_t.runs[0].font.name = "Times New Roman"
            p_t.runs[0].font.size = Pt(10)

        # Mesclagem Objetivo Geral
        c_obj_topo = tabela.rows[1].cells[1]
        for r in range(2, total_linhas + 1):
            c_obj_topo.merge(tabela.rows[r].cells[1])
        c_obj_topo.text = obj_geral
        c_obj_topo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p_o = c_obj_topo.paragraphs[0]
        p_o.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_o.paragraph_format.line_spacing = 1.0
        if p_o.runs:
            p_o.runs[0].font.name = "Times New Roman"
            p_o.runs[0].font.size = Pt(10)

    # Fonte
    p_fonte = doc.add_paragraph()
    p_fonte.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_fonte.paragraph_format.space_before = Pt(3)
    p_fonte.paragraph_format.space_after = Pt(18)
    p_fonte.paragraph_format.line_spacing = 1.0
    escrever_fonte(p_fonte, f"Fonte: Construção do autor ({metadata.get('ano', '2026')}).")