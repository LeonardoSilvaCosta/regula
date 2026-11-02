"""
Lista de tabelas.
As páginas são campos PAGEREF apontando para as legendas do corpo.
"""

from core.campos import adicionar_linha_indice
from ..estrutura import BM_LISTA_TABELAS
from ..formato import adicionar_titulo_lista


def build_lista_tabelas(doc, tabelas_data, quebrar=True):
    entradas = _extrair_entradas(tabelas_data)
    if not entradas:
        return None
    if quebrar:
        doc.add_page_break()

    adicionar_titulo_lista(doc, "LISTA DE TABELAS", BM_LISTA_TABELAS)
    for rotulo, bookmark in entradas:
        adicionar_linha_indice(doc, rotulo, bookmark)
    return ("LISTA DE TABELAS", BM_LISTA_TABELAS)


def _extrair_entradas(tabelas_data):
    bruto = tabelas_data
    if isinstance(tabelas_data, dict):
        bruto = tabelas_data.get("tabelas", tabelas_data.get("lista_tabelas", []))
    entradas = []
    for item in bruto or []:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            ref = str(item[1]).strip()
            if ref.startswith("leg_") or ref.startswith("sec_"):
                entradas.append((str(item[0]).strip(), ref))
        elif isinstance(item, dict) and item.get("bookmark"):
            entradas.append((str(item.get("titulo", "")).strip(), str(item["bookmark"]).strip()))
    return entradas
