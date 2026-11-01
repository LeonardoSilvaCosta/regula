"""
Módulo Orquestrador do Projeto de Qualificação: Seções 1 a 6
(Etapa II.2 da Resolução nº 009/2025-PPGSP/UFPA).

Delega a construção técnica e diagramação para os módulos granulares da Parte Textual:
  - Seção 1: textual.consideracoes_gerais (1.1 Introdução a 1.4 Revisão)
  - Seção 2: textual.objetivos (2.1 Geral e 2.2 Específicos)
  - Seção 3: textual.hipoteses (Hipóteses ou Questões Norteadoras)
  - Seção 4: textual.metodologia (4.1 a 4.6 com bifurcação empírica/documental)
  - Seção 5: textual.produtos (Propostas de PTTs com 22 itens normativos da Res. 007/2025)
  - Seção 6: textual.cronograma (Quadros 1 e 2 - 24 meses Mestrado / 48 meses Doutorado)
"""

from .textual.consideracoes_gerais import build_consideracoes_gerais
from .textual.objetivos import build_objetivos
from .textual.hipoteses import build_hipoteses
from .textual.metodologia import build_metodologia
from .textual.produtos import build_produtos
from .textual.cronograma import build_cronograma
from .estrutura import tem_hipotese


def build_projeto_secoes(doc, dados_projeto, nivel="mestrado", numeros=None):
    """
    Renderiza o corpo textual do Projeto de Qualificação.
    A seção arábica é aberta pelo orquestrador, antes da Apresentação.
    """
    numeros = numeros or {}
    ano_trabalho = str(dados_projeto.get("ano", "2026"))

    build_consideracoes_gerais(doc, dados_projeto)
    build_objetivos(doc, dados_projeto)
    if tem_hipotese(dados_projeto):
        build_hipoteses(doc, dados_projeto, numero=numeros.get("hipoteses", 3))
    build_metodologia(doc, dados_projeto, numero=numeros.get("metodologia", 4))
    build_produtos(doc, dados_projeto, numero=numeros.get("produtos", 5))
    build_cronograma(
        doc,
        dados_projeto,
        nivel=nivel,
        ano_referencia=ano_trabalho,
        numero=numeros.get("cronograma", 6),
    )