"""CLI Unificada do Padronizador PPGSP/UFPA."""
import argparse
import sys
import os

from generators.qualificacao.builder import gerar_documento_qualificacao
from generators.dissertacao.builder import gerar_documento_dissertacao
from generators.tese.builder import gerar_documento_tese

def normalizar_nivel(valor):
    """Normaliza o nível para 'mestrado' ou 'doutorado'."""
    val = valor.strip().lower()
    if val in ["mestrado", "dissertacao", "dissertação"]:
        return "mestrado"
    elif val in ["doutorado", "tese"]:
        return "doutorado"
    return "mestrado"

def main():
    parser = argparse.ArgumentParser(
        prog="padronizador-ppgsp",
        description="Padronizador Automatizado de Documentos do PPGSP/UFPA (Resoluções 007, 009 e 010)."
    )

    subparsers = parser.add_subparsers(dest="comando", help="Tipo de documento acadêmico a ser gerado")

    # Comando: qualificacao
    p_qualif = subparsers.add_parser("qualificacao", help="Gera o Relatório de Qualificação (Resolução nº 009/2025)")
    p_qualif.add_argument("-i", "--input", default="inputs/qualificacao/projeto.docx", help="Caminho do arquivo de entrada")
    p_qualif.add_argument("-o", "--output", default="outputs/qualificacao/Relatorio_Qualificacao_Final.docx", help="Caminho do arquivo final gerado")
    p_qualif.add_argument(
        "-n", "--nivel",
        choices=["mestrado", "dissertacao", "dissertação", "doutorado", "tese"],
        default="mestrado",
        help="Nível do curso: mestrado (dissertação) ou doutorado (tese)"
    )
    p_qualif.add_argument("-a", "--assets", default="assets", help="Pasta contendo recursos visuais (brasao_ufpa.png)")

    # Comando: dissertacao
    p_dissert = subparsers.add_parser("dissertacao", help="Gera a Dissertação de Mestrado (Resolução nº 010/2025)")
    p_dissert.add_argument("-i", "--input", default="inputs/dissertacao/projeto.docx", help="Caminho do arquivo de entrada")
    p_dissert.add_argument("-o", "--output", default="outputs/dissertacao/Dissertacao_Final.docx", help="Caminho do arquivo final gerado")
    p_dissert.add_argument("-a", "--assets", default="assets", help="Pasta contendo recursos visuais")

    # Comando: tese
    p_tese = subparsers.add_parser("tese", help="Gera a Tese de Doutorado (Resolução nº 010/2025)")
    p_tese.add_argument("-i", "--input", default="inputs/tese/projeto.docx", help="Caminho do arquivo de entrada")
    p_tese.add_argument("-o", "--output", default="outputs/tese/Tese_Final.docx", help="Caminho do arquivo final gerado")
    p_tese.add_argument("-a", "--assets", default="assets", help="Pasta contendo recursos visuais")

    args = parser.parse_args()

    if not args.comando:
        parser.print_help()
        sys.exit(1)

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    nivel_normalizado = normalizar_nivel(getattr(args, "nivel", "mestrado"))

    print("=" * 70)
    print(f"[*] INICIANDO PADRONIZAÇÃO: {args.comando.upper()}")
    print(f"[*] NÍVEL DEFINIDO:        {nivel_normalizado.upper()} ({'Tese' if nivel_normalizado == 'doutorado' else 'Dissertação'})")
    print(f"[*] ARQUIVO DE ENTRADA:    {args.input}")
    print(f"[*] ARQUIVO DE SAÍDA:      {args.output}")
    print("=" * 70)

    if args.comando == "qualificacao":
        gerar_documento_qualificacao(args.input, args.output, nivel=nivel_normalizado, assets_dir=args.assets)
    elif args.comando == "dissertacao":
        gerar_documento_dissertacao(args.input, args.output, assets_dir=args.assets)
    elif args.comando == "tese":
        gerar_documento_tese(args.input, args.output, assets_dir=args.assets)

    print(f"\n[OK] Documento gerado com sucesso em: {args.output}\n")

if __name__ == '__main__':
    main()