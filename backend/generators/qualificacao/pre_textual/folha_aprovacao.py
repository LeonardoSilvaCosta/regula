"""
Módulo granular para a Folha de Aprovação do Relatório de Qualificação
conforme o modelo oficial da Resolução nº 009/2025-PPGSP/UFPA (página 14).
"""

import os
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from core.styles import BRASAO_UFPA_ALTURA, BRASAO_UFPA_LARGURA
from ..titulo import escrever_titulo_e_subtitulo, nome_discente, separar_titulacao


def _remove_table_borders(table):
    """Remove completamente qualquer borda da tabela através de tblBorders XML."""
    tblPr = table._tbl.tblPr
    tblBorders = tblPr.first_child_found_in("w:tblBorders")
    if tblBorders is not None:
        tblPr.remove(tblBorders)
    borders_xml = (
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'  <w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'  <w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'  <w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'  <w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'  <w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(parse_xml(borders_xml))


def _papel(membro):
    return (membro.get("funcao") or membro.get("papel") or "").strip().lower()


def membros_ordenados(metadata):
    """Orientador, coorientador e demais em ordem alfabética. Não inventa avaliadores."""
    banca = [dict(m) for m in (metadata.get("banca") or [])]
    if not banca:
        if (metadata.get("orientador") or "").strip():
            banca.append({
                "nome": metadata["orientador"].strip(),
                "instituicao": "",
                "funcao": "Orientador",
            })
        if (metadata.get("coorientador") or "").strip():
            banca.append({
                "nome": metadata["coorientador"].strip(),
                "instituicao": "",
                "funcao": "Coorientador",
            })
        return banca

    orientadores, coorientadores, demais = [], [], []
    for membro in banca:
        papel = _papel(membro)
        if "coorient" in papel:
            coorientadores.append(membro)
        elif "orient" in papel:
            orientadores.append(membro)
        else:
            demais.append(membro)

    coorientador = (metadata.get("coorientador") or "").strip()
    if coorientador and not coorientadores:
        coorientadores.append({
            "nome": coorientador,
            "instituicao": "",
            "funcao": "Coorientador",
        })

    def _chave(membro):
        nome, _tit = separar_titulacao(membro.get("nome", ""))
        return nome.lower()

    demais.sort(key=_chave)
    return orientadores + coorientadores + demais


def _paragrafo_vazio(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    return p


def _escrever_linha_celula(cell, texto, tamanho=12, italico=True, espaco_depois=1):
    if cell.paragraphs[0].text:
        p = cell.add_paragraph()
    else:
        p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(espaco_depois)
    if not texto:
        return p
    r = p.add_run(texto)
    r.font.name = "Times New Roman"
    r.font.size = Pt(tamanho)
    r.italic = italico
    return p


def build_folha_aprovacao(doc, metadata, assets_dir="assets"):
    # 1. Brasão da UFPA
    brasao_path = os.path.join(assets_dir, "brasao_ufpa.png")
    if os.path.exists(brasao_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(0)
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(
            brasao_path, width=BRASAO_UFPA_LARGURA, height=BRASAO_UFPA_ALTURA
        )

    # 2. Cabeçalho Institucional
    is_doutorado = metadata.get("nivel", "mestrado").lower() in ["doutorado", "tese"]
    curso_nome = "DOUTORADO EM SEGURANÇA PÚBLICA" if is_doutorado else "MESTRADO EM SEGURANÇA PÚBLICA"
    tipo_trabalho = "Tese" if is_doutorado else "Dissertação"

    cabecalho = [
        "UNIVERSIDADE FEDERAL DO PARÁ",
        "INSTITUTO DE CIÊNCIAS EXATAS E NATURAIS",
        "PROGRAMA DE PÓS-GRADUAÇÃO EM SEGURANÇA PÚBLICA",
        curso_nome
    ]
    for linha in cabecalho:
        p_c = doc.add_paragraph()
        p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_c.paragraph_format.line_spacing = 1.0
        p_c.paragraph_format.space_before = Pt(0)
        p_c.paragraph_format.space_after = Pt(2)
        r_c = p_c.add_run(linha)
        r_c.bold = True
        r_c.font.name = "Times New Roman"
        r_c.font.size = Pt(12)

    # 3. Título e Autor (Times 14, negrito; subtítulo em estilo frase)
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(14)
    p_tit.paragraph_format.space_after = Pt(6)
    if not escrever_titulo_e_subtitulo(p_tit, metadata.get("titulo", ""), tamanho=14):
        r_t = p_tit.add_run("[TÍTULO DO RELATÓRIO DE QUALIFICAÇÃO]")
        r_t.italic = True
        r_t.font.name = "Times New Roman"
        r_t.font.size = Pt(14)

    p_aut = doc.add_paragraph()
    p_aut.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aut.paragraph_format.space_before = Pt(0)
    p_aut.paragraph_format.space_after = Pt(12)
    autor = nome_discente(metadata.get("autor")) or "[Nome do(a) discente]"
    r_a = p_aut.add_run(autor)
    r_a.bold = True
    r_a.font.name = "Times New Roman"
    r_a.font.size = Pt(14)

    # 4. Texto Padrão de Aprovação
    p_ap = doc.add_paragraph()
    p_ap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_ap.paragraph_format.first_line_indent = Cm(0)
    p_ap.paragraph_format.left_indent = Cm(0)
    p_ap.paragraph_format.line_spacing = 1.15
    p_ap.paragraph_format.space_before = Pt(0)
    p_ap.paragraph_format.space_after = Pt(0)
    r_ap = p_ap.add_run(
        "Relatório de qualificação submetido à avaliação, como requisito parcial para qualificação "
        f"do(a) autor(a) ao desenvolvimento da {tipo_trabalho} "
        "no Programa de Pós-graduação em Segurança Pública, "
        "do Instituto de Ciências Exatas e Naturais, "
        "da Universidade Federal do Pará, "
        "na área de concentração: Segurança Pública, Justiça, Conflitos e Cidadania."
    )
    r_ap.bold = False
    r_ap.font.name = "Times New Roman"
    r_ap.font.size = Pt(12)

    # 5. Local e Data
    _paragrafo_vazio(doc)
    ano = metadata.get("ano", "2026")
    data_txt = f"Belém, Pará, ____ de _______________ de {ano}."
    p_data = doc.add_paragraph()
    p_data.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_data.paragraph_format.line_spacing = 1.0
    p_data.paragraph_format.space_before = Pt(12)
    p_data.paragraph_format.space_after = Pt(18)
    r_data = p_data.add_run(data_txt)
    r_data.font.name = "Times New Roman"
    r_data.font.size = Pt(12)
    _paragrafo_vazio(doc)

    # 6. Coordenador (Times 12, como o cabeçalho institucional)
    coord = (metadata.get("coordenador") or "").strip() or "[Nome do Coordenador]"
    nome_coord, titulacao_coord = separar_titulacao(coord)
    p_cd1 = doc.add_paragraph()
    p_cd1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cd1.paragraph_format.line_spacing = 1.0
    p_cd1.paragraph_format.space_before = Pt(0)
    p_cd1.paragraph_format.space_after = Pt(2)
    if titulacao_coord:
        r_titulacao = p_cd1.add_run(f"{titulacao_coord} ")
        r_titulacao.font.name = "Times New Roman"
        r_titulacao.font.size = Pt(12)
        r_titulacao.italic = True
        r_nome = p_cd1.add_run(nome_coord)
    else:
        r_nome = p_cd1.add_run(coord)
    r_nome.font.name = "Times New Roman"
    r_nome.font.size = Pt(12)
    r_nome.italic = True

    p_cd2 = doc.add_paragraph()
    p_cd2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cd2.paragraph_format.line_spacing = 1.0
    p_cd2.paragraph_format.space_before = Pt(0)
    p_cd2.paragraph_format.space_after = Pt(0)
    r_cd2 = p_cd2.add_run("Coordenador do Programa de Pós-Graduação em Segurança Pública")
    r_cd2.font.name = "Times New Roman"
    r_cd2.font.size = Pt(12)
    r_cd2.italic = True

    # 7. BANCA EXAMINADORA
    _paragrafo_vazio(doc)
    p_bt = doc.add_paragraph()
    p_bt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_bt.paragraph_format.space_before = Pt(0)
    p_bt.paragraph_format.space_after = Pt(8)
    r_bt = p_bt.add_run("BANCA EXAMINADORA")
    r_bt.bold = True
    r_bt.font.name = "Times New Roman"
    r_bt.font.size = Pt(12)

    membros = membros_ordenados(metadata)
    if not membros:
        p_vazio = doc.add_paragraph()
        p_vazio.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_v = p_vazio.add_run("[Membros da banca não informados]")
        r_v.italic = True
        r_v.font.name = "Times New Roman"
        r_v.font.size = Pt(12)
        return

    n_linhas = (len(membros) + 1) // 2
    tbl = doc.add_table(rows=n_linhas, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    _remove_table_borders(tbl)

    for i, membro in enumerate(membros):
        cell = tbl.rows[i // 2].cells[i % 2]
        cell.width = Cm(7.8)
        nome, titulacao = separar_titulacao(membro.get("nome", ""))
        instituicao = (membro.get("instituicao") or "").strip() or "[Instituição de vínculo]"
        funcao = (membro.get("funcao") or membro.get("papel") or "").strip()

        _escrever_linha_celula(cell, nome or "[Nome do membro]", tamanho=12, italico=True, espaco_depois=1)
        if titulacao:
            _escrever_linha_celula(cell, titulacao, tamanho=12, italico=True, espaco_depois=1)
        _escrever_linha_celula(cell, instituicao, tamanho=12, italico=True, espaco_depois=1)
        if funcao:
            _escrever_linha_celula(cell, funcao, tamanho=12, italico=True, espaco_depois=6)