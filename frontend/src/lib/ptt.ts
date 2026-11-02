import type { PTTItem } from "@/lib/api";

export type ImpactoFaixa = "alto" | "medio" | "baixo" | "outro";

export function faixaImpacto(impacto: string): ImpactoFaixa {
  const texto = impacto.trim().toLowerCase().normalize("NFD").replace(/\p{M}/gu, "");
  if (texto.startsWith("alt")) return "alto";
  if (texto.startsWith("med")) return "medio";
  if (texto.startsWith("baix")) return "baixo";
  return "outro";
}

export function minimoPtts(nivel: "mestrado" | "doutorado") {
  return nivel === "doutorado" ? 8 : 4;
}

export function resumoImpacto(ptts: PTTItem[]) {
  const contagem = { alto: 0, medio: 0, baixo: 0, outro: 0 };
  for (const item of ptts) contagem[faixaImpacto(item.impacto)] += 1;
  const total = ptts.length;
  const proporcao = (n: number) => (total === 0 ? 0 : n / total);
  return {
    total,
    ...contagem,
    propAlto: proporcao(contagem.alto),
    propMedio: proporcao(contagem.medio),
    propBaixo: proporcao(contagem.baixo),
  };
}
