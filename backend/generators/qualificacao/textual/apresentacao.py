"""
Apresentação e Quadro 1 da Resolução nº 009/2025-PPGSP/UFPA.
"""

import re

from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL

from core.xml_utils import aplicar_autoajuste_janela, set_cell_border
from core.campos import adicionar_bookmark
from ..formato import (
    adicionar_lacuna,
    adicionar_paragrafo,
    adicionar_titulo,
    escrever_fonte,
    escrever_legenda_quadro_1,
)
from generators.common.pronome import fonte_construcao
from ..legendas import BM_QUADRO_1, legenda_quadro_1
from ..pre_textual.sumario import registrar_entrada


_COLUNAS = [
    "Título",
    "Objetivo Geral",
    "Objetivos Específicos",
    "Tipo de Produto",
    "Tipo de Estudo",
    "Fontes",
    "Status",
]
# Proporções das colunas do Quadro 1 (pesos relativos; a tabela usa autoajuste à janela).
_LARGURAS = [1731, 2276, 3502, 3121, 1416, 857, 1092]
_ALINHAMENTO = [
    WD_ALIGN_PARAGRAPH.LEFT,
    WD_ALIGN_PARAGRAPH.LEFT,
    WD_ALIGN_PARAGRAPH.LEFT,
    WD_ALIGN_PARAGRAPH.LEFT,
    WD_ALIGN_PARAGRAPH.JUSTIFY,
    WD_ALIGN_PARAGRAPH.CENTER,
    WD_ALIGN_PARAGRAPH.CENTER,
]


def build_apresentacao(doc, dados_apresentacao, metadata):
    titulo = adicionar_titulo(doc, "APRESENTAÇÃO", bookmark="sec_apresentacao")
    registrar_entrada(doc, "APRESENTAÇÃO", 1, "_TOC_APRESENTACAO", titulo)

    texto_percurso = (dados_apresentacao or {}).get("texto_percurso", [])
    if texto_percurso:
        for par in texto_percurso:
            adicionar_paragrafo(doc, par)
    else:
        adicionar_lacuna(
            doc,
            "[ORIENTAÇÃO DE PREENCHIMENTO: A Apresentação é obrigatória segundo o Art. 1º, II, item 1 da Resolução nº 009/2025. "
            "Elabore um texto em perspectiva pessoal abordando o percurso profissional vinculado ao objeto e o percurso acadêmico no curso.]",
        )


_TIPO_ESTUDO = "Qualitativo/Quantitativo Exploratório Descritivo"
_STATUS = "Em produção"
_ROMANOS = (
    "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x",
    "xi", "xii", "xiii", "xiv", "xv", "xvi", "xvii", "xviii", "xix", "xx",
)


def _romano(indice):
    if 1 <= indice <= len(_ROMANOS):
        return _ROMANOS[indice - 1]
    return str(indice)


def _texto_item(item, chave):
    if isinstance(item, dict):
        return str(item.get(chave) or "").strip()
    return str(getattr(item, chave, "") or "").strip()


def _limpar_objetivo(item):
    return re.sub(
        r"^\s*\(?\s*(?:i{1,3}|iv|vi{0,3}|ix|x|\d+)\s*[\).\]]\s*",
        "",
        str(item or "").strip(),
        flags=re.IGNORECASE,
    ).strip()


def _lista_objetivos(objetivos):
    return [texto for texto in (_limpar_objetivo(item) for item in objetivos or []) if texto]


def _indices_vinculo(item):
    """Números (1 = i) dos objetivos específicos atendidos pelo artigo ou produto."""
    bruto = item.get("objetivos") if isinstance(item, dict) else getattr(item, "objetivos", None)
    indices = []
    for valor in bruto or []:
        texto = str(valor).strip().lower().rstrip(".)")
        if texto.isdigit():
            numero = int(texto)
        elif texto in _ROMANOS:
            numero = _ROMANOS.index(texto) + 1
        else:
            continue
        if numero > 0 and numero not in indices:
            indices.append(numero)
    return indices


def _rotulo_artigo(ordem, artigo):
    return f"Artigo {ordem}: {_texto_item(artigo, 'titulo')}"


def _rotulo_ptt(item, numero):
    titulo_item = _texto_item(item, "titulo") or _texto_item(item, "nome")
    subtipo = _texto_item(item, "subtipo") or _texto_item(item, "tipo") or "PTT"
    num = _texto_item(item, "num") or str(numero)
    return f"{subtipo} {num} – {titulo_item}"


def _ficha(item, rotulo, fontes_base):
    return {
        "rotulo": rotulo,
        "estudo": _texto_item(item, "tipo_estudo") or _TIPO_ESTUDO,
        "fontes": _texto_item(item, "fontes") or fontes_base,
        "status": _texto_item(item, "status") or _STATUS,
        "indices": _indices_vinculo(item),
        "texto": _limpar_objetivo(_texto_item(item, "objetivo_especifico")),
    }


def _linhas_produtos(metadata, objetivo_geral, artigos, ptts, fontes_padrao, objetivos=None):
    """Uma linha por artigo ou produto técnico.

    Quando o entregável reúne vários objetivos específicos, eles entram na
    mesma célula, separados por ponto e vírgula, na ordem da seção 2.2.
    """
    titulo = str((metadata or {}).get("titulo") or (metadata or {}).get("titulo_curto") or "").strip()
    objetivo = str(objetivo_geral or "").strip()
    fontes_base = str(fontes_padrao or "").strip() or "SIAC"
    fichas = []
    for ordem, artigo in enumerate(artigos or [], start=1):
        fichas.append(_ficha(artigo, _rotulo_artigo(ordem, artigo), fontes_base))
    for numero, item in enumerate(ptts or [], start=1):
        fichas.append(_ficha(item, _rotulo_ptt(item, numero), fontes_base))

    itens = _lista_objetivos(objetivos)
    if any(ficha["indices"] for ficha in fichas) and itens:
        return _linhas_por_vinculo(titulo, objetivo, fichas, itens)
    return _linhas_por_ordem(titulo, objetivo, fichas, itens)


def _linha(titulo, objetivo, texto_objetivo, ficha):
    return [
        titulo,
        objetivo,
        texto_objetivo,
        ficha["rotulo"],
        ficha["estudo"],
        ficha["fontes"],
        ficha["status"],
    ]


def _texto_objetivos(ficha, itens):
    partes = []
    for indice in sorted(ficha["indices"]):
        if 1 <= indice <= len(itens):
            partes.append(f"({_romano(indice)}) {itens[indice - 1]}")
    return "; ".join(partes)


def _linhas_por_vinculo(titulo, objetivo, fichas, itens):
    vinculadas = [ficha for ficha in fichas if ficha["indices"] and _texto_objetivos(ficha, itens)]
    vinculadas.sort(key=lambda ficha: min(ficha["indices"]))
    linhas = [
        _linha(titulo, objetivo, _texto_objetivos(ficha, itens), ficha)
        for ficha in vinculadas
    ]
    cobertos = {indice for ficha in vinculadas for indice in ficha["indices"]}
    for indice, texto in enumerate(itens, start=1):
        if indice in cobertos:
            continue
        linhas.append(_linha(titulo, objetivo, f"({_romano(indice)}) {texto}", {
            "rotulo": "",
            "estudo": _TIPO_ESTUDO,
            "fontes": "",
            "status": _STATUS,
        }))
    return linhas


def _linhas_por_ordem(titulo, objetivo, fichas, itens):
    """Sem vínculo explícito, cada entregável recebe o objetivo da mesma posição."""
    linhas = []
    for indice, ficha in enumerate(fichas):
        if indice < len(itens):
            texto = f"({_romano(indice + 1)}) {itens[indice]}"
        elif ficha["texto"]:
            texto = f"({_romano(indice + 1)}) {ficha['texto']}"
        else:
            texto = f"({_romano(indice + 1)})"
        linhas.append(_linha(titulo, objetivo, texto, ficha))
    for indice in range(len(fichas), len(itens)):
        linhas.append(_linha(titulo, objetivo, f"({_romano(indice + 1)}) {itens[indice]}", {
            "rotulo": "",
            "estudo": _TIPO_ESTUDO,
            "fontes": "",
            "status": _STATUS,
        }))
    return linhas


def build_quadro_estrutura(
    doc,
    dados_apresentacao,
    metadata,
    objetivo_geral="",
    objetivos_especificos=None,
    ptts=None,
    artigos=None,
    fontes_padrao="",
):
    p_qtit = doc.add_paragraph()
    p_qtit.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_qtit.paragraph_format.space_before = Pt(18)
    p_qtit.paragraph_format.space_after = Pt(4)
    p_qtit.paragraph_format.line_spacing = 1.0
    escrever_legenda_quadro_1(p_qtit, legenda_quadro_1(metadata))
    adicionar_bookmark(p_qtit, BM_QUADRO_1)

    linhas = _linhas_produtos(
        metadata,
        objetivo_geral,
        artigos,
        ptts,
        fontes_padrao,
        objetivos_especificos,
    )
    if not linhas:
        linhas = _preparar_linhas(
            (dados_apresentacao or {}).get("quadro_1") or [],
            metadata,
            objetivo_geral,
        )
    if not linhas:
        adicionar_lacuna(doc, "[Quadro 1 não informado no projeto.]")
        return

    _montar_quadro(doc, linhas)
    mes_ano = str((metadata or {}).get("mes_ano") or (metadata or {}).get("ano") or "2026").strip()
    p_fonte = doc.add_paragraph()
    p_fonte.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_fonte.paragraph_format.space_before = Pt(2)
    p_fonte.paragraph_format.space_after = Pt(18)
    p_fonte.paragraph_format.line_spacing = 1.0
    escrever_fonte(p_fonte, fonte_construcao(metadata, mes_ano))


def _preparar_linhas(linhas, metadata, objetivo_geral=""):
    titulo_dissertacao = (
        ((metadata or {}).get("titulo") or "").strip()
        or ((metadata or {}).get("titulo_curto") or "").strip()
    )
    objetivo = str(objetivo_geral or "").strip()
    prontas = []
    for linha in linhas:
        if not isinstance(linha, (list, tuple)):
            continue
        cols = [str(c).strip() if c is not None else "" for c in linha]
        while len(cols) < 7:
            cols.append("")
        cols = cols[:7]
        if titulo_dissertacao:
            cols[0] = titulo_dissertacao
        if objetivo:
            cols[1] = objetivo
        if any(cols):
            prontas.append(cols)
    return prontas


def _texto_celula(celula, texto, negrito=False, alinhamento=WD_ALIGN_PARAGRAPH.LEFT):
    from generators.common.siglas_texto import texto_com_sigla

    if not negrito:
        texto = texto_com_sigla(celula.part.document, texto)
    celula.text = texto
    celula.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p = celula.paragraphs[0]
    p.style = "Conteúdo de Quadro"
    p.alignment = alinhamento
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    if p.runs:
        p.runs[0].font.name = "Times New Roman"
        p.runs[0].font.size = Pt(10)
        p.runs[0].bold = negrito
    set_cell_border(celula, top={"sz": 4}, bottom={"sz": 4}, left={"sz": 4}, right={"sz": 4})


def _montar_quadro(doc, linhas):
    tabela = doc.add_table(rows=1 + len(linhas), cols=len(_COLUNAS))
    tabela.alignment = WD_TABLE_ALIGNMENT.LEFT
    aplicar_autoajuste_janela(tabela, _LARGURAS)

    for idx, nome in enumerate(_COLUNAS):
        celula = tabela.rows[0].cells[idx]
        _texto_celula(celula, nome, negrito=True, alinhamento=WD_ALIGN_PARAGRAPH.CENTER)

    for r_idx, linha in enumerate(linhas, start=1):
        for c_idx, valor in enumerate(linha):
            celula = tabela.rows[r_idx].cells[c_idx]
            _texto_celula(celula, valor, alinhamento=_ALINHAMENTO[c_idx])

    if len(linhas) > 1:
        _mesclar(tabela, 0, linhas[0][0])
        objetivo = next((linha[1] for linha in linhas if linha[1]), "")
        _mesclar(tabela, 1, objetivo)
        _mesclar_repetidos(tabela, linhas)


def _mesclar_repetidos(tabela, linhas):
    """Entregável compartilhado por objetivos seguidos ocupa uma célula só."""
    inicio = 0
    while inicio < len(linhas):
        rotulo = linhas[inicio][3]
        fim = inicio
        while fim + 1 < len(linhas) and linhas[fim + 1][3] == rotulo and rotulo:
            fim += 1
        if fim > inicio:
            for coluna in (3, 4, 5, 6):
                _mesclar_faixa(tabela, coluna, inicio + 1, fim + 1, linhas[inicio][coluna])
        inicio = fim + 1


def _mesclar_faixa(tabela, coluna, inicio, fim, texto):
    topo = tabela.rows[inicio].cells[coluna]
    for linha in range(inicio + 1, fim + 1):
        topo.merge(tabela.rows[linha].cells[coluna])
    _texto_celula(topo, texto, alinhamento=_ALINHAMENTO[coluna])


def _mesclar(tabela, coluna, texto):
    topo = tabela.rows[1].cells[coluna]
    for linha in range(2, len(tabela.rows)):
        topo.merge(tabela.rows[linha].cells[coluna])
    _texto_celula(topo, texto, alinhamento=_ALINHAMENTO[coluna])
