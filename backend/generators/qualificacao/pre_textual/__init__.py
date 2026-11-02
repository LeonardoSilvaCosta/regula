"""Pacote dos Elementos Pré-Textuais da Qualificação (Resolução nº 009/2025)."""
from .capa import build_capa
from .folha_rosto import build_folha_rosto
from .folha_aprovacao import build_folha_aprovacao
from .listas_ilustracoes import build_lista_ilustracoes
from .listas_siglas import build_lista_siglas
from .listas_simbolos import build_lista_simbolos
from .sumario import build_sumario

def build_todos_pre_textuais(doc, metadata, assets_dir="assets"):
    """
    Executa a montagem encadeada de todos os elementos pré-textuais na ordem da Resolução 009/2025:
      1. Capa
      2. Folha de Rosto
      3. Folha de Aprovação
      4. Lista de Ilustrações (Figuras, Gráficos, Quadros e Tabelas)
      5. Lista de Abreviaturas e Siglas
      6. Lista de Símbolos (se houver)
      7. Sumário
    O relatório completo, com corpo e campos de página, é montado por builder.py.
    """
    from ..legendas import (
        BM_QUADRO_1,
        BM_QUADRO_2,
        BM_TABELA_1,
        BM_TABELA_2,
        LEGENDA_TABELA_1,
        LEGENDA_TABELA_2,
        legenda_quadro_1,
        legenda_quadro_2,
    )

    build_capa(doc, metadata, assets_dir=assets_dir)
    build_folha_rosto(doc, metadata, assets_dir=assets_dir)
    build_folha_aprovacao(doc, metadata, assets_dir=assets_dir)
    nivel = metadata.get("nivel", "mestrado")
    parte = "continua" if str(nivel).lower() in ("doutorado", "tese") else None
    build_lista_ilustracoes(doc, [
        (legenda_quadro_1(metadata), BM_QUADRO_1),
        (legenda_quadro_2(nivel, parte), BM_QUADRO_2),
        (LEGENDA_TABELA_1, BM_TABELA_1),
        (LEGENDA_TABELA_2, BM_TABELA_2),
    ])
    build_lista_siglas(doc, metadata.get("siglas", []))

    if metadata.get("simbolos"):
        build_lista_simbolos(doc, metadata)

    build_sumario(doc, {"metadata": metadata, "projeto": metadata.get("projeto", {}), "resultados": {}})

# Alias para manter compatibilidade com chamadas antigas do builder.py
build_pre_textual = build_todos_pre_textuais