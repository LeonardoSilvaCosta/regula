"""Referências ABNT NBR 6023:2018 — título, parágrafo, ordem e destaque."""
import re
import unicodedata

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt

from core.campos import ancorar_paragrafo

_RE_ATO = re.compile(
    r"((?:Lei|Decreto-Lei|Decreto|Medida Provisória|Emenda Constitucional)"
    r"\s+n[ºo°.]?\s*[\d.]+,\s*de\s+\d{1,2}\s+de\s+[A-Za-zÀ-ú]+\s+de\s+\d{4})",
    re.IGNORECASE,
)
_RE_APELIDO = re.compile(
    r"(C[oó]digo\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁÉÍÓÚÂÊÔÃÕÇ]+(?:\s+[A-ZÁÉÍÓÚÂÊÔÃÕÇ][\wÁÉÍÓÚÂÊÔÃÕÇ]+)?"
    r"|Constitui[cç][aã]o(?:\s+da\s+Rep[uú]blica)?(?:\s+Federativa\s+do\s+Brasil)?)",
)
_RE_IN = re.compile(r"\bIn:\s*")
_RE_INICIAL = re.compile(r"[A-ZÁÉÍÓÚÂÊÔÃÕÇ]{1,3}\.?")


def titulo_referencias(capitulo=None):
    """REFERÊNCIAS, ou REFERÊNCIAS DO CAPÍTULO N no relatório de qualificação."""
    if capitulo:
        return f"REFERÊNCIAS DO CAPÍTULO {capitulo}"
    return "REFERÊNCIAS"


def adicionar_titulo_referencias(doc, texto="REFERÊNCIAS", bookmark=None):
    """Times 12, negrito, caixa alta, à esquerda, 18 pt antes e 12 pt depois."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after = Pt(12)
    p.paragraph_format.line_spacing = 1.0
    r = p.add_run(str(texto).upper())
    r.bold = True
    r.font.name = "Times New Roman"
    r.font.size = Pt(12)
    ancorar_paragrafo(p, str(texto).upper(), bookmark=bookmark)
    return p


def adicionar_paragrafo_referencia(doc, texto):
    """Parágrafo simples, à esquerda, sem recuo, com 10 pt depois."""
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.left_indent = Pt(0)
    p.paragraph_format.first_line_indent = Pt(0)
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(10)
    escrever_referencia(p, str(texto).strip())
    return p


def ordenar_referencias(referencias):
    """Ordem alfabética ascendente pelo primeiro elemento de entrada."""
    return sorted(referencias or [], key=_chave_ordenacao)


def renderizar_referencias(doc, referencias, titulo="REFERÊNCIAS", bookmark=None):
    adicionar_titulo_referencias(doc, titulo, bookmark=bookmark)
    for ref in ordenar_referencias(referencias):
        if str(ref).strip():
            adicionar_paragrafo_referencia(doc, ref)


def escrever_referencia(paragrafo, texto):
    for parte, negrito in partes_referencia(texto):
        if not parte:
            continue
        run = paragrafo.add_run(parte)
        run.bold = negrito
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)


def partes_referencia(texto):
    """Faixa em negrito conforme o tipo de documento."""
    texto = str(texto or "").strip()
    if not texto:
        return []
    faixa = (
        _faixa_coletanea(texto)
        or _faixa_ato(texto)
        or _faixa_periodico(texto)
        or _faixa_titulo_obra(texto)
    )
    if not faixa:
        return [(texto, False)]
    inicio, fim = faixa
    return [
        (texto[:inicio], False),
        (texto[inicio:fim], True),
        (texto[fim:], False),
    ]


def _chave_ordenacao(item):
    texto = str(item).strip()
    elemento = texto.split(".", 1)[0]
    return _sem_acento(elemento).casefold()


def _sem_acento(texto):
    normalizado = unicodedata.normalize("NFD", texto)
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn")


def _fim_elemento_entrada(texto, inicio=0):
    """Início do título, depois da autoria e de prenomes abreviados."""
    pos = inicio
    while True:
        ponto = texto.find(". ", pos)
        if ponto < 0:
            return None
        if texto[max(inicio, ponto - 6) : ponto].lower().endswith("et al"):
            return ponto + 2
        token = texto[ponto + 2 :].split(" ", 1)[0]
        if _RE_INICIAL.fullmatch(token):
            pos = ponto + 2
            continue
        return ponto + 2


def _fim_titulo(texto, inicio):
    fim = texto.find(". ", inicio)
    if fim < 0:
        fim = len(texto)
    bloco = texto[inicio:fim]
    dois_pontos = bloco.find(":")
    if dois_pontos >= 0:
        return inicio + dois_pontos
    return fim


def _faixa_titulo_obra(texto):
    """Livro, tese, dissertação ou documento oficial: título principal, sem subtítulo."""
    inicio = _fim_elemento_entrada(texto)
    if inicio is None:
        return None
    return inicio, _fim_titulo(texto, inicio)


def _faixa_coletanea(texto):
    """Capítulo: título da coletânea após In:, sem o subtítulo."""
    marca = _RE_IN.search(texto)
    if not marca:
        return None
    inicio = _fim_elemento_entrada(texto, marca.end())
    if inicio is None:
        return None
    return inicio, _fim_titulo(texto, inicio)


def _faixa_periodico(texto):
    """Artigo: nome do periódico imediatamente antes de ', Local, v.'."""
    if _RE_IN.search(texto):
        return None
    for marca in (", v.", ", vol."):
        pos = texto.find(marca)
        if pos < 0:
            continue
        cidade = texto.rfind(",", 0, pos)
        if cidade < 0:
            continue
        inicio = texto.rfind(". ", 0, cidade)
        if inicio < 0:
            continue
        return inicio + 2, cidade
    return None


def _faixa_ato(texto):
    """Lei ou decreto: numeração e data, ou o título oficial da norma."""
    inicio = _fim_elemento_entrada(texto)
    if inicio is None:
        return None
    janela = texto[inicio : inicio + 200]
    apelido = _RE_APELIDO.search(janela)
    if apelido and apelido.start() < 20:
        return inicio + apelido.start(), inicio + apelido.end()
    ato = _RE_ATO.search(janela)
    if ato and ato.start() < 40:
        return inicio + ato.start(), inicio + ato.end()
    return None
