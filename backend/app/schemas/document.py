"""Schemas Pydantic de metadados, banca, seções e lacunas."""

from enum import Enum

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    qualificacao = "qualificacao"
    dissertacao = "dissertacao"
    tese = "tese"


class AcademicLevel(str, Enum):
    mestrado = "mestrado"
    doutorado = "doutorado"


class BancaMember(BaseModel):
    nome: str
    titulacao: str | None = None
    instituicao: str = ""
    funcao: str = Field(
        description="Papel na banca: Orientador(a), Coorientador(a), Avaliador(a) Interno(a) ou Avaliador(a) Externo(a)."
    )


class DocumentMetadata(BaseModel):
    titulo: str = ""
    subtitulo: str = ""
    autor: str = ""
    orientador: str = ""
    coorientador: str = ""
    coordenador: str = ""
    ano: str = ""
    local: str = ""
    area_concentracao: str = ""
    linha_pesquisa: str = ""


class LacunaItem(BaseModel):
    codigo: str = ""
    secao: str = ""
    gravidade: str = ""
    regra: str = ""
    encontrado: str = ""
    recomendacao: str = ""


class ParseResponse(BaseModel):
    documento_id: str = ""
    tipo_documento: DocumentType
    nivel: AcademicLevel
    metadata: DocumentMetadata
    banca: list[BancaMember]
    siglas: list[tuple[str, str]]
    ptts: list["PTTItem"]
    lacunas: list[LacunaItem]
    conformidade_ptt: "PTTValidationResult"


class GenerateRequest(BaseModel):
    """JSON completo ajustável no frontend antes da geração do DOCX."""

    documento_id: str = ""
    tipo_documento: DocumentType = DocumentType.qualificacao
    nivel: AcademicLevel = AcademicLevel.mestrado
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    banca: list[BancaMember] = Field(default_factory=list)
    siglas: list[tuple[str, str]] = Field(default_factory=list)
    ptts: list["PTTItem"] = Field(default_factory=list)


from app.schemas.ptt import PTTItem, PTTValidationResult  # noqa: E402


class ValidatePTTRequest(BaseModel):
    ptts: list[PTTItem]
    nivel: AcademicLevel = AcademicLevel.mestrado


ParseResponse.model_rebuild()
GenerateRequest.model_rebuild()
