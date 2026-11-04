"use client";

import { useEffect, useState } from "react";
import { FileCheck2 } from "lucide-react";

import { Stepper } from "@/components/Stepper";
import { Step1Upload } from "@/components/wizard/Step1Upload";
import { Step2Diagnostics } from "@/components/wizard/Step2Diagnostics";
import { Step3MetadataReview } from "@/components/wizard/Step3MetadataReview";
import { Step4Export } from "@/components/wizard/Step4Export";
import {
  ApiError,
  checkHealth,
  generateDocument,
  parseDocument,
  type AcademicLevel,
  type ParseResponse,
} from "@/lib/api";
import type { components } from "@/types/api";

type DocumentType = components["schemas"]["DocumentType"];
type WizardStep = 1 | 2 | 3 | 4;
type ApiStatus = "checking" | "online" | "offline";

function criarEstadoVazio(tipo: DocumentType, nivel: AcademicLevel): ParseResponse {
  return {
    documento_id: "",
    tipo_documento: tipo,
    nivel,
    metadata: {
      titulo: "",
      subtitulo: "",
      autor: "",
      orientador: "",
      coorientador: "",
      coordenador: "Prof. Dr. Edson Marcos Leal Soares Ramos",
      ano: "2026",
      local: "Belém-Pará",
      area_concentracao: "Segurança Pública, Justiça, Conflitos e Cidadania",
      linha_pesquisa: "Políticas, Gestão, Direitos Humanos, Criminalidade e Tecnologia da Informação",
      data_aprovacao: "Belém, Pará, ____ de _______________ de 2026.",
    },
    sections: {
      apresentacao: [],
      introducao: [],
      justificativa: [],
      problema: [],
      revisao: [],
      objetivo_geral: "",
      objetivos_especificos: [],
      hipotese: [],
      metodologia_natureza: [],
      metodologia_locus: "",
      metodologia_participantes: "",
      metodologia_fontes: [],
      metodologia_coleta: [],
      metodologia_etica: "",
      metodologia_analise: "",
      referencias: [],
    },
    banca: [
      { nome: "", funcao: "Orientador(a)", instituicao: "Universidade Federal do Pará" },
      { nome: "", funcao: "Avaliador(a) Interno(a)", instituicao: "Universidade Federal do Pará" },
      { nome: "", funcao: "Avaliador(a) Externo(a)", instituicao: "" },
    ],
    siglas: [
      ["UFPA", "Universidade Federal do Pará"],
      ["PPGSP", "Programa de Pós-Graduação em Segurança Pública"],
      ["CIAP", "Centro Integrado de Atenção Psicossocial"],
      ["PMPA", "Polícia Militar do Pará"],
    ],
    ptts: [],
    lacunas: [],
    conformidade_ptt: {
      valido: false,
      total: 0,
      prop_alta: 0,
      mensagem: "",
    },
  };
}

const INITIAL = {
  step: 1 as WizardStep,
  tipoDocumento: "qualificacao" as DocumentType,
  nivel: "mestrado" as AcademicLevel,
};

export default function Home() {
  const [status, setStatus] = useState<ApiStatus>("checking");
  const [step, setStep] = useState<WizardStep>(INITIAL.step);
  const [tipoDocumento, setTipoDocumento] = useState<DocumentType>(INITIAL.tipoDocumento);
  const [nivel, setNivel] = useState<AcademicLevel>(INITIAL.nivel);
  const [file, setFile] = useState<File | null>(null);
  const [parsedData, setParsedData] = useState<ParseResponse | null>(null);
  const [subtitulo, setSubtitulo] = useState("");
  const [isParsing, setIsParsing] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fileHint, setFileHint] = useState<string | null>(null);
  const [downloaded, setDownloaded] = useState(false);
  const [preenchimentoDireto, setPreenchimentoDireto] = useState(false);

  useEffect(() => {
    let active = true;
    checkHealth()
      .then((body) => {
        if (active) setStatus(body.status === "ok" ? "online" : "offline");
      })
      .catch(() => {
        if (active) setStatus("offline");
      });
    return () => {
      active = false;
    };
  }, []);

  const statusLabel =
    status === "checking" ? "Verificando API…" : status === "online" ? "Online" : "Offline";

  function escolherTipo(tipo: DocumentType) {
    setTipoDocumento(tipo);
    if (tipo === "tese") setNivel("doutorado");
    if (tipo === "dissertacao") setNivel("mestrado");
  }

  function escolherArquivo(next: File | null) {
    setFile(next);
    setFileHint(next ? null : "Selecione um arquivo .docx.");
  }

  async function analisar() {
    if (!file) {
      setFileHint("Selecione um arquivo .docx.");
      return;
    }
    setIsParsing(true);
    setError(null);
    setFileHint(null);
    try {
      const data = await parseDocument(file, nivel);
      const vazio = criarEstadoVazio(tipoDocumento, nivel);
      setParsedData({
        ...data,
        tipo_documento: tipoDocumento,
        nivel,
        sections: data.sections ?? vazio.sections,
      });
      setSubtitulo(data.metadata.subtitulo ?? "");
      setDownloaded(false);
      setPreenchimentoDireto(false);
      setStep(2);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Não foi possível analisar o documento.");
    } finally {
      setIsParsing(false);
    }
  }

  function iniciarPreenchimentoDireto() {
    setParsedData(criarEstadoVazio(tipoDocumento, nivel));
    setSubtitulo("");
    setError(null);
    setFileHint(null);
    setDownloaded(false);
    setPreenchimentoDireto(true);
    setStep(3);
  }

  async function gerar() {
    if (!parsedData) {
      setError("Analise novamente o arquivo em Documento de origem antes de gerar.");
      return;
    }
    if (!preenchimentoDireto && !parsedData.documento_id) {
      setError("Analise novamente o arquivo em Documento de origem antes de gerar.");
      return;
    }
    setIsGenerating(true);
    setError(null);
    try {
      const tituloBase = parsedData.metadata.titulo.trim();
      const complemento = subtitulo.trim();
      const titulo =
        complemento && !tituloBase.toLowerCase().includes(complemento.toLowerCase())
          ? `${tituloBase}${tituloBase ? ": " : ""}${complemento}`
          : tituloBase;
      const blob = await generateDocument({
        documento_id: parsedData.documento_id,
        tipo_documento: tipoDocumento,
        nivel,
        metadata: { ...parsedData.metadata, titulo },
        sections: parsedData.sections,
        banca: parsedData.banca,
        siglas: parsedData.siglas,
        ptts: parsedData.ptts,
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "Documento_Padronizado_PPGSP.docx";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setDownloaded(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Não foi possível gerar o documento.");
    } finally {
      setIsGenerating(false);
    }
  }

  function reiniciar() {
    setStep(1);
    setTipoDocumento(INITIAL.tipoDocumento);
    setNivel(INITIAL.nivel);
    setFile(null);
    setParsedData(null);
    setSubtitulo("");
    setError(null);
    setFileHint(null);
    setDownloaded(false);
    setPreenchimentoDireto(false);
  }

  return (
    <div className="flex flex-1 flex-col bg-[#f4f1ea] text-[#1c1915]">
      <header className="border-b border-[#d9d1c3] bg-[#0f3d32] text-[#f7f3ea]">
        <div className="mx-auto flex w-full max-w-5xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-xs tracking-[0.22em] uppercase">UFPA · PPGSP</p>
            <p className="mt-1 text-sm font-medium">Padronizador PPGSP/UFPA</p>
          </div>
          <div className="inline-flex items-center gap-2 text-xs" role="status">
            <FileCheck2 className="size-4" aria-hidden />
            <span>API {statusLabel}</span>
          </div>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-5xl flex-1 flex-col px-6 py-8">
        <Stepper step={step} />
        <div className="mt-8">
          {step === 1 && (
            <Step1Upload
              file={file}
              tipoDocumento={tipoDocumento}
              nivel={nivel}
              isParsing={isParsing}
              error={error ?? fileHint}
              onFile={escolherArquivo}
              onTipo={escolherTipo}
              onNivel={setNivel}
              onAnalyze={analisar}
              onStartDirect={iniciarPreenchimentoDireto}
            />
          )}
          {step === 2 && parsedData && (
            <Step2Diagnostics
              data={parsedData}
              nivel={nivel}
              onBack={() => setStep(1)}
              onNext={() => setStep(3)}
            />
          )}
          {step === 3 && parsedData && (
            <Step3MetadataReview
              data={parsedData}
              subtitulo={subtitulo}
              onSubtitulo={setSubtitulo}
              onChange={setParsedData}
              onBack={() => setStep(preenchimentoDireto ? 1 : 2)}
              onNext={() => {
                setError(null);
                setStep(4);
              }}
            />
          )}
          {step === 4 && parsedData && (
            <Step4Export
              tipoDocumento={tipoDocumento}
              nivel={nivel}
              data={parsedData}
              isGenerating={isGenerating}
              error={error}
              downloaded={downloaded}
              onGenerate={gerar}
              onReset={reiniciar}
              onBack={() => setStep(3)}
            />
          )}
        </div>
      </main>
    </div>
  );
}
