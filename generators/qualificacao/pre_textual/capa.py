"""
Módulo granular para geração exclusiva da CAPA do Relatório de Qualificação
conforme a Resolução nº 009/2025-PPGSP/UFPA (Art. 1º, I, item 1 e modelo da pág. 11).
"""

import os
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from ..titulo import escrever_titulo_e_subtitulo, nome_discente

def build_capa(doc, metadata, assets_dir="assets"):
    """
    Renderiza a Capa segundo os 9 itens obrigatórios do Art. 1º, I, 1 da Res. 009/2025.
    
    Parâmetros:
      - doc: Objeto Document do python-docx
      - metadata: Dicionário contendo 'titulo', 'autor', 'local', 'ano' e 'nivel'
      - assets_dir: Diretório onde se encontra 'brasao_ufpa.png'
    """
    # -------------------------------------------------------------
    # (i) Brasão da UFPA
    # -------------------------------------------------------------
    caminho_brasao = os.path.join(assets_dir, "brasao_ufpa.png")
    p_brasao = doc.add_paragraph()
    p_brasao.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_brasao.paragraph_format.space_before = Pt(0)
    p_brasao.paragraph_format.space_after = Pt(6)

    if os.path.exists(caminho_brasao):
        run_brasao = p_brasao.add_run()
        run_brasao.add_picture(caminho_brasao, width=Cm(2.5))
    else:
        run_brasao = p_brasao.add_run("[BRASÃO DA UFPA - Inserir imagem 'brasao_ufpa.png' na pasta assets]")
        run_brasao.italic = True
        run_brasao.font.size = Pt(10)
        run_brasao.font.color.rgb = RGBColor(120, 120, 120)

    # -------------------------------------------------------------
    # (ii) a (v) Cabeçalho Institucional
    # -------------------------------------------------------------
    nivel = metadata.get("nivel", "mestrado").strip().lower()
    nivel_texto = "DOUTORADO EM SEGURANÇA PÚBLICA" if nivel in ["doutorado", "tese"] else "MESTRADO EM SEGURANÇA PÚBLICA"

    p_cabecalho = doc.add_paragraph()
    p_cabecalho.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cabecalho.paragraph_format.line_spacing = 1.0
    p_cabecalho.paragraph_format.space_before = Pt(0)
    p_cabecalho.paragraph_format.space_after = Pt(24)

    linhas_cabecalho = [
        "UNIVERSIDADE FEDERAL DO PARÁ",
        "INSTITUTO DE CIÊNCIAS EXATAS E NATURAIS",
        "PROGRAMA DE PÓS-GRADUAÇÃO EM SEGURANÇA PÚBLICA",
        nivel_texto
    ]
    for linha in linhas_cabecalho:
        r = p_cabecalho.add_run(f"{linha}\n")
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    # -------------------------------------------------------------
    # (vi) Título e Subtítulo (Times 14 Negrito)
    # -------------------------------------------------------------
    titulo_raw = metadata.get("titulo", "").strip()
    p_titulo = doc.add_paragraph()
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_titulo.paragraph_format.line_spacing = 1.0
    p_titulo.paragraph_format.space_before = Pt(36)
    p_titulo.paragraph_format.space_after = Pt(36)

    if not escrever_titulo_e_subtitulo(p_titulo, titulo_raw, tamanho=14):
        r_tit = p_titulo.add_run("[TÍTULO DO TRABALHO: Evidenciar obrigatoriamente o Produto da Pesquisa]")
        r_tit.italic = True
        r_tit.font.size = Pt(14)
        r_tit.font.color.rgb = RGBColor(120, 120, 120)

    # -------------------------------------------------------------
    # (vii) Nome do(a) discente (Times 14 Negrito, Caixa Baixa)
    # -------------------------------------------------------------
    autor_raw = nome_discente(metadata.get("autor", ""))
    p_autor = doc.add_paragraph()
    p_autor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_autor.paragraph_format.space_before = Pt(36)
    p_autor.paragraph_format.space_after = Pt(0)

    if autor_raw:
        r_aut = p_autor.add_run(autor_raw)
        r_aut.bold = True
        r_aut.font.name = "Times New Roman"
        r_aut.font.size = Pt(14)
    else:
        r_aut = p_autor.add_run("[Nome Completo do(a) Discente]")
        r_aut.italic = True
        r_aut.font.size = Pt(14)
        r_aut.font.color.rgb = RGBColor(120, 120, 120)