"""Montador da Tese de Doutorado conforme a Resolução nº 010/2025-PPGSP/UFPA."""
import docx
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.styles import apply_base_styles, set_page_margins, insert_brasao, insert_cabecalho_institucional
from core.xml_utils import add_page_number_field, configure_section_page_numbers

def gerar_documento_tese(caminho_entrada, caminho_saida, assets_dir="assets"):
    """
    Estrutura de Tese de Doutorado:
    - Mesma estrutura de 4 capítulos da dissertação.
    - Exigência ampliada de 04 artigos científicos no Capítulo 2.
    - Exigência ampliada de no mínimo 08 Produtos Técnicos e Tecnológicos (PTTs) no Capítulo 3.
    """
    doc = docx.Document()
    apply_base_styles(doc)

    titulo_trabalho = "TESE DE DOUTORADO EM SEGURANÇA PÚBLICA: FUSÃO MULTIMODAL AVANÇADA E MODELOS PREDITIVOS"
    autor = "Leonardo da Silva Costa"
    orientador = "Prof. Dr. Edson Marcos Leal Soares Ramos"
    ano = "2026"

    sec_pre = doc.sections[0]
    set_page_margins(sec_pre)
    configure_section_page_numbers(sec_pre, num_format='roman', start_at=1)
    sec_pre.different_first_page_header_footer = True

    # 1. Capa
    insert_brasao(doc, assets_dir)
    insert_cabecalho_institucional(doc)

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(36)
    p_tit.paragraph_format.space_after = Pt(36)
    r_tit = p_tit.add_run(f"{titulo_trabalho}\n")
    r_tit.bold = True
    r_tit.font.size = Pt(14)

    p_aut = doc.add_paragraph()
    p_aut.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aut.paragraph_format.space_before = Pt(36)
    p_aut.paragraph_format.space_after = Pt(72)
    r_aut = p_aut.add_run(f"{autor}\n")
    r_aut.bold = True
    r_aut.font.size = Pt(14)

    p_loc = doc.add_paragraph()
    p_loc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_loc = p_loc.add_run(f"Belém-Pará\n{ano}")
    r_loc.bold = True
    r_loc.font.size = Pt(12)

    doc.add_page_break()

    # 2. Folha de Rosto
    insert_brasao(doc, assets_dir)
    insert_cabecalho_institucional(doc)

    p_aut2 = doc.add_paragraph()
    p_aut2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aut2.paragraph_format.space_before = Pt(12)
    p_aut2.paragraph_format.space_after = Pt(18)
    r_aut2 = p_aut2.add_run(f"{autor}\n")
    r_aut2.bold = True
    r_aut2.font.size = Pt(14)

    p_tit2 = doc.add_paragraph()
    p_tit2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_tit2 = p_tit2.add_run(f"{titulo_trabalho}\n")
    r_tit2.bold = True
    r_tit2.font.size = Pt(14)

    p_rec = doc.add_paragraph()
    p_rec.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_rec.paragraph_format.left_indent = Cm(8.0)
    p_rec.paragraph_format.line_spacing = 1.0
    r_rec = p_rec.add_run(
        "Tese apresentada ao Colegiado do Programa de Pós-Graduação em Segurança Pública, "
        "do Instituto de Ciências Exatas e Naturais, da Universidade Federal do Pará, "
        "como requisito parcial para a obtenção do título de Doutor em Segurança Pública.\n"
    )
    r_rec.font.size = Pt(12)

    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_info.paragraph_format.line_spacing = 1.0
    p_info.paragraph_format.space_after = Pt(36)
    p_info.add_run(
        "Área de Concentração: Segurança Pública, Justiça, Conflitos e Cidadania.\n"
        "Linha de Pesquisa: Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação.\n"
        f"Orientador(a): {orientador}\n"
    )

    doc.add_page_break()

    # Seção Textual
    sec_txt = doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
    set_page_margins(sec_txt)
    sec_txt.header.is_linked_to_previous = False
    configure_section_page_numbers(sec_txt, num_format='decimal', start_at=1)

    hdr_txt = sec_txt.header.paragraphs[0]
    hdr_txt.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr = hdr_txt.add_run()
    r_hdr.font.name = 'Times New Roman'
    r_hdr.font.size = Pt(11)
    add_page_number_field(r_hdr)

    p_c1 = doc.add_paragraph()
    p_c1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c1.paragraph_format.space_before = Pt(24)
    r1 = p_c1.add_run("CAPÍTULO 1 – CONSIDERAÇÕES GERAIS\n")
    r1.bold = True

    p_c2 = doc.add_paragraph()
    p_c2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c2.paragraph_format.space_before = Pt(24)
    r2 = p_c2.add_run("CAPÍTULO 2 – ARTIGOS CIENTÍFICOS (04 ARTIGOS)\n")
    r2.bold = True

    p_c3 = doc.add_paragraph()
    p_c3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c3.paragraph_format.space_before = Pt(24)
    r3 = p_c3.add_run("CAPÍTULO 3 – PRODUTOS E PROPOSTAS DE INTERVENÇÃO (>= 08 PTTS)\n")
    r3.bold = True

    p_c4 = doc.add_paragraph()
    p_c4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c4.paragraph_format.space_before = Pt(24)
    r4 = p_c4.add_run("CAPÍTULO 4 – CONSIDERAÇÕES FINAIS E RECOMENDAÇÕES\n")
    r4.bold = True

    doc.save(caminho_saida)