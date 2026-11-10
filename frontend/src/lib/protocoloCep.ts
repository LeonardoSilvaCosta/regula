export type TipoCampoCep = "sim_nao" | "opcoes" | "texto" | "texto_longo" | "lista" | "anexo";

export type CampoProtocoloCep = {
  chave: string;
  rotulo: string;
  tipo: TipoCampoCep;
  opcoes?: string[];
};

/** Espelha backend/generators/protocolo_cep/estrutura.py */
export const CAMPOS_PROTOCOLO_CEP: CampoProtocoloCep[] = [
  { chave: "pesquisa_seres_humanos", rotulo: "A pesquisa envolve seres humanos?", tipo: "sim_nao" },
  {
    chave: "modelo",
    rotulo: "Modelo que deseja preencher",
    tipo: "opcoes",
    opcoes: ["Simplificado", "Completo"],
  },
  { chave: "pesquisador_principal", rotulo: "Pesquisador Principal", tipo: "texto" },
  {
    chave: "delegar_preenchimento",
    rotulo:
      "Deseja delegar a autorização de preenchimento deste projeto a outras pessoas já cadastradas no sistema?",
    tipo: "sim_nao",
  },
  { chave: "assistentes", rotulo: "Assistentes", tipo: "lista" },
  { chave: "equipe_pesquisa", rotulo: "Equipe de Pesquisa", tipo: "lista" },
  { chave: "instituicao_proponente", rotulo: "Instituição Proponente", tipo: "texto" },
  { chave: "estudo_internacional", rotulo: "É um estudo internacional?", tipo: "sim_nao" },
  { chave: "area_tematica_especial", rotulo: "Área Temática Especial", tipo: "texto" },
  { chave: "grandes_areas_cnpq", rotulo: "Grandes Áreas do Conhecimento (CNPq)", tipo: "texto" },
  {
    chave: "proposito_principal_oms",
    rotulo: "Propósito Principal do Estudo (OMS)",
    tipo: "opcoes",
    opcoes: [
      "Clínico",
      "Ciências básicas",
      "Ciências sociais, Humanas ou Filosofia aplicadas à Saúde",
      "Saúde Coletiva / Saúde Pública",
      "Supportive Care - Cuidados de enfermagem para prevenir, controlar e aliviar condições clínicas do paciente",
      "Outros",
    ],
  },
  { chave: "titulo_publico", rotulo: "Título Público da Pesquisa", tipo: "texto" },
  { chave: "titulo_principal", rotulo: "Título Principal da Pesquisa", tipo: "texto" },
  { chave: "sera_pesquisador_principal", rotulo: "Será o pesquisador principal?", tipo: "sim_nao" },
  { chave: "contato_cientifico", rotulo: "Contato Científico", tipo: "texto" },
  { chave: "desenho", rotulo: "Desenho (resumo do método)", tipo: "texto_longo" },
  { chave: "financiamento", rotulo: "Financiamento", tipo: "texto" },
  { chave: "palavras_chave", rotulo: "Palavra-chave", tipo: "lista" },
  { chave: "resumo", rotulo: "Resumo", tipo: "texto_longo" },
  { chave: "introducao", rotulo: "Introdução", tipo: "texto_longo" },
  { chave: "hipotese", rotulo: "Hipótese", tipo: "texto_longo" },
  { chave: "objetivo_primario", rotulo: "Objetivo Primário", tipo: "texto_longo" },
  { chave: "objetivo_secundario", rotulo: "Objetivo Secundário", tipo: "texto_longo" },
  { chave: "metodologia_proposta", rotulo: "Metodologia Proposta", tipo: "texto_longo" },
  { chave: "criterio_inclusao", rotulo: "Critério de Inclusão", tipo: "texto_longo" },
  { chave: "criterio_exclusao", rotulo: "Critério de Exclusão", tipo: "texto_longo" },
  { chave: "riscos", rotulo: "Riscos", tipo: "texto_longo" },
  { chave: "beneficios", rotulo: "Benefícios", tipo: "texto_longo" },
  { chave: "metodologia_analise", rotulo: "Metodologia de Análise de dados", tipo: "texto_longo" },
  { chave: "desfecho_primario", rotulo: "Desfecho Primário", tipo: "texto_longo" },
  { chave: "desfecho_secundario", rotulo: "Desfecho Secundário", tipo: "texto_longo" },
  { chave: "tamanho_amostra_brasil", rotulo: "Tamanho da Amostra no Brasil", tipo: "texto" },
  { chave: "data_primeiro_recrutamento", rotulo: "Data do Primeiro Recrutamento", tipo: "texto" },
  { chave: "paises_recrutamento", rotulo: "Países de Recrutamento", tipo: "lista" },
  {
    chave: "fontes_secundarias",
    rotulo: "Haverá uso de fontes secundárias de dados (prontuários, dados demográficos, etc)?",
    tipo: "sim_nao",
  },
  {
    chave: "numero_individuos_centro",
    rotulo:
      "Número de indivíduos abordados pessoalmente, recrutados ou que sofrerão intervenção neste centro",
    tipo: "texto",
  },
  {
    chave: "grupos_participantes",
    rotulo: "Grupos em que serão divididos os participantes da pesquisa",
    tipo: "texto_longo",
  },
  { chave: "multicentrico_brasil", rotulo: "O estudo é multicêntrico no Brasil?", tipo: "sim_nao" },
  { chave: "instituicao_coparticipante", rotulo: "Instituição Coparticipante", tipo: "texto" },
  { chave: "dispensa_tcle", rotulo: "Propõe dispensa do TCLE?", tipo: "texto_longo" },
  {
    chave: "retencao_amostras",
    rotulo: "Haverá retenção de amostras para armazenamento em banco?",
    tipo: "sim_nao",
  },
  { chave: "cronograma_execucao", rotulo: "Cronograma de execução", tipo: "texto_longo" },
  { chave: "orcamento_financeiro", rotulo: "Orçamento Financeiro", tipo: "texto_longo" },
  {
    chave: "outras_informacoes",
    rotulo: "Outras informações, justificativas ou considerações",
    tipo: "texto_longo",
  },
  { chave: "bibliografia", rotulo: "Bibliografia", tipo: "texto_longo" },
  {
    chave: "anexos",
    rotulo:
      "Anexar Folha de Rosto e Incluir Arquivos (Projeto detalhado/Brochura, Cronograma, Declaração de instituição e infraestrutura, Declaração dos pesquisadores, TCLE/Termos de Assentimento/Justificativa de Ausência)",
    tipo: "anexo",
  },
  { chave: "manter_sigilo", rotulo: "Você quer manter o sigilo da pesquisa?", tipo: "sim_nao" },
];

export type ProtocoloCep = Record<string, string>;

export function protocoloCepVazio(): ProtocoloCep {
  return Object.fromEntries(CAMPOS_PROTOCOLO_CEP.map((campo) => [campo.chave, ""]));
}
