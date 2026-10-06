"""Limites e categorias elegíveis (representação técnica da política v3)."""

from decimal import Decimal

LIMITE_ALIMENTACAO_DIA = Decimal("60.00")
LIMITE_TRANSPORTE_DIA = Decimal("80.00")
LIMITE_HOSPEDAGEM_DIARIA = Decimal("250.00")
LIMITE_NF_OBRIGATORIA = Decimal("100.00")
FATOR_VIAGEM = Decimal("1.5")

CATEGORIAS_ELEGIVEIS = frozenset(
    {"alimentacao", "transporte_urbano", "hospedagem"}
)

LIMITE_DIARIO_POR_CATEGORIA = {
    "alimentacao": LIMITE_ALIMENTACAO_DIA,
    "transporte_urbano": LIMITE_TRANSPORTE_DIA,
    "hospedagem": LIMITE_HOSPEDAGEM_DIARIA,
}
