"""Carregamento da política v4 (externa) e compatibilidade v3."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from reembolso.models import money


@dataclass(frozen=True)
class PoliticaConfig:
    padrao: dict[str, Decimal]
    centros_custo: dict[str, dict[str, Decimal]]
    nf_obrigatoria_acima_de: Decimal
    acrescimo_em_viagem_percentual: Decimal

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> PoliticaConfig:
        padrao = {
            cat: money(info["limite"])
            for cat, info in raw["padrao"].items()
        }
        centros: dict[str, dict[str, Decimal]] = {}
        for cc, cats in raw.get("centros_custo", {}).items():
            centros[cc] = {cat: money(info["limite"]) for cat, info in cats.items()}
        return cls(
            padrao=padrao,
            centros_custo=centros,
            nf_obrigatoria_acima_de=money(raw.get("nota_fiscal_obrigatoria_acima_de", 100)),
            acrescimo_em_viagem_percentual=Decimal(
                str(raw.get("acrescimo_em_viagem_percentual", 50))
            ),
        )

    @classmethod
    def v3_compat(cls) -> PoliticaConfig:
        """Política única equivalente à v3 (sem variação por centro de custo)."""
        return cls.from_dict(
            {
                "padrao": {
                    "alimentacao": {"limite": 60.00, "periodicidade": "dia"},
                    "transporte_urbano": {"limite": 80.00, "periodicidade": "dia"},
                    "hospedagem": {"limite": 250.00, "periodicidade": "diaria"},
                },
                "centros_custo": {},
                "nota_fiscal_obrigatoria_acima_de": 100.00,
                "acrescimo_em_viagem_percentual": 50,
            }
        )

    def tabela_centro(self, centro_custo: str) -> dict[str, Decimal]:
        if centro_custo in self.centros_custo:
            return self.centros_custo[centro_custo]
        return self.padrao

    def categoria_coberta(self, centro_custo: str, categoria: str) -> bool:
        return categoria in self.tabela_centro(centro_custo)

    def limite_diario(
        self, centro_custo: str, categoria: str, em_viagem: bool
    ) -> Decimal | None:
        tabela = self.tabela_centro(centro_custo)
        if categoria not in tabela:
            return None
        base = tabela[categoria]
        if em_viagem:
            fator = Decimal("1") + self.acrescimo_em_viagem_percentual / Decimal("100")
            return money(base * fator)
        return base
