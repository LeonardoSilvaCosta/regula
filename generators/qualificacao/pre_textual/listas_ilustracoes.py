"""
Lista de ilustrações, uma por designação.
As páginas são campos PAGEREF apontando para as legendas do corpo.
"""

from core.campos import adicionar_linha_indice
from ..estrutura import agrupar_ilustracoes
from ..formato import adicionar_titulo_lista


def build_lista_ilustracoes(doc, ilustracoes_data, quebrar=False):
    """
    ilustracoes_data: lista de (legenda, bookmark).
    Devolve os títulos emitidos, na ordem, para o sumário.
    """
    grupos = agrupar_ilustracoes(_extrair_entradas(ilustracoes_data))
    if not grupos:
        return []

    emitidos = []
    for indice, (titulo, bookmark, entradas) in enumerate(grupos):
        if indice > 0 or quebrar:
            doc.add_page_break()
        adicionar_titulo_lista(doc, titulo, bookmark)
        for rotulo, ref in entradas:
            adicionar_linha_indice(doc, rotulo, ref)
        emitidos.append((titulo, bookmark))
    return emitidos


def _extrair_entradas(ilustracoes_data):
    bruto = ilustracoes_data
    if isinstance(ilustracoes_data, dict):
        bruto = ilustracoes_data.get("quadros", ilustracoes_data.get("lista_quadros", []))
    entradas = []
    for item in bruto or []:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            rotulo, ref = item[0], item[1]
            if _parece_bookmark(ref):
                entradas.append((str(rotulo).strip(), str(ref).strip()))
        elif isinstance(item, dict) and item.get("bookmark"):
            entradas.append((str(item.get("titulo", "")).strip(), str(item["bookmark"]).strip()))
    return entradas


def _parece_bookmark(valor):
    texto = str(valor or "").strip()
    if not texto or " " in texto:
        return False
    return texto.startswith("leg_") or texto.startswith("sec_") or texto.startswith("pos_")
