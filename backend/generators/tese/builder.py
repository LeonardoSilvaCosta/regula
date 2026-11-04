"""Montador da Tese de Doutorado conforme a Resolução nº 010/2025-PPGSP/UFPA."""
import docx
from docx.shared import Cm, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

from core.styles import apply_base_styles, set_page_margins, insert_brasao, insert_cabecalho_institucional
from generators.common.referencias import renderizar_referencias
from generators.qualificacao.parser import parse_projeto_docx
from core.xml_utils import add_page_number_field, configure_section_page_numbers

def _dados_sem_arquivo(metadata, revisao):
    """Documento montado só com metadata e seções revisadas, sem .docx de origem."""
    revisao = revisao or {}
    secoes = revisao.get("sections") or {}
    return {
        "metadata": dict(metadata or revisao.get("metadata") or {}),
        "apresentacao": {"texto_percurso": list(secoes.get("apresentacao") or [])},
        "referencias": list(secoes.get("referencias") or []),
        "secoes": [],
    }


def gerar_documento_tese(
    caminho_entrada,
    caminho_saida,
    assets_dir="assets",
    metadata=None,
    revisao=None,
):
    """
    Estrutura de Tese de Doutorado:
    - Mesma estrutura de 4 capítulos da dissertação.
    - Exigência ampliada de 04 artigos científicos no Capítulo 2.
    - Exigência ampliada de no mínimo 08 Produtos Técnicos e Tecnológicos (PTTs) no Capítulo 3.
    """
    doc = docx.Document()
    apply_base_styles(doc)

    if caminho_entrada is None:
        dados = _dados_sem_arquivo(metadata, revisao)
    else:
        dados = parse_projeto_docx(caminho_entrada)
    revisado = metadata or (revisao or {}).get("metadata") or {}
    extraido = dados.get("metadata") or {}

    def campo(chave):
        return (revisado.get(chave) or extraido.get(chave) or "").strip()

    titulo_trabalho = campo("titulo")
    autor = campo("autor")
    orientador = campo("orientador")
    coorientador = campo("coorientador")
    ano = campo("ano")
    local = campo("local")
    area = campo("area_concentracao")
    linha = campo("linha_pesquisa")
    linha_orientacao = f"Orientador(a): {orientador}\n"
    if coorientador:
        linha_orientacao += f"Coorientador(a): {coorientador}\n"

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
    r_loc = p_loc.add_run(f"{local}\n{ano}")
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
        f"Área de Concentração: {area}.\n"
        f"Linha de Pesquisa: {linha}.\n"
        f"{linha_orientacao}"
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

    secoes = list(dados.get("secoes") or [])
    if not secoes:
        for paragrafo in (dados.get("apresentacao") or {}).get("texto_percurso") or []:
            add_body_p(paragrafo)
    for secao in secoes:
        add_sec_title(secao.get("titulo") or "Seção")
        for paragrafo in secao.get("paragrafos") or []:
            add_body_p(paragrafo)
    referencias = dados.get("referencias") or []
    if referencias:
        doc.add_page_break()
        renderizar_referencias(doc, referencias, titulo="REFERÊNCIAS", bookmark="sec_referencias")

    doc.save(caminho_saida)