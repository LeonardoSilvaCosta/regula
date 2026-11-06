"""
Sumário do Relatório de Qualificação (modelo PPGSP/UFPA).

Capa, folha de rosto, folha de aprovação e listas ficam de fora.
Os números de página são campos PAGEREF, atualizados pelo Word ao abrir o arquivo.
"""

import re

from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

from core.campos import adicionar_bookmark, adicionar_campo_pageref
from ..estrutura import itens_do_sumario

# Títulos primários apontam para um marcador exclusivo, além do marcador sec_* já usado no corpo.
_BOOKMARK_TOC = {
    "sec_apresentacao": "_TOC_APRESENTACAO",
    "sec_1": "_TOC_CONSIDERACOES",
    "sec_1_1": "_TOC_INTRODUCAO",
    "sec_2": "_TOC_OBJETIVOS",
    "sec_2_1": "_TOC_OBJETIVO_GERAL",
    "sec_2_2": "_TOC_OBJETIVOS_ESPECIFICOS",
    "sec_metodologia": "_TOC_METODOLOGIA",
    "sec_produtos": "_TOC_PRODUTOS",
    "sec_cronograma": "_TOC_CRONOGRAMA",
    "sec_resultados": "_TOC_RESULTADOS",
    "sec_referencias": "_TOC_REFERENCIAS",
}

_LINHAS_POR_PAGINA = 28

_RE_SUBSECAO = re.compile(r"^\d+\.\d+")
_RE_PRIMARIA_NUM = re.compile(r"^\d+\.\s+\S")
_RE_NUMERO_SUB = re.compile(r"^(\d+(?:\.\d+)+)\.\s+")
_PRIMARIAS_FIXAS = {"APRESENTAÇÃO", "REFERÊNCIAS"}


def build_sumario(doc, dados, apendices=None, anexos=None, listas=None, quebrar=True):
    """Monta o sumário. `listas` permanece na assinatura e não entra no índice."""
    del listas
    if quebrar:
        doc.add_page_break()

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tit.paragraph_format.space_before = Pt(0)
    p_tit.paragraph_format.space_after = Pt(12)
    p_tit.paragraph_format.line_spacing = 1.0

    r_tit = p_tit.add_run("SUMÁRIO")
    r_tit.bold = True
    r_tit.font.name = "Times New Roman"
    r_tit.font.size = Pt(12)

    origem = dados if isinstance(dados, dict) and "projeto" in dados else {"projeto": {}, "resultados": {}}
    itens = itens_do_sumario(origem, apendices, anexos, listas=None)
    if not itens or itens[0][0] != "APRESENTAÇÃO":
        itens = [("APRESENTAÇÃO", "sec_apresentacao")] + [
            item for item in itens if item[0] != "APRESENTAÇÃO"
        ]

    reservas = []
    for rotulo, bookmark in itens:
        titulo = _exibir(rotulo)
        ancora = _BOOKMARK_TOC.get(bookmark, bookmark)
        nivel = 1 if _primaria(titulo) else 2
        reservas.append(_reservar_linha(doc, titulo, ancora, nivel))
    _estado(doc)["reservas"] = reservas

    doc.add_page_break()


def _exibir(rotulo):
    texto = str(rotulo or "").strip()
    texto = _RE_NUMERO_SUB.sub(r"\1 ", texto)
    if texto.upper().startswith("APÊNDICE"):
        return "Apêndice" + texto[len("APÊNDICE"):]
    if texto.upper().startswith("ANEXO"):
        return "Anexo" + texto[len("ANEXO"):]
    return texto


def _primaria(rotulo):
    if rotulo in _PRIMARIAS_FIXAS:
        return True
    if _RE_SUBSECAO.match(rotulo):
        return False
    return bool(_RE_PRIMARIA_NUM.match(rotulo))


def registrar_entrada(doc, titulo, nivel, bookmark, paragraph=None):
    """Registra a entrada e ancora o título. A página é estimada de novo ao fechar o sumário."""
    if paragraph is not None:
        adicionar_bookmark(paragraph, bookmark)
    entradas = _estado(doc)["entradas"]
    entradas[:] = [item for item in entradas if item["bookmark"] != bookmark]
    titulo_limpo = str(titulo or "").strip()
    entradas.append({
        "titulo": titulo_limpo,
        "nivel": nivel,
        "bookmark": bookmark,
        "pagina": pagina_estimada(doc, bookmark),
    })
    catalogo = getattr(doc, "_catalogo", None)
    if catalogo is not None:
        catalogo.registrar_secao(titulo_limpo, catalogo.pagina, nivel, bookmark)


def preencher_sumario(doc):
    """Segunda fase: grava título, PAGEREF e o número estimado nas linhas já reservadas."""
    reservas = _estado(doc).get("reservas") or []
    if not reservas:
        return
    paginas = mapa_de_paginas(doc)
    catalogo = getattr(doc, "_catalogo", None)
    por_catalogo = {}
    if catalogo is not None:
        por_catalogo = {item["bookmark"]: item for item in catalogo.secoes}
    por_bookmark = {item["bookmark"]: item for item in _estado(doc)["entradas"]}
    for reserva in reservas:
        titulo = reserva["titulo"]
        bookmark = reserva["bookmark"]
        registrado = por_catalogo.get(bookmark) or por_bookmark.get(bookmark) or {}
        pagina_resolvida = (
            registrado.get("pagina")
            or paginas.get(bookmark)
            or 1
        )
        _escrever_linha(
            reserva["paragrafo"],
            titulo,
            bookmark,
            pagina_resolvida,
            nivel=registrado.get("nivel", reserva["nivel"]),
        )


def _estado(doc):
    estado = getattr(doc, "_sumario_qualificacao", None)
    if estado is None:
        estado = {"entradas": [], "reservas": []}
        doc._sumario_qualificacao = estado
    return estado


def _reservar_linha(doc, titulo, bookmark, nivel):
    p = doc.add_paragraph()
    _formatar_linha(p)
    return {"paragrafo": p, "titulo": titulo, "bookmark": bookmark, "nivel": nivel}


def _escrever_linha(paragraph, titulo, bookmark, pagina, nivel=1):
    """Título estático, tabulação e PAGEREF com o número estimado como resultado inicial."""
    paragraph.clear()
    apresentacao = bookmark in ("sec_apresentacao", "_TOC_APRESENTACAO")
    r_txt = paragraph.add_run(f"{titulo}\t")
    r_txt.bold = nivel == 1 or _primaria(titulo)
    r_txt.font.name = "Times New Roman"
    r_txt.font.size = Pt(12)
    pagina_resolvida = max(1, int(pagina or 1))
    if apresentacao:
        texto_pagina = _texto_pagina(pagina_resolvida, romana=True)
    else:
        texto_pagina = str(pagina_resolvida)
    adicionar_campo_pageref(
        paragraph,
        bookmark,
        italico=apresentacao,
        formato="roman" if apresentacao else None,
        resultado=texto_pagina,
    )


def _formatar_linha(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.first_line_indent = Pt(0)
    paragraph.paragraph_format.line_spacing = 1.0
    paragraph.paragraph_format.space_before = Pt(0)
    paragraph.paragraph_format.space_after = Pt(3)
    paragraph.paragraph_format.tab_stops.add_tab_stop(
        Inches(6.299),
        WD_TAB_ALIGNMENT.RIGHT,
        WD_TAB_LEADER.DOTS,
    )


def _texto_pagina(pagina, romana=False):
    numero = max(1, int(pagina or 1))
    if not romana:
        return str(numero)
    simbolos = [
        (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"),
    ]
    texto = ""
    for valor, simbolo in simbolos:
        while numero >= valor:
            texto += simbolo
            numero -= valor
    return texto


def pagina_estimada(doc, bookmark):
    return mapa_de_paginas(doc).get(bookmark, 1)


def _sect_pr(child):
    tag = child.tag.split("}")[-1]
    if tag == "sectPr":
        return child
    if tag != "p":
        return None
    p_pr = child.find(qn("w:pPr"))
    if p_pr is None:
        return None
    return p_pr.find(qn("w:sectPr"))


def _tipo_secao(sect):
    tipo = sect.find(qn("w:type"))
    if tipo is None:
        return "nextPage"
    return tipo.get(qn("w:val")) or "nextPage"


def mapa_de_paginas(doc):
    """Página impressa de cada bookmark: quebras explícitas e densidade de parágrafos.

    Cada `sectPr` fecha a seção cujo conteúdo já foi percorrido. `w:start` reinicia
    a numeração impressa (a parte textual recomeça em 1).
    """
    filhos = list(doc.element.body)
    faixas = []
    inicio = 0
    for indice, child in enumerate(filhos):
        sect = _sect_pr(child)
        if sect is None:
            continue
        faixas.append((inicio, indice + 1, sect))
        inicio = indice + 1

    mapa = {}
    pagina_seguinte = 1
    for indice, (comeco, fim, sect) in enumerate(faixas):
        pg = sect.find(qn("w:pgNumType"))
        if pg is not None and pg.get(qn("w:start")):
            pagina = int(pg.get(qn("w:start")))
        else:
            pagina = pagina_seguinte
        linhas = 0
        for child in filhos[comeco:fim]:
            tag = child.tag.split("}")[-1]
            if tag == "p":
                for bm in child.iter(qn("w:bookmarkStart")):
                    nome = bm.get(qn("w:name"))
                    if nome:
                        mapa[nome] = pagina
                texto = "".join(t.text or "" for t in child.iter(qn("w:t")))
                quebras = sum(
                    1 for br in child.iter(qn("w:br")) if br.get(qn("w:type")) == "page"
                )
                if quebras:
                    pagina += quebras
                    linhas = 0
                    continue
                linhas += max(1, (len(texto) + 89) // 90)
            elif tag == "tbl":
                linhas += max(1, len(list(child.iter(qn("w:tr")))))
            while linhas >= _LINHAS_POR_PAGINA:
                linhas -= _LINHAS_POR_PAGINA
                pagina += 1
        if indice + 1 < len(faixas) and _tipo_secao(faixas[indice + 1][2]) in (
            "nextPage",
            "oddPage",
            "evenPage",
        ):
            pagina += 1
        pagina_seguinte = pagina
    return mapa
