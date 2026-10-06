"""CLI: python -m reembolso calcular --input ... --output ... [--politica] [--cambio]"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from reembolso.cambio import TabelaCambio
from reembolso.engine import calcular
from reembolso.politica_config import PoliticaConfig


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="reembolso",
        description="Motor de calculo de reembolso de despesas corporativas.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    calc = sub.add_parser("calcular", help="Calcula reembolso a partir de JSON de entrada.")
    calc.add_argument("--input", required=True, type=Path, help="Arquivo JSON de despesas.")
    calc.add_argument("--output", required=True, type=Path, help="Arquivo JSON de saida.")
    calc.add_argument(
        "--politica",
        type=Path,
        help="Arquivo politica-v4.json (v3-compat se omitido).",
    )
    calc.add_argument(
        "--cambio",
        type=Path,
        help="Arquivo cambio.json (obrigatorio com despesas em moeda estrangeira).",
    )

    args = parser.parse_args(argv)

    if args.comando == "calcular":
        try:
            raw = json.loads(args.input.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Erro ao ler entrada: {exc}", file=sys.stderr)
            return 1

        politica = PoliticaConfig.v3_compat()
        politica_versao = "v3-compat"
        cambio = TabelaCambio.apenas_brl()

        if args.politica:
            try:
                politica_raw = json.loads(args.politica.read_text(encoding="utf-8"))
                politica = PoliticaConfig.from_dict(politica_raw)
                politica_versao = str(politica_raw.get("versao", "v4"))
            except (OSError, json.JSONDecodeError, KeyError) as exc:
                print(f"Erro ao ler politica: {exc}", file=sys.stderr)
                return 1

        if args.cambio:
            try:
                cambio = TabelaCambio.from_dict(
                    json.loads(args.cambio.read_text(encoding="utf-8"))
                )
            except (OSError, json.JSONDecodeError) as exc:
                print(f"Erro ao ler cambio: {exc}", file=sys.stderr)
                return 1

        resultado = calcular(
            raw,
            politica=politica,
            cambio=cambio,
            politica_versao=politica_versao,
        )
        args.output.write_text(
            json.dumps(resultado.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
