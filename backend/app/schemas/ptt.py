"""Schemas dos 22 itens de PTT e da validação da Resolução 007/2025."""

from typing import Optional

from pydantic import BaseModel, Field, model_validator


class PTTItem(BaseModel):
    """Ficha técnica da Resolução nº 007/2025-PPGSP (22 itens).

    Ano vazio herda o ano do trabalho. Coautoria e divulgação aceitam os
    nomes canônicos (`coautoria`, `divulgacao`) e os do formulário
    (`coautores`, `divulgacao_url`).
    """

    num: str = ""
    nome: str = ""
    autoria: str = ""
    tipo: str = ""
    subtipo: str = ""
    titulo: str = ""
    ano: Optional[str] = None
    coautoria: str = ""
    coautores: Optional[str] = ""
    projeto: str = ""
    financiamento: str = ""
    financiador: str = ""
    demanda: str = "Espontânea"
    impacto: str = "Alto"
    justificativa_impacto: str = ""
    inovacao: str = "Alto"
    justificativa_inovacao: str = ""
    complexidade: str = "Alta"
    justificativa_complexidade: str = ""
    validacao: str = ""
    divulgacao: str = ""
    divulgacao_url: str = ""
    abrangencia: str = "Local"
    publico_usuario: str = "Estado, Município, Comunidade"
    objetivo_especifico: str = ""
    tipo_estudo: str = "Qualitativo/Quantitativo Exploratório Descritivo"
    fontes: str = ""
    status: str = "Em produção"

    @model_validator(mode="before")
    @classmethod
    def _ano_vazio(cls, dados):
        if isinstance(dados, dict):
            ano = dados.get("ano")
            if isinstance(ano, str) and not ano.strip():
                dados = {**dados, "ano": None}
        return dados

    @model_validator(mode="after")
    def _espelhar_nomes(self):
        coautores = (self.coautores or "").strip()
        coautoria = (self.coautoria or "").strip()
        if coautores and not coautoria:
            self.coautoria = coautores
        elif coautoria and not coautores:
            self.coautores = coautoria
        url = (self.divulgacao_url or "").strip()
        divulgacao = (self.divulgacao or "").strip()
        if url and not divulgacao:
            self.divulgacao = url
        elif divulgacao and not url:
            self.divulgacao_url = divulgacao
        return self


class ArtigoQuadro(BaseModel):
    """Linha de artigo científico usada no Quadro 1 da Apresentação."""

    titulo: str = ""
    objetivo_especifico: str = ""
    tipo_estudo: str = "Qualitativo/Quantitativo Exploratório Descritivo"
    fontes: str = ""
    status: str = "Em produção"
    subtipo: str = "Artigo"


class PTTValidationResult(BaseModel):
    valido: bool
    total: int
    prop_alta: float = Field(description="Proporção de produtos com impacto Alto (0 a 1).")
    mensagem: str

