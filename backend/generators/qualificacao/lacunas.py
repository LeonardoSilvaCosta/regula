"""Relatório das lacunas que o gerador consegue ver e não deve inventar."""
import os
import re

from .legendas import legenda_quadro_1, legenda_quadro_2
from .simbolos_texto import siglas_ausentes, texto_narrativo
from .estrutura import (
    artigo_tem_conteudo,
    artigos_de,
    citacoes_longas,
    nomes_blocos_ausentes,
    texto_problema,
    verbos_repetidos_quadro,
)
_CAMPOS_PRODUTO = (
    "autoria", "tipo", "subtipo", "titulo", "ano", "coautoria",
    "projeto", "financiamento", "financiador", "demanda",
    "impacto", "justificativa_impacto", "inovacao", "justificativa_inovacao",
    "complexidade", "justificativa_complexidade", "validacao", "divulgacao",
    "abrangencia", "publico_usuario",
)
_JUSTIFICATIVAS = (
    "justificativa_impacto",
    "justificativa_inovacao",
    "justificativa_complexidade",
)


def _palavras(texto):
    return re.findall(r"\S+", texto or "")


def coletar_lacunas(dados, siglas, apendices_omitidos, anexos_omitidos):
    achados = []

    def add(codigo, secao, gravidade, regra, encontrado, recomendacao):
        achados.append({
            "codigo": codigo,
            "secao": secao,
            "gravidade": gravidade,
            "regra": regra,
            "encontrado": encontrado,
            "recomendacao": recomendacao,
        })

    metadata = dados.get("metadata") or {}
    titulo = metadata.get("titulo") or ""
    if re.search(r"(?<![A-Za-zÀ-ÿ])pará(?![A-Za-zÀ-ÿ])", titulo):
        add(
            "PRE_001",
            "Capa / folha de rosto",
            "ADVERTENCIA",
            "O subtítulo deve preservar a capitalização de nomes próprios.",
            "A palavra 'pará' aparece em minúscula no título.",
            "Grafar Pará.",
        )
    banca = metadata.get("banca") or []
    if not banca and not (metadata.get("orientador") or "").strip():
        add(
            "PRE_002",
            "Folha de aprovação",
            "ADVERTENCIA",
            "A banca examinadora precisa estar identificada.",
            "Nenhum membro informado.",
            "Informar orientador e demais membros, com titulação e instituição.",
        )
    for membro in banca:
        nome = membro.get("nome") or ""
        instituicao = membro.get("instituicao") or ""
        if "[" in nome or "[" in instituicao:
            add(
                "PRE_002",
                "Folha de aprovação",
                "ADVERTENCIA",
                "Campos provisórios da banca devem ser substituídos antes da versão definitiva.",
                f"{nome} — {instituicao}".strip(" —"),
                "Substituir pelos dados reais da banca. A data pode permanecer em aberto até a aprovação.",
            )

    quadro_1 = legenda_quadro_1(metadata)
    quadro_2 = legenda_quadro_2(metadata.get("nivel"))
    if not quadro_1.startswith("Quadro 1") or not quadro_2.startswith("Quadro 2"):
        add(
            "EST_001",
            "Quadros",
            "ERRO",
            "O quadro da apresentação é o Quadro 1 e o cronograma é o Quadro 2.",
            f"{quadro_1} | {quadro_2}",
            "Renumerar as legendas e usar o mesmo enunciado na lista e no corpo.",
        )
    if "desenvolvidas" in quadro_2.lower():
        add(
            "EST_002",
            "Cronograma",
            "ADVERTENCIA",
            "A lista e o cronograma devem descrever atividades planejadas, com o mesmo texto.",
            quadro_2,
            "Usar 'atividades a serem realizadas'.",
        )

    for indice, produto in enumerate((dados.get("projeto") or {}).get("ptts") or [], start=1):
        faltantes = []
        for campo in _CAMPOS_PRODUTO:
            if campo == "subtipo" and (produto.get("subtipo") or produto.get("subtipo_producao")):
                continue
            if not str(produto.get(campo) or "").strip():
                faltantes.append(campo)
        if faltantes:
            add(
                "PTT_001",
                f"Produto {indice}",
                "ADVERTENCIA",
                "Cada produto deve trazer os campos da ficha prevista na Resolução nº 009/2025, em conjunto com a nº 007/2025.",
                "Ausentes: " + ", ".join(faltantes),
                "Completar a ficha. A área e a linha institucionais são preenchidas pelo modelo.",
            )
        for campo in _JUSTIFICATIVAS:
            texto = str(produto.get(campo) or "")
            quantidade = len(_palavras(texto))
            if quantidade > 50:
                add(
                    "PTT_002",
                    f"Produto {indice}",
                    "ADVERTENCIA",
                    "A justificativa deve ter no máximo 50 palavras.",
                    f"{campo}: {quantidade} palavras.",
                    "Reduzir o texto da justificativa.",
                )

    artigo = {}
    resultados = dados.get("resultados") or {}
    if isinstance(resultados, dict):
        artigo = resultados.get("artigo_1") or resultados.get("artigo_preliminar") or {}
    if not artigo_tem_conteudo(artigo):
        add(
            "PRE_003",
            "Resultados preliminares",
            "ERRO",
            "A seção deve apresentar resultados alcançados.",
            "Não há conteúdo científico informado.",
            "Inserir os resultados já obtidos. O gerador não inventa autores nem texto provisório.",
        )
    autores = str(artigo.get("autores") or "")
    if re.search(r"Autor\s+\d+", autores, flags=re.IGNORECASE):
        add(
            "PRE_004",
            "Resultados preliminares",
            "ADVERTENCIA",
            "Os autores do artigo devem ser os nomes reais.",
            autores,
            "Substituir os marcadores Autor 1, Autor 2 e Autor 3.",
        )

    for rotulo in apendices_omitidos:
        add(
            "POS_001",
            "Apêndice",
            "ADVERTENCIA",
            "Apêndice incluído precisa ter o material anunciado.",
            rotulo,
            "Anexar o conteúdo ou retirar a entrada. O título sem corpo não foi gerado.",
        )
    for rotulo in anexos_omitidos:
        add(
            "POS_002",
            "Anexo",
            "ADVERTENCIA",
            "Anexo incluído precisa ter o material anunciado.",
            rotulo,
            "Anexar o conteúdo ou retirar a entrada. O título sem corpo não foi gerado.",
        )

    ausentes = siglas_ausentes(dados, siglas)
    if ausentes:
        amostra = ", ".join(ausentes[:40])
        add(
            "PRE_005",
            "Lista de abreviaturas e siglas",
            "ADVERTENCIA",
            "A lista deve contemplar as siglas utilizadas no texto.",
            amostra,
            "Incluir a forma por extenso de cada sigla ausente.",
        )

    quadro = (dados.get("apresentacao") or {}).get("quadro_1") or []
    if not quadro:
        add(
            "QUA_001",
            "Quadro 1",
            "ADVERTENCIA",
            "A apresentação deve trazer o Quadro 1.",
            "Nenhuma linha informada.",
            "Informar título, objetivo geral, objetivos específicos, produto, tipo de estudo, fontes e status.",
        )
    repetidos = verbos_repetidos_quadro(quadro)
    if repetidos:
        add(
            "QUA_002",
            "Quadro 1",
            "ADVERTENCIA",
            "Cada objetivo específico do Quadro 1 deve iniciar com um verbo distinto.",
            ", ".join(repetidos),
            "Reescrever os objetivos para que o verbo inicial não se repita.",
        )

    if not (dados.get("projeto") or {}).get("cronograma"):
        add(
            "CRO_001",
            "Cronograma",
            "ADVERTENCIA",
            "O cronograma deve discriminar os meses de cada etapa.",
            "Nenhum mês informado.",
            "Informar os meses de execução. O gerador não preenche um calendário padrão.",
        )

    problema = texto_problema(dados.get("projeto"))
    if "?" not in problema:
        add(
            "RED_001",
            "Problema de pesquisa",
            "ADVERTENCIA",
            "O problema de pesquisa deve ser formulado como pergunta.",
            problema or "Texto não informado.",
            "Formular o problema em forma de pergunta, articulada à introdução.",
        )

    narrativa = texto_narrativo(dados)
    if re.search(r"\bapud\b", narrativa, flags=re.IGNORECASE):
        add(
            "RED_002",
            "Revisão da literatura",
            "ADVERTENCIA",
            "A resolução pede para evitar apud e priorizar a fonte primária.",
            "O texto contém apud.",
            "Citar a fonte primária.",
        )
    longas = citacoes_longas(narrativa)
    if longas:
        add(
            "RED_003",
            "Corpo do trabalho",
            "ADVERTENCIA",
            "Citações diretas com mais de três linhas devem ser evitadas.",
            longas[0],
            "Substituir a citação longa por síntese.",
        )

    for indice, artigo in enumerate(artigos_de(dados.get("resultados")), start=1):
        if not artigo_tem_conteudo(artigo):
            continue
        faltam = nomes_blocos_ausentes(artigo)
        if faltam:
            add(
                "RES_001",
                f"Resultados preliminares / produto {indice}",
                "ADVERTENCIA",
                "O manuscrito deve conter resumo, introdução, metodologia, resultados parciais e referências.",
                "Ausentes: " + ", ".join(faltam),
                "Completar os blocos ausentes. O gerador não redige o manuscrito.",
            )

    return achados


def emitir_lacunas(caminho_saida, achados):
    if achados:
        linhas = []
        for item in achados:
            linhas.append(
                f"[{item['gravidade']}] {item['codigo']} | {item['secao']}\n"
                f"  Regra: {item['regra']}\n"
                f"  Encontrado: {item['encontrado']}\n"
                f"  Recomendação: {item['recomendacao']}"
            )
        texto = "\n".join(linhas)
    else:
        texto = "Nenhuma lacuna automática identificada."

    print("\n--- Lacunas de conformidade ---")
    print(texto)
    destino = os.path.splitext(caminho_saida)[0] + ".lacunas.txt"
    with open(destino, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto + "\n")
    print(f"\n[LACUNAS] {destino}")
    return destino
