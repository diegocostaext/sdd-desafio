"""Núcleo de regras de negócio do motor de reembolso."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from reembolso.models import Despesa, ItemResultado, ResultadoCalculo, money
from reembolso.policy import (
    CATEGORIAS_ELEGIVEIS,
    FATOR_VIAGEM,
    LIMITE_DIARIO_POR_CATEGORIA,
    LIMITE_NF_OBRIGATORIA,
)


def normalizar_categoria(categoria: str) -> str:
    return categoria.strip().lower().replace("-", "_")


def chave_duplicata(d: Despesa) -> tuple[str, str, str, Decimal, str]:
    cat = normalizar_categoria(d.categoria)
    return (d.data, cat, d.fornecedor.strip(), d.valor, d.descricao.strip())


def dentro_competencia(data: str, inicio: str, fim: str) -> bool:
    return inicio <= data <= fim


def limite_diario(categoria: str, em_viagem: bool) -> Decimal | None:
    cat = normalizar_categoria(categoria)
    base = LIMITE_DIARIO_POR_CATEGORIA.get(cat)
    if base is None:
        return None
    if em_viagem:
        return money(base * FATOR_VIAGEM)
    return base


def exige_nota_fiscal(valor: Decimal) -> bool:
    return valor > LIMITE_NF_OBRIGATORIA


def classificar_status(valor_informado: Decimal, valor_reembolsavel: Decimal) -> str:
    if valor_reembolsavel <= Decimal("0"):
        return "nao_reembolsavel"
    if valor_reembolsavel < valor_informado:
        return "reembolsado_parcial"
    return "reembolsado_integral"


def calcular(payload: dict[str, Any]) -> ResultadoCalculo:
    colaborador_id = str(payload["colaborador"]["id"])
    periodo = payload["periodo"]
    competencia = str(periodo["competencia"])
    inicio = str(periodo["inicio"])
    fim = str(periodo["fim"])
    em_viagem = bool(payload.get("em_viagem", False))

    despesas = [Despesa.from_dict(d) for d in payload["despesas"]]
    despesas.sort(key=lambda d: (d.data, d.id))

    vistos_duplicata: set[tuple[str, str, str, Decimal, str]] = set()
    uso_diario: dict[tuple[str, str], Decimal] = defaultdict(lambda: Decimal("0"))

    itens: list[ItemResultado] = []
    total_solicitado = Decimal("0")
    total_reembolsavel = Decimal("0")

    for d in despesas:
        motivos: list[str] = []
        cat_norm = normalizar_categoria(d.categoria)
        valor_reembolsavel = Decimal("0")

        if d.valor > Decimal("0"):
            total_solicitado += d.valor

        if not dentro_competencia(d.data, inicio, fim):
            motivos.append(
                "RN-006: data fora do periodo de competencia "
                f"({d.data} nao esta entre {inicio} e {fim})."
            )
            itens.append(
                ItemResultado(
                    id=d.id,
                    status="nao_reembolsavel",
                    valor_informado=d.valor,
                    valor_reembolsavel=Decimal("0"),
                    motivos=motivos,
                )
            )
            continue

        dup = chave_duplicata(d)
        if dup in vistos_duplicata:
            motivos.append(
                "RN-007: duplicata detectada (mesma data, categoria, fornecedor, "
                "valor e descricao); apenas a primeira ocorrencia e processada."
            )
            itens.append(
                ItemResultado(
                    id=d.id,
                    status="nao_reembolsavel",
                    valor_informado=d.valor,
                    valor_reembolsavel=Decimal("0"),
                    motivos=motivos,
                )
            )
            continue
        vistos_duplicata.add(dup)

        if cat_norm not in CATEGORIAS_ELEGIVEIS:
            motivos.append(
                f"RN-008: categoria '{d.categoria}' nao esta coberta pela politica."
            )
            itens.append(
                ItemResultado(
                    id=d.id,
                    status="nao_reembolsavel",
                    valor_informado=d.valor,
                    valor_reembolsavel=Decimal("0"),
                    motivos=motivos,
                )
            )
            continue

        if d.valor < Decimal("0"):
            chave_dia = (d.data, cat_norm)
            credito = min(-d.valor, uso_diario[chave_dia])
            uso_diario[chave_dia] -= credito
            valor_reembolsavel = -credito
            motivos.append(
                "RN-010: estorno reduz o reembolso ja acumulado na categoria "
                f"para o dia {d.data} (ate zerar o saldo do dia)."
            )
            status = classificar_status(d.valor, valor_reembolsavel)
            itens.append(
                ItemResultado(
                    id=d.id,
                    status=status,
                    valor_informado=d.valor,
                    valor_reembolsavel=valor_reembolsavel,
                    motivos=motivos,
                )
            )
            total_reembolsavel += valor_reembolsavel
            continue

        if exige_nota_fiscal(d.valor) and not d.tem_nota_fiscal:
            motivos.append(
                "RN-004: nota fiscal obrigatoria para despesas com valor "
                f"estritamente maior que R$ {LIMITE_NF_OBRIGATORIA}."
            )
            itens.append(
                ItemResultado(
                    id=d.id,
                    status="nao_reembolsavel",
                    valor_informado=d.valor,
                    valor_reembolsavel=Decimal("0"),
                    motivos=motivos,
                )
            )
            continue

        limite = limite_diario(cat_norm, em_viagem)
        chave_dia = (d.data, cat_norm)
        usado = uso_diario[chave_dia]
        restante = money(limite - usado) if limite is not None else d.valor

        if restante <= Decimal("0"):
            valor_reembolsavel = Decimal("0")
            motivos.append(
                f"RN-001: limite diario de R$ {limite} para {cat_norm} "
                f"em {d.data} ja foi atingido."
            )
        else:
            valor_reembolsavel = min(d.valor, restante)
            uso_diario[chave_dia] = money(usado + valor_reembolsavel)
            if valor_reembolsavel < d.valor:
                motivos.append(
                    f"RN-003: reembolso parcial — excedente de R$ "
                    f"{money(d.valor - valor_reembolsavel)} acima do limite "
                    f"diario de R$ {limite} para {cat_norm}."
                )
            else:
                motivos.append("RN-001: valor dentro do limite diario da categoria.")

        if em_viagem and limite is not None:
            motivos.append("RN-005: limites ampliados em 50% por colaborador em viagem.")

        status = classificar_status(d.valor, valor_reembolsavel)
        itens.append(
            ItemResultado(
                id=d.id,
                status=status,
                valor_informado=d.valor,
                valor_reembolsavel=valor_reembolsavel,
                motivos=motivos,
            )
        )
        total_reembolsavel += valor_reembolsavel

    total_reembolsavel = money(max(total_reembolsavel, Decimal("0")))
    total_solicitado = money(total_solicitado)

    return ResultadoCalculo(
        colaborador_id=colaborador_id,
        periodo_competencia=competencia,
        total_solicitado=total_solicitado,
        total_reembolsavel=total_reembolsavel,
        itens=itens,
    )
