"""Campos de página, marcadores e tabulação pontilhada do Word."""
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt

_bookmark_seq = 0

BOOKMARKS_TITULO = {
    "APRESENTAÇÃO": "sec_apresentacao",
    "1. CONSIDERAÇÕES GERAIS": "sec_1",
    "1.1. INTRODUÇÃO": "sec_1_1",
    "1.2. JUSTIFICATIVA": "sec_1_2",
    "1.3. PROBLEMA DE PESQUISA": "sec_1_3",
    "1.4. REVISÃO DA LITERATURA / REFERENCIAL TEÓRICO": "sec_1_4",
    "2. OBJETIVOS": "sec_2",
    "2.1. OBJETIVO GERAL": "sec_2_1",
    "2.2. OBJETIVOS ESPECÍFICOS": "sec_2_2",
    "3. HIPÓTESE / QUESTÃO NORTEADORA": "sec_3",
    "4. METODOLOGIA": "sec_4",
    "4.1. NATUREZA DA PESQUISA": "sec_4_1",
    "4.2. LÓCUS": "sec_4_2",
    "4.3. PARTICIPANTES E COORTE POPULACIONAL": "sec_4_3",
    "4.3. FONTES DE DADOS": "sec_4_3",
    "4.4. PROCEDIMENTOS DE COLETA": "sec_4_4",
    "4.5. PROCEDIMENTOS ÉTICOS": "sec_4_5",
    "4.6. ANÁLISE DE DADOS": "sec_4_6",
    "5. PROPOSTA DE PRODUTOS": "sec_5",
    "6. CRONOGRAMA": "sec_6",
    "7. RESULTADOS PRELIMINARES": "sec_7",
    "REFERÊNCIAS": "sec_referencias",
}


def adicionar_bookmark(paragraph, nome):
    """Insere bookmarkStart/End no parágrafo para PAGEREF."""
    global _bookmark_seq
    _bookmark_seq += 1
    ident = str(_bookmark_seq)
    inicio = OxmlElement("w:bookmarkStart")
    inicio.set(qn("w:id"), ident)
    inicio.set(qn("w:name"), nome)
    fim = OxmlElement("w:bookmarkEnd")
    fim.set(qn("w:id"), ident)
    p_pr = paragraph._p.find(qn("w:pPr"))
    if p_pr is not None:
        p_pr.addnext(inicio)
    else:
        paragraph._p.insert(0, inicio)
    paragraph._p.append(fim)


def ancorar_paragrafo(paragraph, texto, bookmark=None):
    """Marca o parágrafo se o texto for um título conhecido ou se o nome for explícito."""
    nome = bookmark or BOOKMARKS_TITULO.get((texto or "").strip())
    if nome:
        adicionar_bookmark(paragraph, nome)


def _run_times(tamanho_meio_pontos="24", italico=False):
    run = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    fontes = OxmlElement("w:rFonts")
    fontes.set(qn("w:ascii"), "Times New Roman")
    fontes.set(qn("w:hAnsi"), "Times New Roman")
    fontes.set(qn("w:cs"), "Times New Roman")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), tamanho_meio_pontos)
    sz_cs = OxmlElement("w:szCs")
    sz_cs.set(qn("w:val"), tamanho_meio_pontos)
    rpr.append(fontes)
    rpr.append(sz)
    rpr.append(sz_cs)
    if italico:
        ital = OxmlElement("w:i")
        rpr.append(ital)
        ital_cs = OxmlElement("w:iCs")
        rpr.append(ital_cs)
    run.append(rpr)
    return run


def adicionar_campo_pageref(paragraph, bookmark, italico=False, formato=None):
    """Campo PAGEREF. O Word recalcula a página ao abrir o arquivo.

    `formato` é um comutador do Word (ex.: ``roman`` para algarismos minúsculos).
    """
    r_inicio = _run_times(italico=italico)
    fld_inicio = OxmlElement("w:fldChar")
    fld_inicio.set(qn("w:fldCharType"), "begin")
    fld_inicio.set(qn("w:dirty"), "true")
    r_inicio.append(fld_inicio)

    r_instr = _run_times(italico=italico)
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    comando = f" PAGEREF {bookmark} \\h "
    if formato:
        comando = f" PAGEREF {bookmark} \\h \\* {formato} "
    instr.text = comando
    r_instr.append(instr)

    r_sep = _run_times(italico=italico)
    fld_sep = OxmlElement("w:fldChar")
    fld_sep.set(qn("w:fldCharType"), "separate")
    r_sep.append(fld_sep)

    r_texto = _run_times(italico=italico)
    texto = OxmlElement("w:t")
    texto.text = "0"
    r_texto.append(texto)

    r_fim = _run_times(italico=italico)
    fld_fim = OxmlElement("w:fldChar")
    fld_fim.set(qn("w:fldCharType"), "end")
    r_fim.append(fld_fim)

    for elemento in (r_inicio, r_instr, r_sep, r_texto, r_fim):
        paragraph._p.append(elemento)


def aplicar_tabulacao_coluna(paragraph, pos_twips):
    """Tabulação à esquerda, sem líder, para alinhar o texto por extenso."""
    p_pr = paragraph._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "left")
    tab.set(qn("w:pos"), str(int(pos_twips)))
    tabs.append(tab)
    p_pr.append(tabs)


def twips_coluna_rotulo(rotulos):
    """Coluna larga o bastante para o maior rótulo + cerca de quatro espaços."""
    n = max((len(str(rotulo or "")) for rotulo in rotulos), default=4)
    return n * 160 + 240


def aplicar_tabulacao_pontilhada(paragraph, pos_twips="9072"):
    """Tabulação à direita com pontilhado, na largura útil da página A4 (16 cm)."""
    p_pr = paragraph._p.get_or_add_pPr()
    tabs = OxmlElement("w:tabs")
    tab = OxmlElement("w:tab")
    tab.set(qn("w:val"), "right")
    tab.set(qn("w:leader"), "dot")
    tab.set(qn("w:pos"), str(pos_twips))
    tabs.append(tab)
    p_pr.append(tabs)


def adicionar_linha_indice(doc, rotulo, bookmark):
    """Linha de lista ou sumário: título, pontilhado e campo de página."""
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    aplicar_tabulacao_pontilhada(p)

    r_txt = p.add_run(str(rotulo).strip())
    r_txt.font.name = "Times New Roman"
    r_txt.font.size = Pt(12)

    r_tab = p.add_run("\t")
    r_tab.font.name = "Times New Roman"
    r_tab.font.size = Pt(12)

    adicionar_campo_pageref(p, bookmark)
    return p


def habilitar_atualizacao_de_campos(doc):
    """Pede ao Word que atualize PAGE e PAGEREF ao abrir o documento."""
    settings = doc.settings.element
    update = settings.find(qn("w:updateFields"))
    if update is None:
        update = OxmlElement("w:updateFields")
        settings.append(update)
    update.set(qn("w:val"), "true")
