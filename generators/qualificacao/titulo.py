"""Separação de título e subtítulo conforme a Resolução nº 009/2025."""
from docx.shared import Pt


_PREFIXOS_TITULACAO = (
    "Prof. Dra.",
    "Profa. Dra.",
    "Prof. Dr.",
    "Profa. Dr.",
    "Prof.",
    "Profa.",
    "Dra.",
    "Dr.",
    "Me.",
    "Ma.",
)


def separar_titulo_subtitulo(titulo_completo):
    """
    Título principal em caixa alta.
    Subtítulo em estilo frase: só a primeira letra é forçada a maiúscula.
    O restante permanece como veio no texto, para preservar nomes próprios e siglas.
    """
    if not titulo_completo:
        return "", ""
    texto = str(titulo_completo).strip()
    if ":" not in texto:
        return texto.upper(), ""
    principal, sub = texto.split(":", 1)
    principal = principal.strip().upper()
    sub = sub.strip()
    if sub:
        sub = sub[0].upper() + sub[1:]
    return principal, sub


def escrever_titulo_e_subtitulo(paragraph, titulo_completo, tamanho=14):
    """Escreve título e subtítulo no parágrafo, ambos em negrito."""
    tit, sub = separar_titulo_subtitulo(titulo_completo)
    if not tit and not sub:
        return False
    r_tit = paragraph.add_run(tit)
    r_tit.bold = True
    r_tit.font.name = "Times New Roman"
    r_tit.font.size = Pt(tamanho)
    if sub:
        r_sep = paragraph.add_run(": ")
        r_sep.bold = True
        r_sep.font.name = "Times New Roman"
        r_sep.font.size = Pt(tamanho)
        r_sub = paragraph.add_run(sub)
        r_sub.bold = True
        r_sub.font.name = "Times New Roman"
        r_sub.font.size = Pt(tamanho)
    return True


_PARTICULAS = {"da", "de", "do", "das", "dos", "e"}


def nome_discente(nome):
    """Caixa baixa com iniciais maiúsculas quando o nome veio inteiro em caixa alta."""
    texto = (nome or "").strip()
    letras = [caractere for caractere in texto if caractere.isalpha()]
    if not texto or not letras or any(caractere.islower() for caractere in letras):
        return texto
    partes = []
    for indice, token in enumerate(texto.split()):
        pedacos = []
        for ordem, pedaco in enumerate(token.split("-")):
            baixo = pedaco.lower()
            if indice > 0 and ordem == 0 and baixo in _PARTICULAS:
                pedacos.append(baixo)
            else:
                pedacos.append(baixo.capitalize() if pedaco else pedaco)
        partes.append("-".join(pedacos))
    return " ".join(partes)


def separar_titulacao(nome):
    """Separa 'Prof. Dr.' do nome próprio. Devolve (nome, titulacao)."""
    texto = (nome or "").strip()
    if not texto:
        return "", ""
    for prefixo in _PREFIXOS_TITULACAO:
        if texto.lower().startswith(prefixo.lower()):
            resto = texto[len(prefixo):].strip(" .")
            return (resto or texto), texto[: len(prefixo)].strip()
    return texto, ""
