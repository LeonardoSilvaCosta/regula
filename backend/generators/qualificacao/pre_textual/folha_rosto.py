"""
Módulo granular para geração exclusiva da FOLHA DE ROSTO do Relatório de Qualificação
conforme a Resolução nº 009/2025-PPGSP/UFPA (Art. 1º, I, item 2 e modelo da pág. 12).
"""

import os
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.styles import BRASAO_UFPA_ALTURA, BRASAO_UFPA_LARGURA
from ..titulo import escrever_titulo_e_subtitulo, nome_discente


def _campo(paragrafo, rotulo, valor, italico=False):
    r_rotulo = paragrafo.add_run(f"{rotulo}:")
    r_rotulo.bold = True
    r_rotulo.font.name = "Times New Roman"
    r_rotulo.font.size = Pt(12)
    r_val = paragrafo.add_run(f" {valor}")
    r_val.bold = False
    r_val.italic = italico
    r_val.font.name = "Times New Roman"
    r_val.font.size = Pt(12)
    if italico:
        r_val.font.color.rgb = RGBColor(120, 120, 120)


def _paragrafo_campo(doc, rotulo, valor, italico=False, space_before=0):
    """Uma linha por campo, como no modelo oficial (rótulo+':' em negrito)."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.line_spacing = 1.15
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.first_line_indent = Cm(0)
    _campo(p, rotulo, valor, italico=italico)
    return p

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
    tipo_trabalho = "Tese" if is_doutorado else "Dissertação"

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
        run_brasao.add_picture(
            caminho_brasao, width=BRASAO_UFPA_LARGURA, height=BRASAO_UFPA_ALTURA
        )
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

    r_rec = p_rec.add_run(
        "Relatório de Qualificação apresentado ao Colegiado do Programa de Pós-Graduação em "
        "Segurança Pública, da Universidade Federal do Pará, como requisito parcial à qualificação "
        "ao desenvolvimento da "
    )
    r_rec.font.name = "Times New Roman"
    r_rec.font.size = Pt(12)
    r_tipo = p_rec.add_run(tipo_trabalho)
    r_tipo.bold = True
    r_tipo.font.name = "Times New Roman"
    r_tipo.font.size = Pt(12)
    r_fim = p_rec.add_run(".")
    r_fim.font.name = "Times New Roman"
    r_fim.font.size = Pt(12)

    # -------------------------------------------------------------
    # (ix) e (x) Área, Linha, Orientador e Coorientador à Margem Esquerda
    # -------------------------------------------------------------
    area = metadata.get("area_concentracao", "Segurança Pública, Justiça, Conflitos e Cidadania").strip()
    linha = metadata.get("linha_pesquisa", "Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação").strip()
    orientador = metadata.get("orientador", "").strip()
    coorientador = metadata.get("coorientador", "").strip()

    area_txt = area if area.endswith(".") else f"{area}."
    linha_txt = linha if linha.endswith(".") else f"{linha}."
    _paragrafo_campo(doc, "Área de Concentração", area_txt, space_before=0)
    _paragrafo_campo(doc, "Linha de Pesquisa", linha_txt, space_before=6)
    if orientador:
        _paragrafo_campo(doc, "Orientador(a)", orientador, space_before=10)
    else:
        _paragrafo_campo(
            doc,
            "Orientador(a)",
            "[Nome Completo e Titulação do(a) Orientador(a)]",
            italico=True,
            space_before=10,
        )
    if coorientador:
        _paragrafo_campo(doc, "Coorientador(a)", coorientador, space_before=10)

    # (xi) e (xii) Local e ano no corpo, na base da página (não no rodapé)
    local = (metadata.get("local") or "Belém-Pará").strip()
    ano = (metadata.get("ano") or "2026").strip()

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc.paragraph_format.line_spacing = 1.0
    p_loc.paragraph_format.space_before = Pt(72)
    p_loc.paragraph_format.space_after = Pt(0)

    r_loc = p_loc.add_run(f"{local} {ano}" if " " in ano else f"{local}\n{ano}")
    r_loc.font.name = "Times New Roman"
    r_loc.font.size = Pt(12)
    r_loc.bold = True