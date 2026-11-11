export interface CategoriaCodebook {
  eixo: string;
  codigo: string;
  nome: string;
  definicao: string;
  inclusao: string[];
  exclusao: string[];
  contraexemplos: string[];
}

export interface MatrizFronteira {
  titulo: string;
  colunas: string[];
  linhas: string[][];
  fonte: string;
}

export interface Codebook {
  versao: string;
  data_versao: string;
  contexto: string[];
  autores_peritos: string[];
  fontes_dados: string[];
  fundamentacao: string[];
  desidentificacao: string[];
  aprovacao_etica: string[];
  salvaguardas: string[];
  polaridade: string[];
  sujeito: string[];
  temporalidade: string[];
  granularidade: string[];
  categorias: CategoriaCodebook[];
  matrizes: MatrizFronteira[];
  metricas: string[];
  limiares: string[];
  adjudicacao_piloto: string[];
  adjudicacao_producao: string[];
  ferramenta: string;
  configuracao_interface: string;
  changelog: string[];
  simbolos: [string, string][];
}

export function codebookVazio(): Codebook {
  return {
    versao: "1.0",
    data_versao: "",
    contexto: [],
    autores_peritos: [],
    fontes_dados: [],
    fundamentacao: [],
    desidentificacao: [],
    aprovacao_etica: [],
    salvaguardas: [],
    polaridade: [],
    sujeito: [],
    temporalidade: [],
    granularidade: [],
    categorias: [],
    matrizes: [],
    metricas: [],
    limiares: [],
    adjudicacao_piloto: [],
    adjudicacao_producao: [],
    ferramenta: "Label Studio",
    configuracao_interface: "",
    changelog: [],
    simbolos: [
      ["κ", "kappa de Cohen"],
      ["α", "alfa de Krippendorff"],
    ],
  };
}

export function linhas(valor: string): string[] {
  return valor
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function texto(valor: string[] | undefined): string {
  return (valor ?? []).join("\n");
}
