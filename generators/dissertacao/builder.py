"""Montador da Dissertação de Mestrado conforme a Resolução nº 010/2025-PPGSP/UFPA."""
import docx
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

from core.styles import apply_base_styles, set_page_margins, insert_brasao, insert_cabecalho_institucional
from core.xml_utils import set_cell_border, add_page_number_field, configure_section_page_numbers
from core.ptt_schema import formatar_ficha_22_itens

def gerar_documento_dissertacao(caminho_entrada, caminho_saida, assets_dir="assets"):
    doc = docx.Document()
    apply_base_styles(doc)

    titulo_trabalho = (
        "ESTEIRA PREDITIVA MULTIMODAL DE SUPORTE À DECISÃO CLÍNICA NO CIAP/PMPA: "
        "MODELOS DE APRENDIZADO DE MÁQUINA PARA PREDIÇÃO DE DESFECHOS RELACIONADOS "
        "À SAÚDE MENTAL DE POLICIAIS MILITARES DO PARÁ A PARTIR DE PRONTUÁRIOS PSICOSSOCIAIS"
    )
    autor = "Leonardo da Silva Costa"
    orientador = "Prof. Dr. Edson Marcos Leal Soares Ramos"
    ano = "2026"

    # SEÇÃO 1: PRÉ-TEXTUAL (Paginação Romana Minúscula Itálico 11)
    sec_pre = doc.sections[0]
    set_page_margins(sec_pre)
    configure_section_page_numbers(sec_pre, num_format='roman', start_at=1)
    sec_pre.different_first_page_header_footer = True

    hdr_pre = sec_pre.header.paragraphs[0]
    hdr_pre.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr_pre = hdr_pre.add_run()
    r_hdr_pre.font.name = 'Times New Roman'
    r_hdr_pre.font.size = Pt(11)
    r_hdr_pre.italic = True
    add_page_number_field(r_hdr_pre)

    # 1. Capa
    insert_brasao(doc, assets_dir)
    insert_cabecalho_institucional(doc)

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.line_spacing = 1.0
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
    p_loc.paragraph_format.line_spacing = 1.0
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
    p_tit2.paragraph_format.line_spacing = 1.0
    p_tit2.paragraph_format.space_after = Pt(24)
    r_tit2 = p_tit2.add_run(f"{titulo_trabalho}\n")
    r_tit2.bold = True
    r_tit2.font.size = Pt(14)

    p_rec = doc.add_paragraph()
    p_rec.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_rec.paragraph_format.left_indent = Cm(8.0)
    p_rec.paragraph_format.line_spacing = 1.0
    p_rec.paragraph_format.space_after = Pt(18)
    r_rec = p_rec.add_run(
        "Dissertação apresentada ao Colegiado do Programa de Pós-Graduação em Segurança Pública, "
        "do Instituto de Ciências Exatas e Naturais, da Universidade Federal do Pará, "
        "como requisito parcial para a obtenção do título de Mestre em Segurança Pública.\n"
    )
    r_rec.font.size = Pt(12)

    p_info = doc.add_paragraph()
    p_info.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_info.paragraph_format.line_spacing = 1.0
    p_info.paragraph_format.space_after = Pt(36)
    r_info = p_info.add_run(
        "Área de Concentração: Segurança Pública, Justiça, Conflitos e Cidadania.\n"
        "Linha de Pesquisa: Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação.\n"
        f"Orientador(a): {orientador}\n"
    )
    r_info.font.size = Pt(12)

    p_loc2 = doc.add_paragraph()
    p_loc2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_loc2.paragraph_format.line_spacing = 1.0
    r_loc2 = p_loc2.add_run(f"Belém-Pará\n{ano}")
    r_loc2.bold = True
    r_loc2.font.size = Pt(12)

    doc.add_page_break()

    # -----------------------------------------------------------------------
    # SEÇÃO 2: PARTE TEXTUAL (4 Capítulos Obrigatórios da Resolução 010/2025)
    # -----------------------------------------------------------------------
    sec_txt = doc.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)
    set_page_margins(sec_txt)
    sec_txt.header.is_linked_to_previous = False
    configure_section_page_numbers(sec_txt, num_format='decimal', start_at=1)

    hdr_txt = sec_txt.header.paragraphs[0]
    hdr_txt.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_hdr_txt = hdr_txt.add_run()
    r_hdr_txt.font.name = 'Times New Roman'
    r_hdr_txt.font.size = Pt(11)
    add_page_number_field(r_hdr_txt)

    def add_cap_title(txt):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(18)
        r = p.add_run(txt)
        r.bold = True
        r.font.size = Pt(12)

    def add_sec_title(txt):
        p = doc.add_paragraph()
        p.paragraph_format.space_before = Pt(14)
        p.paragraph_format.space_after = Pt(6)
        r = p.add_run(txt)
        r.bold = True
        r.font.size = Pt(12)

    def add_body_p(txt):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.first_line_indent = Cm(1.27)
        p.paragraph_format.line_spacing = 1.5
        p.add_run(txt)

    # CAPÍTULO 1
    add_cap_title("CAPÍTULO 1 – CONSIDERAÇÕES GERAIS")
    add_sec_title("1.1 INTRODUÇÃO")
    add_body_p("Contextualização do cuidado em saúde mental na Polícia Militar do Pará e desafios de vigilância proativa.")
    add_sec_title("1.2 JUSTIFICATIVA DA PESQUISA")
    add_body_p("Relevância acadêmica, institucional e social da triagem preditiva multimodal via BERTimbau e SHAP.")
    add_sec_title("1.3 PROBLEMA DE PESQUISA")
    add_body_p("De que maneira modelos de ML multimodais contribuem para a predição precoce de desfechos no CIAP/PMPA?")
    add_sec_title("1.4 REVISÃO DA LITERATURA / REFERENCIAL TEÓRICO")
    add_body_p("Fundamentação conceitual em informática em saúde, psiquiatria computacional e estresse policial.")
    add_sec_title("1.5 OBJETIVOS")
    add_body_p("Desenvolvimento e avaliação da esteira preditiva multimodal estruturada em 2 artigos e 6 PTTs.")
    add_sec_title("1.6 QUESTÃO NORTEADORA")
    add_body_p("É viável antecipar crises agudas com AUROC > 0,85 em janelas de 90 dias via fusão intermediária?")
    add_sec_title("1.7 METODOLOGIA")
    add_body_p("Coorte de 5.706 atendimentos, amostra balanceada de 360 casos auditada por Tukey e modelagem com XGBoost e Transformers.")

    # CAPÍTULO 2: ARTIGOS CIENTÍFICOS (Mínimo 2 para Mestrado)
    doc.add_page_break()
    add_cap_title("CAPÍTULO 2 – ARTIGOS CIENTÍFICOS")
    add_sec_title("2.1 ARTIGO CIENTÍFICO 1")
    add_body_p("Caracterização Epidemiológica e Padrões Clínico-Léxicos de Saúde Mental na Polícia Militar do Pará.")
    p_note1 = doc.add_paragraph()
    p_note1.add_run("Nota: Artigo em elaboração a ser submetido a periódico Qualis A1/A2, primeiro autor Leonardo da Silva Costa.").italic = True

    add_sec_title("2.2 ARTIGO CIENTÍFICO 2")
    add_body_p("Modelagem Multimodal com Fusão Intermediária e Explainable AI (SHAP) para Predição de Desfechos de Saúde Ocupacional.")
    p_note2 = doc.add_paragraph()
    p_note2.add_run("Nota: Artigo em elaboração a ser submetido a periódico Qualis A1/A2, primeiro autor Leonardo da Silva Costa.").italic = True

    # CAPÍTULO 3: PRODUTOS E PROPOSTAS DE INTERVENÇÃO (Mínimo dobro de artigos: >= 4 PTTs)
    doc.add_page_break()
    add_cap_title("CAPÍTULO 3 – PRODUTOS E PROPOSTAS DE INTERVENÇÃO")
    add_sec_title("3.1 CARTEIRA DE PRODUTOS TÉCNICOS E TECNOLÓGICOS")
    add_body_p("Apresentação dos produtos vinculados com fichas técnicas estruturadas de 22 itens conforme a Resolução 007/2025.")

    # CAPÍTULO 4: CONSIDERAÇÕES FINAIS
    doc.add_page_break()
    add_cap_title("CAPÍTULO 4 – CONSIDERAÇÕES FINAIS E RECOMENDAÇÕES")
    add_sec_title("4.1 CONSIDERAÇÕES FINAIS")
    add_body_p("Síntese dos resultados alcançados em articulação direta com os objetivos específicos propostos.")
    add_sec_title("4.2 RECOMENDAÇÕES PARA TRABALHOS FUTUROS")
    add_body_p("Prospecções metodológicas para expansão a outras forças de segurança pública e integração operacional contínua.")

    # REFERÊNCIAS
    doc.add_page_break()
    p_rt = doc.add_paragraph()
    p_rt.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_rt = p_rt.add_run("REFERÊNCIAS\n")
    r_rt.bold = True
    r_rt.font.size = Pt(12)

    doc.save(caminho_saida)