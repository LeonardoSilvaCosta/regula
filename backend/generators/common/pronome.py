"""Flexão de autor/autora a partir do pronome informado no formulário."""


def genero(meta):
    valor = str((meta or {}).get("pronome") or "").strip().lower()
    if valor in {"ela", "ela/dela", "dela"}:
        return "ela"
    if valor in {"ele", "ele/dele", "dele"}:
        return "ele"
    return ""


def fonte_elaborado(ano, meta):
    if genero(meta) == "ela":
        return f"Fonte: Elaborado pela autora, {ano}."
    if genero(meta) == "ele":
        return f"Fonte: Elaborado pelo autor, {ano}."
    return f"Fonte: Elaborado pelo(a) autor(a), {ano}."


def fonte_construcao(meta, complemento=""):
    if genero(meta) == "ela":
        nucleo = "Construção da autora"
    elif genero(meta) == "ele":
        nucleo = "Construção do autor"
    else:
        nucleo = "Construção do(a) autor(a)"
    resto = str(complemento or "").strip()
    if resto:
        return f"Fonte: {nucleo}. {resto}."
    return f"{nucleo}."


def do_autor(meta):
    if genero(meta) == "ela":
        return "da autora"
    if genero(meta) == "ele":
        return "do autor"
    return "do(a) autor(a)"
