"""CLI: PYTHONPATH=src python -m reembolso calcular --input despesas.json --output resultado.json"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from reembolso.engine import calcular


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="reembolso",
        description="Motor de calculo de reembolso de despesas corporativas.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    calc = sub.add_parser("calcular", help="Calcula reembolso a partir de JSON de entrada.")
    calc.add_argument("--input", required=True, type=Path, help="Arquivo JSON de despesas.")
    calc.add_argument("--output", required=True, type=Path, help="Arquivo JSON de saida.")

    args = parser.parse_args(argv)

    if args.comando == "calcular":
        try:
            raw = json.loads(args.input.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Erro ao ler entrada: {exc}", file=sys.stderr)
            return 1

        resultado = calcular(raw)
        args.output.write_text(
            json.dumps(resultado.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
