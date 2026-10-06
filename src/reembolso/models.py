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
        )


@dataclass
class ItemResultado:
    id: str
    status: str
    valor_informado: Decimal
    valor_reembolsavel: Decimal
    motivos: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "status": self.status,
            "valor_informado": float(self.valor_informado),
            "valor_reembolsavel": float(self.valor_reembolsavel),
            "motivos": self.motivos,
        }


@dataclass
class ResultadoCalculo:
    colaborador_id: str
    periodo_competencia: str
    total_solicitado: Decimal
    total_reembolsavel: Decimal
    itens: list[ItemResultado]

    def to_dict(self) -> dict[str, Any]:
        return {
            "colaborador": {"id": self.colaborador_id},
            "periodo": {"competencia": self.periodo_competencia},
            "total_solicitado": float(self.total_solicitado),
            "total_reembolsavel": float(self.total_reembolsavel),
            "itens": [i.to_dict() for i in self.itens],
        }
