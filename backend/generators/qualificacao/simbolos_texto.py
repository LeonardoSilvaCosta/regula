"""Detecção de notações estatísticas na ordem em que aparecem no texto."""
import re


CATALOGO = (
    ("P10", r"\bP10\b", "Percentil 10"),
    ("P90", r"\bP90\b", "Percentil 90"),
    ("Q1", r"\bQ1\b", "Primeiro quartil"),
    ("Q3", r"\bQ3\b", "Terceiro quartil"),
    ("N", r"(?<![A-Za-zÀ-ÿ])N(?=\s*=)", "Tamanho da população ou da coorte"),
    ("n", r"(?<![A-Za-zÀ-ÿ])n(?=\s*=)", "Tamanho da amostra"),
)

_SIGLA = re.compile(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)?\b")
_IGNORAR_SIGLA = {
    "II", "III", "IV", "VI", "VII", "VIII", "IX", "XI", "XII",
    "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX", "XXI", "XXII",
    "DE", "DO", "DA", "DOS", "DAS", "EM", "NO", "NA", "NOS", "NAS",
    "OS", "AS", "UM", "SE", "LE", "OU", "AO", "AOS", "POR",
}


def _percorrer(obj, acumulado):
    if isinstance(obj, str):
        acumulado.append(obj)
    elif isinstance(obj, dict):
        for valor in obj.values():
            _percorrer(valor, acumulado)
    elif isinstance(obj, (list, tuple)):
        for valor in obj:
            _percorrer(valor, acumulado)


def texto_narrativo(dados):
    partes = []
    for chave in ("apresentacao", "projeto", "resultados"):
        _percorrer(dados.get(chave), partes)
    return "\n".join(partes)


def simbolos_do_documento(dados):
    """Usa a lista informada. Se não houver, detecta notações no texto, na ordem de aparição."""
    informados = (dados.get("metadata") or {}).get("simbolos")
    if informados:
        return list(informados)
    texto = texto_narrativo(dados)
    achados = []
    for simbolo, padrao, significado in CATALOGO:
        encontrado = re.search(padrao, texto)
        if encontrado:
            achados.append((encontrado.start(), simbolo, significado))
    achados.sort(key=lambda item: item[0])
    return [(simbolo, significado) for _, simbolo, significado in achados]


def _linha_em_caixa_alta(texto, inicio):
    """Títulos integralmente em caixa alta não são lista de siglas."""
    ini = texto.rfind("\n", 0, inicio) + 1
    fim = texto.find("\n", inicio)
    if fim < 0:
        fim = len(texto)
    linha = texto[ini:fim]
    letras = [c for c in linha if c.isalpha()]
    if len(letras) < 8:
        return False
    maiusculas = sum(1 for c in letras if c.isupper())
    return maiusculas / len(letras) > 0.85


def siglas_ausentes(dados, lista_siglas):
    """Siglas em caixa alta usadas no corpo e ausentes da lista informada."""
    conhecidas = set()
    for item in lista_siglas or []:
        if isinstance(item, (tuple, list)) and item:
            conhecidas.add(str(item[0]).strip().upper())
        elif isinstance(item, dict):
            conhecidas.add(str(item.get("sigla", "")).strip().upper())
    texto = texto_narrativo(dados)
    usos = {}
    for achado in _SIGLA.finditer(texto):
        sigla = achado.group(0)
        if sigla in _IGNORAR_SIGLA or sigla in conhecidas:
            continue
        if _linha_em_caixa_alta(texto, achado.start()):
            continue
        depois = texto[achado.end(): achado.end() + 6]
        antes = texto[max(0, achado.start() - 1): achado.start()]
        e_citacao = depois.startswith(";") or depois.startswith(",") or depois.startswith(" et")
        if antes == "(" and (";" in depois or "," in depois):
            e_citacao = True
        if not e_citacao:
            usos[sigla] = usos.get(sigla, 0) + 1
    return sorted(usos)
