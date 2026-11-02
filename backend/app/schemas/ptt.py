"""Schemas dos 22 itens de PTT e da validação da Resolução 007/2025."""

from pydantic import BaseModel, Field


class PTTItem(BaseModel):
    """Ficha técnica da Resolução nº 007/2025-PPGSP (22 itens)."""

    num: str = ""
    nome: str = ""
    autoria: str = ""
    tipo: str = ""
    subtipo: str = ""
    titulo: str = ""
    ano: str = ""
    coautoria: str = ""
    projeto: str = ""
    financiamento: str = ""
    financiador: str = ""
    demanda: str = ""
    impacto: str = ""
    justificativa_impacto: str = ""
    inovacao: str = ""
    justificativa_inovacao: str = ""
    complexidade: str = ""
    justificativa_complexidade: str = ""
    validacao: str = ""
    divulgacao: str = ""
    abrangencia: str = ""
    publico_usuario: str = ""


class PTTValidationResult(BaseModel):
    valido: bool
    total: int
    prop_alta: float = Field(description="Proporção de produtos com impacto Alto (0 a 1).")
    mensagem: str

