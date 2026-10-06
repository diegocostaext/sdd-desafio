"""Conversão para BRL conforme tabela de câmbio do envelope."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from reembolso.models import money


@dataclass(frozen=True)
class TabelaCambio:
    taxas_por_data: dict[str, dict[str, Decimal]]

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> TabelaCambio:
        taxas: dict[str, dict[str, Decimal]] = {}
        for data, moedas in raw.get("taxas", {}).items():
            taxas[data] = {
                moeda: Decimal(str(valor)) for moeda, valor in moedas.items()
            }
        return cls(taxas_por_data=taxas)

    @classmethod
    def apenas_brl(cls) -> TabelaCambio:
        return cls(taxas_por_data={})

    def _data_cotacao(self, data_despesa: str) -> str | None:
        candidatas = [d for d in self.taxas_por_data if d <= data_despesa]
        if not candidatas:
            return None
        return max(candidatas)

    def converter_para_brl(
        self, data_despesa: str, moeda: str, valor: Decimal
    ) -> tuple[Decimal | None, list[str]]:
        moeda = moeda.strip().upper()
        if moeda == "BRL":
            return money(valor), []

        data_cot = self._data_cotacao(data_despesa)
        if data_cot is None:
            return None, [
                "RN-013: nao ha cotacao em cambio.json para a data da despesa "
                f"({data_despesa}) nem em dia util anterior."
            ]

        taxas = self.taxas_por_data[data_cot]
        if moeda not in taxas:
            return None, [
                f"RN-013: moeda {moeda} sem cotacao em cambio.json "
                f"(data de referencia {data_cot})."
            ]

        taxa = taxas[moeda]
        valor_brl = money(valor * taxa)
        motivos = [
            f"RN-013: valor convertido de {moeda} para BRL usando cotacao de "
            f"{data_cot} (taxa {taxa})."
        ]
        if data_cot != data_despesa:
            motivos.append(
                "AMB-011: fim de semana/feriado — usada ultima cotacao de dia util "
                f"anterior ou igual a {data_despesa}."
            )
        return valor_brl, motivos
