import type { components } from "@/types/api";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export type AcademicLevel = components["schemas"]["AcademicLevel"];
export type PTTItem = components["schemas"]["PTTItem"];
export type PTTValidationResult = components["schemas"]["PTTValidationResult"];

export interface DocumentSections {
  apresentacao?: string[];
  introducao?: string[];
  justificativa?: string[];
  problema?: string[];
  revisao?: string[];
  objetivo_geral?: string;
  objetivos_especificos?: string[];
  hipotese?: string[];
  metodologia_natureza?: string[];
  metodologia_locus?: string;
  metodologia_participantes?: string;
  metodologia_fontes?: string[];
  metodologia_coleta?: string[];
  metodologia_etica?: string;
  metodologia_analise?: string;
  referencias?: string[];
}

type SchemaParseResponse = components["schemas"]["ParseResponse"];
type SchemaGenerateRequest = components["schemas"]["GenerateRequest"];

export type ParseResponse = Omit<SchemaParseResponse, "metadata"> & {
  metadata: components["schemas"]["DocumentMetadata"] & {
    data_aprovacao?: string;
  };
  sections: DocumentSections;
};

export type GenerateRequest = SchemaGenerateRequest & {
  sections: DocumentSections;
};

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown };
    if (typeof body.detail === "string") return body.detail;
    if (body.detail != null) return JSON.stringify(body.detail);
  } catch {
    /* resposta sem JSON */
  }
  return `A API respondeu com status ${response.status}.`;
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(`${API_BASE_URL}/health`, {
    cache: "no-store",
  });
  if (!response.ok) throw new ApiError(await readError(response), response.status);
  return response.json() as Promise<{ status: string }>;
}

export async function parseDocument(
  file: File,
  nivel: AcademicLevel,
): Promise<ParseResponse> {
  const form = new FormData();
  form.append("file", file);
  form.append("nivel", nivel);
  const response = await fetch(`${API_BASE_URL}/api/v1/parse`, {
    method: "POST",
    body: form,
  });
  if (!response.ok) throw new ApiError(await readError(response), response.status);
  return response.json() as Promise<ParseResponse>;
}

export async function validatePTTs(
  ptts: PTTItem[],
  nivel: AcademicLevel,
): Promise<PTTValidationResult> {
  const response = await fetch(`${API_BASE_URL}/api/v1/validate-ptts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ ptts, nivel }),
  });
  if (!response.ok) throw new ApiError(await readError(response), response.status);
  return response.json() as Promise<PTTValidationResult>;
}

export async function generateDocument(payload: GenerateRequest): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/v1/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new ApiError(await readError(response), response.status);
  return response.blob();
}
