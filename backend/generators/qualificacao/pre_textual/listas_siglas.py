"""
Lista de abreviaturas e siglas.
Só é emitida quando o projeto informa ao menos um par.
"""

from core.campos import twips_coluna_rotulo
from ..estrutura import BM_LISTA_SIGLAS
from ..formato import adicionar_linha_par_alinhado, adicionar_titulo_lista


def normalizar_siglas(siglas_data):
    lista_siglas = []
    if isinstance(siglas_data, dict):
        lista_siglas = siglas_data.get("siglas", siglas_data.get("lista_siglas", []))
    elif isinstance(siglas_data, list):
        lista_siglas = siglas_data

    pares = []
    for item in lista_siglas or []:
        if isinstance(item, (tuple, list)) and len(item) >= 2:
            sigla = str(item[0]).strip()
            significado = str(item[1]).strip()
        elif isinstance(item, dict):
            sigla = str(item.get("sigla", "")).strip()
            significado = str(item.get("significado", item.get("descricao", ""))).strip()
        elif isinstance(item, str) and ("–" in item or "-" in item):
            partes = item.replace("–", "-").split("-", 1)
            sigla, significado = partes[0].strip(), partes[1].strip()
        elif isinstance(item, str) and item.strip():
            sigla, significado = item.strip(), ""
        else:
            continue
        if sigla:
            pares.append((sigla, significado))
    pares.sort(key=lambda par: par[0].upper())
    return pares


def build_lista_siglas(doc, siglas_data, quebrar=True):
    pares = normalizar_siglas(siglas_data)
    if not pares:
        return None
    if quebrar:
        doc.add_page_break()

    adicionar_titulo_lista(doc, "LISTA DE ABREVIATURAS E SIGLAS", BM_LISTA_SIGLAS)
    pos_twips = twips_coluna_rotulo(sigla for sigla, _significado in pares)
    for sigla, significado in pares:
        adicionar_linha_par_alinhado(doc, sigla, significado, pos_twips)
    return ("LISTA DE ABREVIATURAS E SIGLAS", BM_LISTA_SIGLAS)
