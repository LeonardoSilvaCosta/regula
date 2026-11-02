"""Extrai seções, metadados e tabelas do .docx enviado pelo usuário."""

import os
import re
import unicodedata

import docx
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


_RE_NUMERO = re.compile(r"^(?:cap[ií]tulo\s+)?\d+(?:\.\d+)*\s*[-–.)]?\s*", re.IGNORECASE)
_RE_ROTULO = re.compile(r"^(?P<chave>[^:]{2,40}):\s*(?P<valor>.+)$")
_RE_SIGLA = re.compile(r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9]{2,12})\s*[-–:]\s+(.+)$")
_RE_ANO = re.compile(r"\b(19|20)\d{2}\b")
_RE_SUBITEM_PTT = re.compile(r"^(?:\d+\.\d+\b|ptt\s*\d+\b|produto\s*\d+\b)", re.IGNORECASE)

_ROTULOS_META = {
    "titulo": "titulo",
    "título": "titulo",
    "autor": "autor",
    "autora": "autor",
    "orientador": "orientador",
    "orientadora": "orientador",
    "coorientador": "coorientador",
    "coorientadora": "coorientador",
    "coordenador": "coordenador",
    "coordenadora": "coordenador",
    "ano": "ano",
    "local": "local",
    "area de concentracao": "area_concentracao",
    "área de concentração": "area_concentracao",
    "linha de pesquisa": "linha_pesquisa",
}

_CAMPOS_PTT = {
    "titulo": "titulo",
    "título": "titulo",
    "autoria": "autoria",
    "tipo": "tipo",
    "subtipo": "subtipo",
    "ano": "ano",
    "coautoria": "coautoria",
    "projeto": "projeto",
    "financiamento": "financiamento",
    "financiador": "financiador",
    "demanda": "demanda",
    "impacto": "impacto",
    "justificativa do impacto": "justificativa_impacto",
    "inovacao": "inovacao",
    "inovação": "inovacao",
    "justificativa da inovacao": "justificativa_inovacao",
    "justificativa da inovação": "justificativa_inovacao",
    "complexidade": "complexidade",
    "justificativa da complexidade": "justificativa_complexidade",
    "validacao": "validacao",
    "validação": "validacao",
    "divulgacao": "divulgacao",
    "divulgação": "divulgacao",
    "abrangencia": "abrangencia",
    "abrangência": "abrangencia",
    "publico usuario": "publico_usuario",
    "público usuário": "publico_usuario",
    "publico-alvo": "publico_usuario",
}

# Ordem: rótulos mais específicos antes dos genéricos.
_SECOES = [
    (("apresenta",), "apresentacao"),
    (("introdu",), "introducao"),
    (("justific",), "justificativa"),
    (("problema",), "problema"),
    (("revis", "referencial", "estado da arte"), "revisao"),
    (("objetivo geral",), "objetivo_geral"),
    (("objetivos especific", "objetivo especific"), "objetivos_especificos"),
    (("hipotese", "hipoteses", "questao norteadora", "questoes norteadoras"), "hipotese"),
    (("natureza da pesquisa", "natureza"), "metodologia_natureza"),
    (("locus",), "metodologia_locus"),
    (("participant", "coorte", "amostra"), "metodologia_participantes"),
    (("fontes de dados", "fonte de dados", "fontes"), "metodologia_fontes"),
    (("coleta",), "metodologia_coleta"),
    (("etica", "éticos", "eticos"), "metodologia_etica"),
    (("analise de dados", "análise de dados", "modelagem"), "metodologia_analise"),
    (("metodolog",), "metodologia"),
    (("cronograma",), "cronograma"),
    (("resultado",), "resultados"),
    (("referenc",), "referencias"),
    (("sigla", "abreviatur"), "siglas"),
    (("apendice",), "apendices"),
    (("anexo",), "anexos"),
    (("produto", "ptt"), "ptts"),
    (("objetivo",), "objetivos"),
]


def _sem_acento(texto):
    base = unicodedata.normalize("NFKD", texto or "")
    return "".join(ch for ch in base if not unicodedata.combining(ch)).lower()


def _titulo_limpo(texto):
    return _RE_NUMERO.sub("", (texto or "").strip()).strip(" .:-")


def _classificar(texto):
    limpo = _sem_acento(_titulo_limpo(texto))
    if not limpo or len(limpo) > 140:
        return None
    for chaves, nome in _SECOES:
        if any(chave in limpo for chave in chaves):
            return nome
    return None


def _e_titulo(paragrafo):
    texto = paragrafo.text.strip()
    if not texto or len(texto) > 180:
        return False
    estilo = (paragrafo.style.name or "") if paragrafo.style is not None else ""
    if estilo.lower().startswith("heading") or estilo.lower().startswith("título") or estilo.lower().startswith("titulo"):
        return True
    if texto.endswith((".", "?", "!")) or len(texto.split()) > 14:
        return False
    if _RE_NUMERO.match(texto) and len(texto) < 120:
        return True
    letras = [ch for ch in texto if ch.isalpha()]
    if letras and texto == texto.upper() and len(texto) < 80:
        return True
    return bool(_classificar(texto)) and len(texto) <= 80


def _iterar_blocos(documento):
    for filho in documento.element.body:
        if filho.tag == qn("w:p"):
            yield ("p", Paragraph(filho, documento))
        elif filho.tag == qn("w:tbl"):
            yield ("t", Table(filho, documento))


def _matriz(tabela):
    linhas = []
    for row in tabela.rows:
        linhas.append([cell.text.strip() for cell in row.cells])
    return [linha for linha in linhas if any(celula.strip() for celula in linha)]


def _e_subitem_ptt(texto):
    """Subitem do item 5, como 5.1 ou PTT 1. O título da seção não conta."""
    return bool(_RE_SUBITEM_PTT.match(_sem_acento(texto or "").strip()))


def _ptt_vazio(nome, indice):
    return {
        "num": str(indice),
        "nome": nome,
        "autoria": "",
        "tipo": "",
        "subtipo": "",
        "titulo": nome,
        "ano": "",
        "coautoria": "",
        "projeto": "",
        "financiamento": "",
        "financiador": "",
        "demanda": "",
        "impacto": "",
        "justificativa_impacto": "",
        "inovacao": "",
        "justificativa_inovacao": "",
        "complexidade": "",
        "justificativa_complexidade": "",
        "validacao": "",
        "divulgacao": "",
        "abrangencia": "",
        "publico_usuario": "",
    }


def _aplicar_linha_ptt(ptt, texto):
    casado = _RE_ROTULO.match(texto.strip())
    if not casado:
        return False
    chave = _sem_acento(casado.group("chave").strip())
    destino = _CAMPOS_PTT.get(chave)
    if not destino:
        return False
    ptt[destino] = casado.group("valor").strip()
    return True


def _atividades_cronograma(paragrafos, tabela):
    atividades = []
    if tabela:
        for linha in tabela:
            nome = (linha[0] if linha else "").strip()
            if not nome or _sem_acento(nome) in ("atividade", "etapa", "cronograma"):
                continue
            atividades.append((nome, []))
    for texto in paragrafos:
        nome = texto.strip("•-– ").strip()
        if nome:
            atividades.append((nome, []))
    return atividades


def _siglas_de(paragrafos):
    pares = []
    for texto in paragrafos:
        casado = _RE_SIGLA.match(texto.strip())
        if casado:
            pares.append((casado.group(1).strip(), casado.group(2).strip()))
    return pares


def _banca_de(meta, paragrafos):
    membros = []
    if meta.get("orientador"):
        membros.append({
            "nome": meta["orientador"],
            "instituicao": "",
            "funcao": "Orientador",
        })
    if meta.get("coorientador"):
        membros.append({
            "nome": meta["coorientador"],
            "instituicao": "",
            "funcao": "Coorientador",
        })
    for texto in paragrafos:
        baixo = _sem_acento(texto)
        if "avaliador" not in baixo and "banca" not in baixo:
            continue
        nome = texto.split(":", 1)[-1].strip() if ":" in texto else texto.strip()
        if nome and nome not in {m["nome"] for m in membros}:
            funcao = "Avaliador Externo" if "extern" in baixo else "Avaliador"
            membros.append({"nome": nome, "instituicao": "", "funcao": funcao})
    return membros


def parse_projeto_docx(caminho_docx):
    if not os.path.exists(caminho_docx):
        raise FileNotFoundError(f"Arquivo de entrada não encontrado: {caminho_docx}")

    documento = docx.Document(caminho_docx)
    baldes = {
        "apresentacao": [],
        "introducao": [],
        "justificativa": [],
        "problema": [],
        "revisao": [],
        "objetivo_geral": [],
        "objetivos_especificos": [],
        "objetivos": [],
        "hipotese": [],
        "metodologia": [],
        "metodologia_natureza": [],
        "metodologia_locus": [],
        "metodologia_participantes": [],
        "metodologia_fontes": [],
        "metodologia_coleta": [],
        "metodologia_etica": [],
        "metodologia_analise": [],
        "cronograma": [],
        "resultados": [],
        "referencias": [],
        "siglas": [],
        "apendices": [],
        "anexos": [],
        "ptts": [],
    }
    secoes_ordem = []
    atual = None
    tabelas = []
    tabela_cronograma = None
    preambulo = []
    meta_rotulos = {}

    def abrir(nome, titulo):
        nonlocal atual
        atual = nome
        secoes_ordem.append({"chave": nome, "titulo": titulo, "paragrafos": []})

    for tipo, bloco in _iterar_blocos(documento):
        if tipo == "t":
            matriz = _matriz(bloco)
            if not matriz:
                continue
            if atual == "cronograma" and tabela_cronograma is None:
                tabela_cronograma = matriz
            else:
                tabelas.append(matriz)
            continue
        texto = bloco.text.strip()
        if not texto:
            continue
        casado = _RE_ROTULO.match(texto)
        if casado and atual is None:
            chave = _sem_acento(casado.group("chave").strip())
            destino = _ROTULOS_META.get(chave) or _ROTULOS_META.get(casado.group("chave").strip().lower())
            if destino:
                meta_rotulos[destino] = casado.group("valor").strip()
                continue
        if _e_titulo(bloco):
            nome = _classificar(texto) or "livre"
            abrir(nome, _titulo_limpo(texto) or texto)
            if nome == "ptts" and _e_subitem_ptt(texto):
                baldes["ptts"].append(_ptt_vazio(_titulo_limpo(texto) or texto, len(baldes["ptts"]) + 1))
            continue
        if atual is None:
            preambulo.append(texto)
            continue
        secoes_ordem[-1]["paragrafos"].append(texto)
        if atual == "ptts":
            if _e_subitem_ptt(texto):
                baldes["ptts"].append(_ptt_vazio(texto.strip(), len(baldes["ptts"]) + 1))
                continue
            if not baldes["ptts"]:
                continue
            if not _aplicar_linha_ptt(baldes["ptts"][-1], texto):
                item = baldes["ptts"][-1]
                if item["justificativa_impacto"]:
                    item["justificativa_impacto"] += "\n" + texto
                else:
                    item["justificativa_impacto"] = texto
            continue
        if atual in baldes and atual != "ptts":
            baldes[atual].append(texto)

    if not baldes["objetivo_geral"] and baldes["objetivos"]:
        baldes["objetivo_geral"] = [baldes["objetivos"][0]]
        baldes["objetivos_especificos"] = baldes["objetivos_especificos"] or baldes["objetivos"][1:]
    elif baldes["objetivos"] and not baldes["objetivos_especificos"]:
        baldes["objetivos_especificos"] = list(baldes["objetivos"])

    metodologia_solta = baldes["metodologia"]
    if metodologia_solta and not baldes["metodologia_natureza"]:
        baldes["metodologia_natureza"] = list(metodologia_solta)

    titulo = meta_rotulos.get("titulo", "")
    if not titulo:
        for texto in preambulo:
            if len(texto) > 12:
                titulo = texto
                preambulo = [item for item in preambulo if item != texto]
                break
    if preambulo and not baldes["apresentacao"]:
        baldes["apresentacao"] = list(preambulo)

    ano = meta_rotulos.get("ano", "")
    if not ano:
        for texto in [titulo, meta_rotulos.get("local", "")] + preambulo:
            casado = _RE_ANO.search(texto or "")
            if casado:
                ano = casado.group(0)
                break

    siglas = _siglas_de(baldes["siglas"])
    referencias = [item for item in baldes["referencias"] if item.strip()]
    artigos = []
    if baldes["resultados"]:
        artigos.append({
            "titulo": "Resultados preliminares",
            "secoes_texto": [("RESULTADOS", "\n\n".join(baldes["resultados"]))],
        })

    ptts = []
    for item in baldes["ptts"]:
        if item.get("titulo") or item.get("nome") or item.get("justificativa_impacto"):
            ptts.append(item)

    nao_mapeadas = [
        secao for secao in secoes_ordem
        if secao["chave"] == "livre" and secao["paragrafos"]
    ]

    return {
        "metadata": {
            "titulo": titulo,
            "autor": meta_rotulos.get("autor", ""),
            "orientador": meta_rotulos.get("orientador", ""),
            "coorientador": meta_rotulos.get("coorientador", ""),
            "coordenador": meta_rotulos.get("coordenador", ""),
            "nivel": "",
            "local": meta_rotulos.get("local", ""),
            "ano": ano,
            "area_concentracao": meta_rotulos.get("area_concentracao", ""),
            "linha_pesquisa": meta_rotulos.get("linha_pesquisa", ""),
            "data_aprovacao": "",
            "banca": _banca_de(meta_rotulos, preambulo + baldes["apresentacao"]),
            "siglas": siglas,
        },
        "apresentacao": {"texto_percurso": baldes["apresentacao"], "quadro_1": []},
        "projeto": {
            "introducao": baldes["introducao"],
            "justificativa": baldes["justificativa"],
            "problema": baldes["problema"],
            "revisao": baldes["revisao"],
            "objetivo_geral": " ".join(baldes["objetivo_geral"]).strip(),
            "objetivos_especificos": baldes["objetivos_especificos"],
            "hipotese": baldes["hipotese"],
            "metodologia_natureza": baldes["metodologia_natureza"],
            "metodologia_locus": baldes["metodologia_locus"],
            "metodologia_participantes": baldes["metodologia_participantes"],
            "metodologia_fontes": baldes["metodologia_fontes"],
            "metodologia_coleta": baldes["metodologia_coleta"],
            "metodologia_etica": baldes["metodologia_etica"],
            "metodologia_analise": baldes["metodologia_analise"],
            "tabela_1": {"linhas": tabelas[0]} if tabelas else {"linhas": []},
            "tabela_2": {"linhas": tabelas[1]} if len(tabelas) > 1 else {"linhas": []},
            "ptts": ptts,
            "cronograma": _atividades_cronograma(baldes["cronograma"], tabela_cronograma),
            "ano": ano,
        },
        "resultados": {"artigos": artigos},
        "referencias": referencias,
        "pos_textual": {
            "apendices": [{"titulo": "Apêndice", "conteudo": "\n".join(baldes["apendices"])}] if baldes["apendices"] else [],
            "anexos": [{"titulo": "Anexo", "conteudo": "\n".join(baldes["anexos"])}] if baldes["anexos"] else [],
        },
        "secoes": [
            secao for secao in secoes_ordem
            if secao["chave"] not in ("siglas", "referencias") and secao["paragrafos"]
        ],
        "secoes_nao_mapeadas": nao_mapeadas,
    }
