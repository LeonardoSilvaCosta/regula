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


class TabelaMetodologia(BaseModel):
    linhas: list[list[str]] = Field(default_factory=list)


class DocumentSections(BaseModel):
    """Textos das seções normativas da Resolução 009/2025, independentes do Word."""

    apresentacao: list[str] = Field(default_factory=list)
    introducao: list[str] = Field(default_factory=list)
    justificativa: list[str] = Field(default_factory=list)
    problema: list[str] = Field(default_factory=list)
    revisao: list[str] = Field(default_factory=list)
    objetivo_geral: str = ""
    objetivos_especificos: list[str] = Field(default_factory=list)
    hipotese: list[str] = Field(default_factory=list)
    metodologia_natureza: list[str] = Field(default_factory=list)
    metodologia_locus: str = ""
    metodologia_participantes: list[str] = Field(default_factory=list)
    metodologia_fontes: list[str] = Field(default_factory=list)
    metodologia_coleta: list[str] = Field(default_factory=list)
    metodologia_etica: list[str] = Field(default_factory=list)
    metodologia_analise: list[str] = Field(default_factory=list)
    tabela_1: TabelaMetodologia | None = None
    tabela_2: TabelaMetodologia | None = None
    referencias: list[str] = Field(default_factory=list)


class CronogramaAtividade(BaseModel):
    nome: str = ""
    meses: list[int] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    titulo: str = ""
    subtitulo: str = ""
    autor: str = ""
    orientador: str = ""
    coorientador: str = ""
    coordenador: str = "Prof. Dr. Edson Marcos Leal Soares Ramos"
    ano: str = "2026"
    local: str = "Belém-Pará"
    area_concentracao: str = "Segurança Pública, Justiça, Conflitos e Cidadania"
    linha_pesquisa: str = ""
    data_aprovacao: str = ""


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
    artigos: list["ArtigoQuadro"] = Field(default_factory=list)
    lacunas: list[LacunaItem]
    conformidade_ptt: "PTTValidationResult"
    sections: DocumentSections = Field(default_factory=DocumentSections)
    cronograma: list[CronogramaAtividade] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    """JSON completo ajustável no frontend antes da geração do DOCX.

    Com `documento_id` vazio, a compilação usa apenas metadata, sections, banca, ptts e siglas.
    """

    documento_id: str = ""
    tipo_documento: DocumentType = DocumentType.qualificacao
    nivel: AcademicLevel = AcademicLevel.mestrado
    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    sections: DocumentSections = Field(default_factory=DocumentSections)
    banca: list[BancaMember] = Field(default_factory=list)
    siglas: list[tuple[str, str]] = Field(default_factory=list)
    ptts: list["PTTItem"] = Field(default_factory=list)
    artigos: list["ArtigoQuadro"] = Field(default_factory=list)
    cronograma: list[CronogramaAtividade] = Field(default_factory=list)


from app.schemas.ptt import ArtigoQuadro, PTTItem, PTTValidationResult  # noqa: E402


class ValidatePTTRequest(BaseModel):
    ptts: list[PTTItem]
    nivel: AcademicLevel = AcademicLevel.mestrado


ParseResponse.model_rebuild()
GenerateRequest.model_rebuild()
