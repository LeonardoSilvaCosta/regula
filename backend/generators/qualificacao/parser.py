"""Extrai seções, metadados e tabelas do .docx enviado pelo usuário."""

import logging
import os
import re
import unicodedata

import docx
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph


logger = logging.getLogger(__name__)

_JUSTIFICATIVAS_50 = (
    "justificativa_impacto",
    "justificativa_inovacao",
    "justificativa_complexidade",
)

_RE_NUMERO = re.compile(r"^(?:cap[ií]tulo\s+)?\d+(?:\.\d+)*\s*[-–.)]?\s*", re.IGNORECASE)
_RE_ROTULO = re.compile(r"^(?P<chave>[^:]{2,60})\s*[:：]\s*(?P<valor>.*)$")
_RE_SIGLA = re.compile(r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ0-9]{2,12})\s*[-–:]\s+(.+)$")
_RE_ANO = re.compile(r"\b(19|20)\d{2}\b")
# 5.9.1, PTT 1 ou Produto 1. O cabeçalho 5.9 não é produto.
_RE_SUBITEM_PTT = re.compile(
    r"^(?:\d+\.\d+\.\d+\b|ptt\s*\d+\b|produto\s*\d+\b)",
    re.IGNORECASE,
)
_RE_LOCAL = re.compile(
    r"^[A-Za-zÀ-ÿ][\wÀ-ÿ'’.\- ]{0,40}?\s*[-–/]\s*(?:[A-Z]{2}|[A-Za-zÀ-ÿ][\wÀ-ÿ'’.\- ]{1,24})$"
)
_RE_TITULACAO = re.compile(
    r"^(?P<titulo>(?:(?:profa?|professor(?:a)?|dra?)\.?\s+)+)",
    re.IGNORECASE,
)
_RE_AREA = re.compile(
    r"[aá]rea\s+de\s+concentra[cç][aã]o\s*:\s*(.+)",
    re.IGNORECASE,
)
_RE_LINHA_PESQUISA = re.compile(
    r"linha\s+de\s+pesquisa\s*:\s*(.+)",
    re.IGNORECASE,
)
_RE_ORIENTADOR = re.compile(
    r"orientador(?:\(a\))?\s*:\s*(.+)",
    re.IGNORECASE,
)
_RE_COORIENTADOR = re.compile(
    r"coorientador(?:\(a\))?\s*:\s*(.+)",
    re.IGNORECASE,
)
_RE_DATA_APROVACAO = re.compile(
    r"(?:bel[eé]m.*)?(?:_{2,}|\d{1,2})\s+de\s+(?:_{2,}|[a-zçãéíóú]+)\s+de\s+(?:19|20)\d{2}",
    re.IGNORECASE,
)

# Dados gerais: somente capa e folha de rosto.
_ALIASES_GERAIS = (
    ("area_concentracao", ("area de concentracao",)),
    ("linha_pesquisa", ("linha de pesquisa",)),
    ("subtitulo", ("subtitulo",)),
    ("titulo", ("titulo",)),
    ("autor", ("autor", "autora", "discente")),
    ("ano", ("ano",)),
    ("local", ("local", "cidade")),
)

# Orientação e banca: somente a folha de aprovação.
_ALIASES_BANCA = (
    ("instituicao_coorientador", ("instituicao do coorientador", "instituicao da coorientadora", "instituicao coorientador")),
    ("instituicao_orientador", ("instituicao do orientador", "instituicao da orientadora", "instituicao orientador")),
    ("coorientador", ("coorientador", "coorientadora", "co-orientador", "co-orientadora")),
    ("orientador", ("orientador", "orientadora")),
    ("coordenador", ("coordenador", "coordenadora")),
)

_INSTITUCIONAL = (
    "universidade federal do para",
    "instituto de ciencias exatas e naturais",
    "programa de pos-graduacao em seguranca publica",
    "programa de pos graduacao em seguranca publica",
    "universidade",
    "instituto",
    "programa de pos",
    "faculdade",
)

# Classificação da Resolução 007/2025: pista no nome -> (tipo, subtipo).
_CLASSE_PTT = (
    ("infografic", "Material Didático", "Infográfico"),
    ("codebook", "Manual/Protocolo", "Codebook"),
    ("base de dados", "Base de Dados", "Base de Dados"),
    ("banco de dados", "Base de Dados", "Base de Dados"),
    ("software", "Software Registrável", "Software"),
    ("aplicativo", "Software Registrável", "Aplicativo"),
    ("manual", "Manual/Protocolo", "Manual"),
    ("protocolo", "Manual/Protocolo", "Protocolo"),
    ("llm", "Ferramenta Tecnológica", "Modelo de Linguagem"),
    ("modelo de linguagem", "Ferramenta Tecnológica", "Modelo de Linguagem"),
    ("modelo", "Ferramenta Tecnológica", "Modelo de IA"),
)

_AREA_PADRAO = "Segurança Pública, Justiça, Conflitos e Cidadania"
_LINHA_TECNOLOGIA = "Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação"
_COORDENADOR_PADRAO = "Prof. Dr. Edson Marcos Leal Soares Ramos"

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
    # Caixa alta só abre seção quando o texto é um título conhecido
    # (INTRODUÇÃO, APRESENTAÇÃO etc.). O título da capa não entra aqui.
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


def _destino_meta(rotulo, aliases):
    """Associa o nome do campo no documento à chave dos metadados."""
    chave = _sem_acento(rotulo or "").strip(" .:-–—")
    chave = re.sub(r"\s+", " ", chave)
    if not chave or len(chave) > 70:
        return None
    for destino, nomes in aliases:
        for alias in nomes:
            if chave == alias:
                return destino
            if chave.startswith(alias + "(") or chave.startswith(alias + " ("):
                return destino
            if " " in alias and chave.startswith(alias + " "):
                return destino
    return None


def _quebra_de_pagina(paragrafo):
    """Quebra explícita. lastRenderedPageBreak aparece em quase todo parágrafo e não separa a capa."""
    return 'w:type="page"' in paragrafo._p.xml


def _zona_explicita(texto):
    """Capa, folha de rosto, folha de aprovação ou lista de siglas, quando o título aparece."""
    limpo = _sem_acento(_titulo_limpo(texto))
    if limpo in ("capa",) or limpo.startswith("capa "):
        return "capa"
    if "folha de rosto" in limpo:
        return "folha_rosto"
    if "folha de aprovacao" in limpo:
        return "folha_aprovacao"
    if "abreviatur" in limpo or "lista de siglas" in limpo or limpo in ("siglas", "sigla"):
        return "siglas"
    return None


def _e_secao_5(texto):
    """Seção 5 ou subseção 5.9. O item 5.9.1 é produto, não cabeçalho."""
    bruto = (texto or "").strip()
    if re.match(r"^\d+\.\d+\.\d+", bruto):
        return False
    limpo = _sem_acento(_titulo_limpo(bruto.split(":")[0]))
    if re.match(r"^5(\.\d+)?(\s|\.|$)", bruto) and (
        "produto" in limpo or "ptt" in limpo or limpo in ("", "produtos")
    ):
        return True
    return limpo.startswith("proposta de produto") or limpo in (
        "produtos tecnicos",
        "produtos tecnologicos",
        "produtos tecnico-tecnologicos",
        "produtos",
    )


def _fim_pretextual(texto):
    limpo = _sem_acento(_titulo_limpo(texto))
    # Número de seção (1, 2, 10). Ano de quatro dígitos não encerra a capa.
    if re.match(r"^(?:[1-9]|1\d)(?:\s|\.|$)", (texto or "").strip()) and not re.match(r"^5(?:\s|\.|$)", (texto or "").strip()):
        return True
    if re.match(r"^1(?:\s|\.|\)|-|–)+\s*consideracoes gerais\b", _sem_acento(texto or "")):
        return True
    return any(chave in limpo for chave in (
        "resumo", "abstract", "sumario", "dedicatoria", "agradec", "epigrafe", "lista de", "introdu", "apresenta",
    ))


def _inicio_corpo(texto):
    """Primeiro título do corpo encerra a capa mesmo sem quebra de página."""
    bruto = (texto or "").strip()
    if not bruto or len(bruto) > 180:
        return False
    limpo = _sem_acento(_titulo_limpo(bruto))
    if limpo in ("introducao", "apresentacao") or limpo.startswith(("introducao ", "apresentacao ")):
        return True
    return bool(re.match(r"^1(?:\s|\.|\)|-|–)+\s*consideracoes gerais\b", _sem_acento(bruto)))


def _marca_rosto(texto):
    baixo = _sem_acento(texto)
    return (
        "area de concentracao" in baixo
        or "linha de pesquisa" in baixo
        or "requisito parcial" in baixo
        or "colegiado do programa" in baixo
    )


def _marca_aprovacao(texto):
    baixo = _sem_acento(texto)
    return (
        "banca examinadora" in baixo
        or "folha de aprovacao" in baixo
        or "data de aprovacao" in baixo
    )


def _linha_institucional(texto):
    baixo = _sem_acento(texto).strip(" .")
    if baixo.startswith("mestrado") or baixo.startswith("doutorado") or baixo in ("ufpa", "ppgsp"):
        return True
    return any(chave in baixo for chave in _INSTITUCIONAL)


def _e_caixa_alta(texto):
    letras = [ch for ch in texto if ch.isalpha()]
    return len(letras) >= 3 and all(ch.isupper() for ch in letras)


def _e_nome_proprio(texto):
    """Nome em Title Case, com partículas minúsculas (da, de, do)."""
    palavras = [p for p in re.split(r"\s+", (texto or "").strip()) if p]
    if len(palavras) < 2 or len(palavras) > 8:
        return False
    particulas = {"da", "de", "do", "das", "dos", "e", "di", "du"}
    proprias = 0
    for palavra in palavras:
        if palavra.lower() in particulas:
            continue
        nucleo = palavra.strip(".")
        if not nucleo or not nucleo[0].isupper() or nucleo[1:].lower() != nucleo[1:]:
            return False
        proprias += 1
    return proprias >= 2


def _guardar_meta(meta, destino, valor):
    valor = (valor or "").strip()
    if destino and valor and not meta.get(destino):
        meta[destino] = valor


def _linha_meta(meta, texto, pendente, aliases):
    """Lê 'Nome do campo: valor' ou um rótulo sozinho, cujo valor vem na linha seguinte."""
    casado = _RE_ROTULO.match((texto or "").strip())
    if casado:
        destino = _destino_meta(casado.group("chave"), aliases)
        valor = casado.group("valor").strip()
        if destino and valor:
            _guardar_meta(meta, destino, valor)
            return None
        if destino and not valor:
            return destino
        return pendente
    if pendente:
        _guardar_meta(meta, pendente, texto)
        return None
    destino = _destino_meta(texto, aliases)
    if destino and len(_sem_acento(texto).strip(" .:-")) <= 48:
        return destino
    return None


def _tabela_meta(meta, matriz, aliases):
    for linha in matriz:
        celulas = []
        for celula in linha:
            texto = (celula or "").strip()
            if texto and (not celulas or celulas[-1] != texto):
                celulas.append(texto)
        if not celulas:
            continue
        if len(celulas) >= 2:
            destino = _destino_meta(celulas[0], aliases)
            if destino:
                _guardar_meta(meta, destino, celulas[1])
                continue
        for celula in celulas:
            _linha_meta(meta, celula, None, aliases)


def _celulas_unicas(linha):
    celulas = []
    for celula in linha:
        texto = (celula or "").strip()
        if texto and (not celulas or celulas[-1] != texto):
            celulas.append(texto)
    return celulas


def _funcao_de_texto(texto):
    baixo = _sem_acento(texto)
    if "coorient" in baixo:
        return "Coorientador(a)"
    if "orient" in baixo and "coorden" not in baixo:
        return "Orientador(a)"
    if "extern" in baixo:
        return "Avaliador(a) Externo(a)"
    if "intern" in baixo or "ufpa" in baixo:
        return "Avaliador(a) Interno(a)"
    if "avali" in baixo or "examin" in baixo:
        return "Avaliador(a) Interno(a)"
    if "coorden" in baixo:
        return "Coordenador"
    return ""


def _separar_titulacao(texto):
    """'Prof. Dr. Fulano' vira titulação e nome."""
    casado = _RE_TITULACAO.match((texto or "").strip())
    if not casado:
        return "", (texto or "").strip()
    titulacao = re.sub(r"\s+", " ", casado.group("titulo")).strip()
    nome = (texto or "").strip()[casado.end():].strip(" .,-")
    return titulacao, nome or (texto or "").strip()


def _papel_avaliador(instituicao, pista=""):
    baixo = _sem_acento(f"{instituicao} {pista}")
    if "extern" in baixo:
        return "Avaliador(a) Externo(a)"
    if "ufpa" in baixo or "federal do para" in baixo or "intern" in baixo:
        return "Avaliador(a) Interno(a)"
    if instituicao.strip():
        return "Avaliador(a) Externo(a)"
    return "Avaliador(a) Interno(a)"


def _explodir_linhas(textos):
    linhas = []
    for texto in textos:
        for parte in re.split(r"[\n\r]+", texto or ""):
            parte = parte.strip()
            if parte:
                linhas.append(parte)
    return linhas


def _partir_titulo(texto):
    """Na capa, o que vem depois dos dois pontos é o subtítulo."""
    if ":" in (texto or ""):
        titulo, subtitulo = texto.split(":", 1)
        return titulo.strip(), subtitulo.strip()
    return (texto or "").strip(), ""


def _formatar_local(texto):
    """Saída canônica Cidade-Estado, sem espaços em volta do hífen."""
    bruto = re.sub(r"\s+", " ", (texto or "").strip())
    baixo = _sem_acento(bruto)
    if "belem" in baixo and (re.search(r"\bpa\b", baixo) or "para" in baixo):
        return "Belém-Pará"
    partes = [parte.strip(" .") for parte in re.split(r"\s*[-–/]\s*", bruto) if parte.strip(" .")]
    if len(partes) >= 2:
        return f"{partes[0]}-{partes[1]}"
    return bruto


def _parece_local(texto):
    bruto = (texto or "").strip()
    if not bruto or len(bruto) > 40:
        return False
    if _RE_LOCAL.match(bruto):
        return True
    return bool(re.search(r"bel[eé]m", bruto, re.IGNORECASE))


def _rodape_local_ano(linhas):
    """O ano fica na linha de baixo do local, no fim da capa (corpo ou rodapé)."""
    uteis = [linha for linha in linhas if linha.strip()]
    if not uteis:
        return uteis, "", ""
    ultima = uteis[-1].strip()
    ano = ""
    local = ""
    corte = len(uteis)
    if _RE_ANO.fullmatch(ultima) or (_RE_ANO.search(ultima) and len(ultima) <= 12):
        ano = _RE_ANO.search(ultima).group(0)
        corte = len(uteis) - 1
        if corte and _parece_local(uteis[corte - 1]):
            local = _formatar_local(uteis[corte - 1])
            corte -= 1
    elif _parece_local(ultima):
        local = _formatar_local(ultima)
        corte = len(uteis) - 1
    return uteis[:corte], local, ano


def _ler_capa(textos, rodape=None):
    """Título em caixa alta, autor em Title Case, local e ano no fim da capa."""
    linhas = [
        linha for linha in _explodir_linhas(textos)
        if _sem_acento(linha) not in ("capa",)
    ]
    miolo, local, ano = _rodape_local_ano(linhas)
    if rodape and (not local or not ano):
        _, local_rodape, ano_rodape = _rodape_local_ano(list(rodape))
        local = local or local_rodape
        ano = ano or ano_rodape
    titulo_linhas = []
    autor = ""
    for linha in miolo:
        if _linha_institucional(linha):
            continue
        palavras = linha.split()
        if (
            not autor
            and not _e_caixa_alta(linha)
            and _e_nome_proprio(linha)
            and 2 <= len(palavras) <= 6
            and ":" not in linha
        ):
            autor = linha.strip()
            continue
        if _e_caixa_alta(linha) or ":" in linha:
            titulo_linhas.append(linha.strip())
    titulo, subtitulo = _partir_titulo(" ".join(titulo_linhas))
    return {
        "titulo": titulo,
        "subtitulo": subtitulo,
        "autor": autor,
        "local": local,
        "ano": ano,
    }


def _valor_apos_dois_pontos(casado):
    """Texto exato depois dos dois pontos, até o próximo rótulo se estiver na mesma linha."""
    valor = (casado.group(1) if casado else "").strip()
    valor = re.split(
        r"\s+(?=(?:[aá]rea\s+de\s+concentra[cç][aã]o|linha\s+de\s+pesquisa|coorientador|orientador)\b)",
        valor,
        maxsplit=1,
        flags=re.IGNORECASE,
    )[0].strip()
    return valor


def _ler_folha_rosto(textos):
    """O valor do campo é o texto que vem depois dos dois pontos."""
    linhas = [
        linha for linha in _explodir_linhas(textos)
        if _sem_acento(linha) not in ("folha de rosto",)
    ]
    meta = {}
    for linha in linhas:
        baixo = _sem_acento(linha)
        if "coorientador" in baixo:
            _guardar_meta(meta, "coorientador", _valor_apos_dois_pontos(_RE_COORIENTADOR.search(linha)).rstrip("."))
            continue
        if "orientador" in baixo:
            _guardar_meta(meta, "orientador", _valor_apos_dois_pontos(_RE_ORIENTADOR.search(linha)).rstrip("."))
            continue
        if "area de concentracao" in baixo:
            _guardar_meta(meta, "area_concentracao", _valor_apos_dois_pontos(_RE_AREA.search(linha)))
            continue
        if "linha de pesquisa" in baixo:
            _guardar_meta(meta, "linha_pesquisa", _valor_apos_dois_pontos(_RE_LINHA_PESQUISA.search(linha)))
    return meta


def _bloco_membro(partes):
    funcao = ""
    nome = ""
    titulacao = ""
    instituicao = ""
    for parte in partes:
        casado = _RE_ROTULO.match(parte)
        if casado and _funcao_de_texto(casado.group("chave")) not in ("", "Coordenador"):
            papel = _funcao_de_texto(casado.group("chave"))
            bruto = casado.group("valor").strip()
            tit, nome_limpo = _separar_titulacao(bruto)
            if papel.startswith("Avaliador"):
                papel = _papel_avaliador(instituicao, parte)
            return nome_limpo, papel, instituicao, tit
        papel = _funcao_de_texto(parte)
        if papel and papel != "Coordenador":
            funcao = papel
            continue
        if not nome:
            titulacao, nome = _separar_titulacao(parte)
        elif not instituicao and not _e_nome_proprio(parte):
            instituicao = parte.strip()
    if nome and funcao:
        if funcao.startswith("Avaliador"):
            funcao = _papel_avaliador(instituicao, funcao)
        return nome, funcao, instituicao, titulacao
    return None


def _ler_folha_aprovacao(textos, tabelas):
    """Acima de BANCA EXAMINADORA está o coordenador; abaixo, os membros."""
    linhas = _explodir_linhas(textos)
    indice = next((i for i, linha in enumerate(linhas) if "banca examinadora" in _sem_acento(linha)), None)
    coordenador = ""
    abaixo = linhas
    if indice is not None:
        for linha in reversed(linhas[:indice]):
            baixo = _sem_acento(linha)
            if "coordenador" in baixo or "folha de aprovacao" in baixo or _linha_institucional(linha):
                continue
            coordenador = linha.strip()
            break
        abaixo = linhas[indice + 1 :]

    membros = []
    vistos = set()

    def acrescentar(nome, funcao, instituicao="", titulacao=""):
        nome = (nome or "").strip(" .:-")
        if not nome or len(nome) < 3 or _linha_institucional(nome):
            return
        chave = _sem_acento(nome)
        if chave in vistos:
            return
        vistos.add(chave)
        if (funcao or "").startswith("Avaliador"):
            funcao = _papel_avaliador(instituicao, funcao)
        membros.append({
            "nome": nome,
            "titulacao": (titulacao or "").strip(),
            "instituicao": (instituicao or "").strip(),
            "funcao": funcao or "Avaliador(a) Interno(a)",
        })

    grupo = []
    espera_instituicao = False
    for linha in abaixo:
        if _fim_pretextual(linha) or "abreviatur" in _sem_acento(linha):
            break
        if espera_instituicao and _linha_institucional(linha):
            if membros:
                membros[-1]["instituicao"] = linha.strip()
                if membros[-1]["funcao"].startswith("Avaliador"):
                    membros[-1]["funcao"] = _papel_avaliador(linha, membros[-1]["funcao"])
            espera_instituicao = False
            continue
        papel = _funcao_de_texto(linha)
        rotulo = _RE_ROTULO.match(linha)
        if papel and papel != "Coordenador" or (rotulo and _funcao_de_texto(rotulo.group("chave")) not in ("", "Coordenador")):
            grupo.append(linha)
            bloco = _bloco_membro(grupo)
            if bloco:
                acrescentar(*bloco)
                espera_instituicao = True
            grupo = []
            continue
        if not _linha_institucional(linha):
            grupo.append(linha)

    data_aprovacao = ""
    for linha in linhas:
        if _RE_DATA_APROVACAO.search(linha):
            data_aprovacao = linha.strip()
            break

    for indice, linha in enumerate(linhas):
        baixo = _sem_acento(linha)
        if "coordenador" not in baixo:
            continue
        sem_rotulo = re.sub(r"\([^)]*coordenador[^)]*\)", "", linha, flags=re.IGNORECASE).strip(" .:-")
        if sem_rotulo and "coordenador" not in _sem_acento(sem_rotulo) and not _linha_institucional(sem_rotulo):
            coordenador = sem_rotulo
        elif indice > 0 and not _linha_institucional(linhas[indice - 1]):
            coordenador = linhas[indice - 1].strip()
        break

    for matriz in tabelas:
        for linha in matriz:
            for celula in _celulas_unicas(linha):
                partes = [parte.strip() for parte in re.split(r"[\n\r]+", celula) if parte.strip()]
                if not partes or "banca examinadora" in _sem_acento(partes[0]):
                    continue
                instituicao = partes[1] if len(partes) > 1 else ""
                papel = partes[2] if len(partes) > 2 else ""
                if not papel and len(partes) == 2 and _funcao_de_texto(partes[1]) not in ("", "Coordenador"):
                    papel = partes[1]
                    instituicao = ""
                titulacao, nome = _separar_titulacao(partes[0])
                funcao = _funcao_de_texto(papel)
                if funcao.startswith("Avaliador"):
                    funcao = _papel_avaliador(instituicao, papel)
                if funcao and funcao != "Coordenador":
                    acrescentar(nome, funcao, instituicao, titulacao)
    return coordenador, membros, data_aprovacao


def _banca_de(meta, membros_aprovacao):
    membros = list(membros_aprovacao)
    nomes = set()
    for membro in membros:
        _, limpo = _separar_titulacao(membro.get("nome") or "")
        if limpo:
            nomes.add(_sem_acento(limpo))

    def garantir(nome, instituicao, funcao):
        titulacao, limpo = _separar_titulacao(nome)
        if not limpo or _sem_acento(limpo) in nomes:
            return
        nomes.add(_sem_acento(limpo))
        membros.append({
            "nome": limpo,
            "titulacao": titulacao,
            "instituicao": instituicao,
            "funcao": funcao,
        })

    garantir(meta.get("orientador"), meta.get("instituicao_orientador", ""), "Orientador(a)")
    garantir(meta.get("coorientador"), meta.get("instituicao_coorientador", ""), "Coorientador(a)")
    coordenador = (meta.get("coordenador") or "").strip()
    if coordenador:
        garantir(coordenador, "", "Coordenador")
    for membro in membros:
        papel = membro["funcao"]
        if papel == "Coordenador" and not meta.get("coordenador"):
            meta["coordenador"] = membro["nome"]
        elif papel.startswith("Orientador") and not meta.get("orientador"):
            meta["orientador"] = membro["nome"]
            meta["instituicao_orientador"] = membro.get("instituicao") or ""
        elif papel.startswith("Coorientador") and not meta.get("coorientador"):
            meta["coorientador"] = membro["nome"]
            meta["instituicao_coorientador"] = membro.get("instituicao") or ""
    return [m for m in membros if m["funcao"] != "Coordenador"]


def _inferir_classe_ptt(texto):
    baixo = _sem_acento(texto)
    for pista, tipo, subtipo in _CLASSE_PTT:
        if pista in baixo:
            return tipo, subtipo
    return "", ""


def _e_produto_nomeado(texto):
    """'Infográfico X: descrição', e não o cabeçalho 5.9 nem um campo da ficha."""
    if _e_secao_5(texto) or _e_cabecalho_produto(texto):
        return False
    casado = _RE_ROTULO.match((texto or "").strip())
    if not casado:
        return False
    chave = _sem_acento(casado.group("chave").strip())
    if chave in _CAMPOS_PTT or _destino_meta(casado.group("chave"), _ALIASES_GERAIS):
        return False
    valor = casado.group("valor").strip()
    return bool(valor) and 1 <= len(chave.split()) <= 16


def _e_cabecalho_produto(texto):
    bruto = (texto or "").strip()
    if re.match(r"^\d+\.\d+\.\d+", bruto):
        return False
    limpo = _sem_acento(_titulo_limpo(bruto.split(":")[0]))
    return bool(re.match(r"^\d+\.\d+(\s|$)", bruto) and "produto" in limpo)


def _ptt_de_linha(texto, indice):
    bruto = _RE_SUBITEM_PTT.sub("", (texto or "").strip()).strip(" .:-")
    nome = bruto
    descricao = ""
    casado = _RE_ROTULO.match(bruto)
    if casado and _sem_acento(casado.group("chave")) not in _CAMPOS_PTT:
        nome = casado.group("chave").strip()
        descricao = casado.group("valor").strip()
    nome = _titulo_limpo(nome) or nome
    tipo, subtipo = _inferir_classe_ptt(f"{nome} {descricao}")
    item = _ptt_vazio(nome, indice)
    item["tipo"] = tipo
    item["subtipo"] = subtipo
    item["demanda"] = descricao
    item["justificativa_impacto"] = descricao
    return item


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
    linhas_capa = []
    linhas_rosto = []
    linhas_aprovacao = []
    tabelas_aprovacao = []
    meta_rotulos = {}
    rotulo_pendente = None
    frente = "capa"
    quebra_pendente = False

    def abrir(nome, titulo):
        nonlocal atual
        atual = nome
        secoes_ordem.append({"chave": nome, "titulo": titulo, "paragrafos": []})

    def avancar_pagina():
        """Uma quebra só troca de frente se a página atual já tiver texto."""
        nonlocal frente, rotulo_pendente
        if frente == "capa" and linhas_capa:
            frente = "folha_rosto"
        elif frente == "folha_rosto" and linhas_rosto:
            frente = "folha_aprovacao"
        rotulo_pendente = None

    for tipo, bloco in _iterar_blocos(documento):
        if tipo == "t":
            matriz = _matriz(bloco)
            if not matriz:
                continue
            if frente in ("capa", "folha_rosto", "folha_aprovacao"):
                if frente == "folha_aprovacao":
                    tabelas_aprovacao.append(matriz)
                continue
            if atual == "cronograma" and tabela_cronograma is None:
                tabela_cronograma = matriz
            else:
                tabelas.append(matriz)
            continue
        tem_quebra = _quebra_de_pagina(bloco)
        texto = bloco.text.strip()
        if not texto:
            if tem_quebra and not quebra_pendente:
                quebra_pendente = True
            continue
        if quebra_pendente:
            avancar_pagina()
            quebra_pendente = False
        if tem_quebra:
            quebra_pendente = True
        zona = _zona_explicita(texto)
        if zona:
            frente = zona
            rotulo_pendente = None
            if zona == "siglas":
                abrir("siglas", _titulo_limpo(texto) or texto)
            continue
        if frente in ("capa", "folha_rosto", "folha_aprovacao") and _inicio_corpo(texto):
            frente = "corpo"
            rotulo_pendente = None
        elif frente in ("capa", "folha_rosto", "folha_aprovacao") and _e_titulo(bloco) and _fim_pretextual(texto):
            frente = "corpo"
            rotulo_pendente = None
        elif frente != "corpo" and _marca_aprovacao(texto):
            frente = "folha_aprovacao"
        elif frente == "capa" and _marca_rosto(texto):
            frente = "folha_rosto"
        if atual == "ptts" and not _e_secao_5(texto) and (_e_subitem_ptt(texto) or _e_produto_nomeado(texto)):
            baldes["ptts"].append(_ptt_de_linha(texto, len(baldes["ptts"]) + 1))
            continue
        if frente == "capa":
            linhas_capa.append(texto)
            continue
        if frente == "folha_rosto":
            linhas_rosto.append(texto)
            continue
        if frente == "folha_aprovacao":
            linhas_aprovacao.append(texto)
            continue
        if atual == "ptts" and not _e_secao_5(texto) and (_e_subitem_ptt(texto) or _e_produto_nomeado(texto)):
            baldes["ptts"].append(_ptt_de_linha(texto, len(baldes["ptts"]) + 1))
            continue
        if _e_titulo(bloco):
            nome = _classificar(texto) or "livre"
            if nome == "ptts" and not _e_secao_5(texto):
                nome = "livre"
            if nome == "siglas" or _e_secao_5(texto):
                frente = "corpo"
            abrir(nome if not _e_secao_5(texto) else "ptts", _titulo_limpo(texto) or texto)
            continue
        if atual is None:
            preambulo.append(texto)
            continue
        secoes_ordem[-1]["paragrafos"].append(texto)
        if atual == "ptts":
            if not _e_secao_5(texto) and (_e_subitem_ptt(texto) or _e_produto_nomeado(texto)):
                baldes["ptts"].append(_ptt_de_linha(texto, len(baldes["ptts"]) + 1))
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

    rodape = []
    for secao in documento.sections:
        for paragrafo in secao.footer.paragraphs:
            if paragrafo.text.strip():
                rodape.append(paragrafo.text.strip())
    capa = _ler_capa(linhas_capa, rodape)
    rosto = _ler_folha_rosto(linhas_rosto)
    coordenador, membros_aprovacao, data_aprovacao = _ler_folha_aprovacao(linhas_aprovacao, tabelas_aprovacao)
    meta_rotulos.update({chave: valor for chave, valor in {**capa, **rosto}.items() if valor})
    if coordenador:
        meta_rotulos["coordenador"] = coordenador
    if data_aprovacao:
        meta_rotulos["data_aprovacao"] = data_aprovacao
    if preambulo and not baldes["apresentacao"]:
        baldes["apresentacao"] = list(preambulo)

    ano = meta_rotulos.get("ano", "")

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

    banca = _banca_de(meta_rotulos, membros_aprovacao)
    sem_rosto = not linhas_rosto and not rosto
    sem_aprovacao = not linhas_aprovacao and not tabelas_aprovacao and not membros_aprovacao
    if sem_rosto and sem_aprovacao:
        if not meta_rotulos.get("area_concentracao"):
            meta_rotulos["area_concentracao"] = _AREA_PADRAO
        if not meta_rotulos.get("coordenador"):
            meta_rotulos["coordenador"] = _COORDENADOR_PADRAO
        if not meta_rotulos.get("linha_pesquisa"):
            corpus = _sem_acento(" ".join(
                texto
                for nome, linhas in baldes.items()
                if nome != "ptts"
                for texto in linhas
            ))
            if any(pista in corpus for pista in (
                "inteligencia artificial", "aprendizado de maquina", "aprendizado",
                "tecnologia", "dados", "algoritm", "software", "llm", "modelo",
            )):
                meta_rotulos["linha_pesquisa"] = _LINHA_TECNOLOGIA

    for indice, item in enumerate(ptts, start=1):
        for campo in _JUSTIFICATIVAS_50:
            quantidade = len(re.findall(r"\S+", str(item.get(campo) or "")))
            if quantidade > 50:
                logger.warning(
                    "Produto %s: %s tem %s palavras (máximo de 50).",
                    indice,
                    campo,
                    quantidade,
                )

    for item in ptts:
        if not item.get("autoria"):
            item["autoria"] = meta_rotulos.get("autor", "")
        if not item.get("impacto"):
            item["impacto"] = "Alto"
        if not item.get("ano"):
            item["ano"] = meta_rotulos.get("ano", "")

    return {
        "metadata": {
            "titulo": meta_rotulos.get("titulo", ""),
            "subtitulo": meta_rotulos.get("subtitulo", ""),
            "autor": meta_rotulos.get("autor", ""),
            "orientador": meta_rotulos.get("orientador", ""),
            "coorientador": meta_rotulos.get("coorientador", ""),
            "coordenador": meta_rotulos.get("coordenador", ""),
            "nivel": "",
            "local": meta_rotulos.get("local", ""),
            "ano": ano,
            "area_concentracao": meta_rotulos.get("area_concentracao", ""),
            "linha_pesquisa": meta_rotulos.get("linha_pesquisa", ""),
            "data_aprovacao": meta_rotulos.get("data_aprovacao", ""),
            "banca": banca,
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
