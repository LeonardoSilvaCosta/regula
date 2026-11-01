"""
Módulo granular para geração exclusiva da FOLHA DE ROSTO do Relatório de Qualificação
conforme a Resolução nº 009/2025-PPGSP/UFPA (Art. 1º, I, item 2 e modelo da pág. 12).
"""

import os
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from ..titulo import escrever_titulo_e_subtitulo, nome_discente

def build_folha_rosto(doc, metadata, assets_dir="assets"):
    """
    Renderiza a Folha de Rosto segundo a ordem e especificações do Art. 1º, I, 2.
    
    Ordem oficial estrita:
      (i) Brasão da UFPA
      (ii) a (v) Cabeçalho Institucional
      (vi) Nome do(a) discente
      (vii) Título e subtítulo
      (viii) Texto recuado a 8 cm à direita (Dissertação ou Tese parametrizado)
      (ix) Área de Concentração e Linha de Pesquisa à margem esquerda
      (x) Nome e titulação do Orientador(a) e Coorientador(a)
      (xi) Belém-Pará
      (xii) Ano de aprovação
    """
    is_doutorado = metadata.get("nivel", "mestrado").strip().lower() in ["doutorado", "tese"]
    nivel_cabecalho = "DOUTORADO EM SEGURANÇA PÚBLICA" if is_doutorado else "MESTRADO EM SEGURANÇA PÚBLICA"
    tipo_trabalho_artigo = "ao desenvolvimento da Tese" if is_doutorado else "ao desenvolvimento da Dissertação"

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
        run_brasao = p_brasao.add_run("[BRASÃO DA UFPA]")
        run_brasao.italic = True
        run_brasao.font.size = Pt(10)
        run_brasao.font.color.rgb = RGBColor(120, 120, 120)

    # -------------------------------------------------------------
    # (ii) a (v) Cabeçalho Institucional (Times 12 Negrito)
    # -------------------------------------------------------------
    p_cabecalho = doc.add_paragraph()
    p_cabecalho.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cabecalho.paragraph_format.line_spacing = 1.0
    p_cabecalho.paragraph_format.space_before = Pt(0)
    p_cabecalho.paragraph_format.space_after = Pt(18)

    linhas_cabecalho = [
        "UNIVERSIDADE FEDERAL DO PARÁ",
        "INSTITUTO DE CIÊNCIAS EXATAS E NATURAIS",
        "PROGRAMA DE PÓS-GRADUAÇÃO EM SEGURANÇA PÚBLICA",
        nivel_cabecalho
    ]
    for linha in linhas_cabecalho:
        r = p_cabecalho.add_run(f"{linha}\n")
        r.bold = True
        r.font.name = "Times New Roman"
        r.font.size = Pt(12)

    # -------------------------------------------------------------
    # (vi) Nome do(a) discente (vem ANTES do título, Times 14 Negrito)
    # -------------------------------------------------------------
    autor_raw = nome_discente(metadata.get("autor", ""))
    p_autor = doc.add_paragraph()
    p_autor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_autor.paragraph_format.space_before = Pt(12)
    p_autor.paragraph_format.space_after = Pt(18)

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

    # -------------------------------------------------------------
    # (vii) Título e Subtítulo (Times 14 Negrito)
    # -------------------------------------------------------------
    titulo_raw = metadata.get("titulo", "").strip()
    p_titulo = doc.add_paragraph()
    p_titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_titulo.paragraph_format.line_spacing = 1.0
    p_titulo.paragraph_format.space_before = Pt(0)
    p_titulo.paragraph_format.space_after = Pt(24)

    if not escrever_titulo_e_subtitulo(p_titulo, titulo_raw, tamanho=14):
        r_tit = p_titulo.add_run("[TÍTULO DO RELATÓRIO DE QUALIFICAÇÃO]")
        r_tit.italic = True
        r_tit.font.size = Pt(14)
        r_tit.font.color.rgb = RGBColor(120, 120, 120)

    # -------------------------------------------------------------
    # (viii) Texto Recuado a 8 cm à direita (Times 12, Espaço Simples)
    # -------------------------------------------------------------
    p_rec = doc.add_paragraph()
    p_rec.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_rec.paragraph_format.left_indent = Cm(8.0)
    p_rec.paragraph_format.line_spacing = 1.0
    p_rec.paragraph_format.space_before = Pt(0)
    p_rec.paragraph_format.space_after = Pt(18)

    texto_recuado = (
        "Relatório de Qualificação apresentado ao Colegiado do Programa de Pós-Graduação em "
        f"Segurança Pública, da Universidade Federal do Pará, como requisito parcial à qualificação "
        f"{tipo_trabalho_artigo}."
    )
    r_rec = p_rec.add_run(texto_recuado)
    r_rec.font.name = "Times New Roman"
    r_rec.font.size = Pt(12)

    # -------------------------------------------------------------
    # (ix) e (x) Área, Linha, Orientador e Coorientador à Margem Esquerda
    # -------------------------------------------------------------
    area = metadata.get("area_concentracao", "Segurança Pública, Justiça, Conflitos e Cidadania").strip()
    linha = metadata.get("linha_pesquisa", "Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação").strip()
    orientador = metadata.get("orientador", "").strip()
    coorientador = metadata.get("coorientador", "").strip()

    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_info.paragraph_format.line_spacing = 1.0
    p_info.paragraph_format.space_before = Pt(0)
    p_info.paragraph_format.space_after = Pt(36)

    # Área de Concentração
    r_area_rotulo = p_info.add_run("Área de Concentração: ")
    r_area_rotulo.font.name = "Times New Roman"
    r_area_rotulo.font.size = Pt(12)
    r_area_val = p_info.add_run(f"{area}\n")
    r_area_val.font.name = "Times New Roman"
    r_area_val.font.size = Pt(12)

    # Linha de Pesquisa
    r_linha_rotulo = p_info.add_run("Linha de Pesquisa: ")
    r_linha_rotulo.font.name = "Times New Roman"
    r_linha_rotulo.font.size = Pt(12)
    r_linha_val = p_info.add_run(f"{linha}\n")
    r_linha_val.font.name = "Times New Roman"
    r_linha_val.font.size = Pt(12)

    # Orientador(a)
    r_orient_rotulo = p_info.add_run("Orientador(a): ")
    r_orient_rotulo.font.name = "Times New Roman"
    r_orient_rotulo.font.size = Pt(12)
    if orientador:
        r_orient_val = p_info.add_run(f"{orientador}\n")
    else:
        r_orient_val = p_info.add_run("[Nome Completo e Titulação do(a) Orientador(a)]\n")
        r_orient_val.italic = True
        r_orient_val.font.color.rgb = RGBColor(120, 120, 120)
    r_orient_val.font.name = "Times New Roman"
    r_orient_val.font.size = Pt(12)

    # Coorientador(a) se houver
    if coorientador:
        r_coorient_rotulo = p_info.add_run("Coorientador(a): ")
        r_coorient_rotulo.font.name = "Times New Roman"
        r_coorient_rotulo.font.size = Pt(12)
        r_coorient_val = p_info.add_run(f"{coorientador}\n")
        r_coorient_val.font.name = "Times New Roman"
        r_coorient_val.font.size = Pt(12)

    # -------------------------------------------------------------
    # (xi) e (xii) Local e Ano (Centralizado, Negrito, Espaço Simples)
    # -------------------------------------------------------------
    local = metadata.get("local", "Belém-Pará").strip()
    ano = str(metadata.get("ano", "2026")).strip()

    p_rodape = doc.add_paragraph()
    p_rodape.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_rodape.paragraph_format.line_spacing = 1.0
    p_rodape.paragraph_format.space_before = Pt(0)
    p_rodape.paragraph_format.space_after = Pt(0)

    r_loc = p_rodape.add_run(f"{local}\n{ano}")
    r_loc.bold = True
    r_loc.font.name = "Times New Roman"
    r_loc.font.size = Pt(12)

    # Quebra de página para o próximo elemento pré-textual
    doc.add_page_break()