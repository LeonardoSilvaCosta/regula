"""Primeira ocorrência por extenso; as seguintes ficam só com a sigla."""
import re


def _limite_sigla(sigla):
    return (
        r"(?<![A-Za-zÀ-ÿ0-9/])"
        + re.escape(sigla)
        + r"(?![A-Za-zÀ-ÿ0-9/])"
    )


def _ocorrencias(texto, sigla, significado, inicio):
    """Forma expandida, sigla isolada e nome por extenso, a partir de `inicio`."""
    expandidos = list(
        re.finditer(
            re.escape(significado) + r"\s*\(\s*" + re.escape(sigla) + r"\s*\)",
            texto[inicio:],
            flags=re.IGNORECASE,
        )
    )
    siglas = list(re.finditer(_limite_sigla(sigla), texto[inicio:]))
    nomes = list(
        re.finditer(
            r"(?<![A-Za-zÀ-ÿ])" + re.escape(significado) + r"(?![A-Za-zÀ-ÿ])",
            texto[inicio:],
            flags=re.IGNORECASE,
        )
    )
    achados = []
    for match in expandidos:
        achados.append((inicio + match.start(), inicio + match.end(), "expandida", match.group(0)))
    for match in siglas:
        achados.append((inicio + match.start(), inicio + match.end(), "sigla", match.group(0)))
    for match in nomes:
        achados.append((inicio + match.start(), inicio + match.end(), "nome", match.group(0)))
    return achados


def normalizar_siglas_texto(texto, pares, introduzidas):
    if not texto or not pares:
        return texto
    ordenados = sorted(pares, key=lambda par: len(par[1]), reverse=True)
    cursor = 0
    partes = []
    while cursor < len(texto):
        escolhido = None
        for sigla, significado in ordenados:
            if not significado:
                continue
            for inicio, fim, tipo, trecho in _ocorrencias(texto, sigla, significado, cursor):
                if escolhido is None or inicio < escolhido[0] or (
                    inicio == escolhido[0] and fim - inicio > escolhido[1] - escolhido[0]
                ):
                    escolhido = (inicio, fim, tipo, trecho, sigla, significado)
        if escolhido is None:
            partes.append(texto[cursor:])
            break
        inicio, fim, tipo, trecho, sigla, significado = escolhido
        chave = sigla.upper()
        ja_introduzida = bool(introduzidas.get(chave))
        parentese = re.match(r"\s*\(([^)]*)\)", texto[fim:])
        sigla_no_parentese = bool(
            parentese
            and re.search(
                r"(?<![A-Za-zÀ-ÿ0-9])" + re.escape(sigla) + r"(?![A-Za-zÀ-ÿ0-9])",
                parentese.group(1),
            )
        )
        if tipo == "nome" and sigla_no_parentese:
            fim += parentese.end()
            tipo = "expandida"
            trecho = texto[inicio:fim]
        partes.append(texto[cursor:inicio])
        composto = parentese.group(1).strip() if parentese and "/" in parentese.group(1) else ""
        if tipo == "expandida" and ja_introduzida:
            partes.append(composto or sigla)
        elif tipo == "expandida":
            partes.append(trecho)
        elif tipo == "sigla" and not ja_introduzida:
            partes.append(f"{significado} ({sigla})")
        elif tipo == "sigla":
            partes.append(trecho)
        elif not ja_introduzida:
            partes.append(f"{trecho} ({sigla})")
        else:
            partes.append(sigla)
        introduzidas[chave] = True
        cursor = fim
    return "".join(partes)


class ControleSiglas:
    def __init__(self, pares):
        self.pares = list(pares or [])
        self.introduzidas = {sigla.upper(): False for sigla, _ in self.pares}

    def aplicar(self, texto):
        if not isinstance(texto, str) or not texto:
            return texto
        return normalizar_siglas_texto(texto, self.pares, self.introduzidas)


def ativar_siglas(doc, pares):
    doc._controle_siglas = ControleSiglas(pares)


def texto_com_sigla(doc, texto):
    controle = getattr(doc, "_controle_siglas", None)
    if controle is None or texto is None:
        return texto
    return controle.aplicar(str(texto))
