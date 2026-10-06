from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any


def money(value: Decimal | str | float | int) -> Decimal:
    return Decimal(str(value)).quantize(Decimal("0.01"))


@dataclass(frozen=True)
class Despesa:
    id: str
    data: str
    categoria: str
    descricao: str
    fornecedor: str
    valor: Decimal
    tem_nota_fiscal: bool
    moeda: str = "BRL"

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> Despesa:
        return cls(
            id=str(raw["id"]),
            data=str(raw["data"]),
            categoria=str(raw["categoria"]),
            descricao=str(raw.get("descricao", "")),
            fornecedor=str(raw.get("fornecedor", "")),
            valor=money(raw["valor"]),
            tem_nota_fiscal=bool(raw.get("tem_nota_fiscal", False)),
            moeda=str(raw.get("moeda", "BRL")).upper(),
        )


@dataclass
class ItemResultado:
    id: str
    status: str
    valor_informado: Decimal
    valor_reembolsavel: Decimal
    motivos: list[str] = field(default_factory=list)
    moeda: str = "BRL"
    valor_em_brl: Decimal | None = None

    def to_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "id": self.id,
            "status": self.status,
            "valor_informado": float(self.valor_informado),
            "valor_reembolsavel": float(self.valor_reembolsavel),
            "motivos": self.motivos,
        }
        if self.moeda != "BRL":
            out["moeda"] = self.moeda
        if self.valor_em_brl is not None:
            out["valor_em_brl"] = float(self.valor_em_brl)
        return out


@dataclass
class ResultadoCalculo:
    colaborador_id: str
    periodo_competencia: str
    total_solicitado: Decimal
    total_reembolsavel: Decimal
    itens: list[ItemResultado]
    politica_versao: str = "v3-compat"

    def to_dict(self) -> dict[str, Any]:
        return {
            "colaborador": {"id": self.colaborador_id},
            "periodo": {"competencia": self.periodo_competencia},
            "politica_versao": self.politica_versao,
            "total_solicitado": float(self.total_solicitado),
            "total_reembolsavel": float(self.total_reembolsavel),
            "itens": [i.to_dict() for i in self.itens],
        }
