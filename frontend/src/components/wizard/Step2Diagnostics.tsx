"use client";

import { Badge } from "@/components/ui/Badge";
import { Card } from "@/components/ui/Card";
import { ProgressBar } from "@/components/ui/ProgressBar";
import type { AcademicLevel, ParseResponse } from "@/lib/api";
import { minimoPtts, resumoImpacto } from "@/lib/ptt";

export function Step2Diagnostics({
  data,
  nivel,
  onBack,
  onNext,
}: {
  data: ParseResponse;
  nivel: AcademicLevel;
  onBack: () => void;
  onNext: () => void;
}) {
  const resumo = resumoImpacto(data.ptts);
  const minimo = minimoPtts(nivel);
  const carteiraOk =
    data.conformidade_ptt.valido &&
    resumo.total >= minimo &&
    resumo.propAlto >= 0.5 &&
    resumo.propMedio <= 0.25 &&
    resumo.propBaixo <= 0.25;
  const lacunas = data.lacunas.length;
  const estruturaOk = lacunas === 0;

  return (
    <div className="flex flex-col gap-5">
      <Card
        title="Resolução nº 007/2025 — Carteira de PTTs"
        description="Impacto alto exige pelo menos 50%. Impacto médio e baixo ficam em no máximo 25% cada."
        action={
          <Badge tone={carteiraOk ? "success" : "danger"}>
            {carteiraOk ? "Carteira conforme" : "Carteira fora dos critérios"}
          </Badge>
        }
      >
        <p className="mb-3 text-sm">
          <span className="text-2xl font-semibold text-[#0f3d32]">{resumo.total}</span>
          <span className="text-[#5c564c]"> produtos identificados · mínimo exigido: {minimo}</span>
        </p>
        <ProgressBar
          caption={`${resumo.alto} alto, ${resumo.medio} médio, ${resumo.baixo} baixo`}
          segments={[
            { key: "alto", label: "Alto", value: resumo.alto, className: "bg-emerald-600" },
            { key: "medio", label: "Médio", value: resumo.medio, className: "bg-amber-400" },
            { key: "baixo", label: "Baixo", value: resumo.baixo, className: "bg-stone-400" },
            { key: "outro", label: "Não classificado", value: resumo.outro, className: "bg-red-400" },
          ]}
        />
        <p className="mt-3 text-xs text-[#6b645a]">
          Alto {Math.round(resumo.propAlto * 100)}% · Médio {Math.round(resumo.propMedio * 100)}% · Baixo{" "}
          {Math.round(resumo.propBaixo * 100)}%
        </p>
        {!carteiraOk && (
          <p className="mt-4 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-950" role="alert">
            {data.conformidade_ptt.mensagem ||
              "A carteira não atende aos critérios da Resolução nº 007/2025."}
          </p>
        )}
      </Card>

      <Card
        title="Resoluções nº 009/2025 e 010/2025 — Estrutura e lacunas"
        action={
          <Badge tone={estruturaOk ? "success" : "warning"}>
            {estruturaOk ? "Conforme" : "Atenção: Lacunas Encontradas"}
          </Badge>
        }
      >
        {estruturaOk ? (
          <p className="text-sm text-[#4a453c]">Nenhuma lacuna estrutural foi identificada pelo parser.</p>
        ) : (
          <ul className="flex flex-col gap-3">
            {data.lacunas.map((lacuna, index) => (
              <li key={`${lacuna.codigo}-${index}`} className="rounded-lg border border-[#efe8dc] px-3 py-2">
                <p className="text-sm font-medium text-[#1c1915]">
                  {lacuna.secao || "Seção"}
                  {lacuna.codigo ? ` · ${lacuna.codigo}` : ""}
                </p>
                <p className="mt-1 text-sm text-[#4a453c]">
                  {lacuna.recomendacao || lacuna.encontrado || lacuna.regra}
                </p>
              </li>
            ))}
          </ul>
        )}
      </Card>

      <div className="flex justify-between gap-3">
        <button
          type="button"
          onClick={onBack}
          className="inline-flex h-11 items-center rounded-md border border-[#d9d1c3] bg-white px-4 text-sm font-medium"
        >
          Voltar
        </button>
        <button
          type="button"
          onClick={onNext}
          className="inline-flex h-11 items-center rounded-md bg-[#0f3d32] px-5 text-sm font-medium text-white hover:bg-[#145244]"
        >
          Revisar Dados para Geração
        </button>
      </div>
    </div>
  );
}
