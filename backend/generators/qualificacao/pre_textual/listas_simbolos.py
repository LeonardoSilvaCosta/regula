"""
Lista de símbolos, na ordem em que aparecem no trabalho.
"""

from core.campos import twips_coluna_rotulo
from ..estrutura import BM_LISTA_SIMBOLOS
from ..formato import adicionar_linha_par_alinhado, adicionar_titulo_lista


def _extrair(metadata):
    if isinstance(metadata, dict):
        simbolos_raw = metadata.get("simbolos", [])
    else:
        simbolos_raw = metadata or []
    pares = []
    for item in simbolos_raw:
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            simbolo = str(item[0]).strip()
            significado = str(item[1]).strip()
        elif isinstance(item, str) and ("–" in item or "-" in item):
            delimitador = "–" if "–" in item else "-"
            partes = item.split(delimitador, 1)
            simbolo = partes[0].strip()
            significado = partes[1].strip()
        else:
            simbolo = str(item).strip()
            significado = ""
        if simbolo:
            pares.append((simbolo, significado))
    return pares


def build_lista_simbolos(doc, metadata, quebrar=True):
    pares = _extrair(metadata)
    if not pares:
        return None
    if quebrar:
        doc.add_page_break()

    adicionar_titulo_lista(doc, "LISTA DE SÍMBOLOS", BM_LISTA_SIMBOLOS)
    pos_twips = twips_coluna_rotulo(simbolo for simbolo, _significado in pares)
    for simbolo, significado in pares:
        adicionar_linha_par_alinhado(doc, simbolo, significado, pos_twips)
    return ("LISTA DE SÍMBOLOS", BM_LISTA_SIMBOLOS)
