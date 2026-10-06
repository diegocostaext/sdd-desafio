"""Núcleo de regras de negócio do motor de reembolso."""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal
from typing import Any

from reembolso.cambio import TabelaCambio
from reembolso.models import Despesa, ItemResultado, ResultadoCalculo, money
from reembolso.politica_config import PoliticaConfig


def normalizar_categoria(categoria: str) -> str:
    return categoria.strip().lower().replace("-", "_")


def chave_duplicata(d: Despesa) -> tuple[str, str, str, Decimal, str, str]:
    cat = normalizar_categoria(d.categoria)
    return (d.data, cat, d.fornecedor.strip(), d.valor, d.descricao.strip(), d.moeda)


def dentro_competencia(data: str, inicio: str, fim: str) -> bool:
    return inicio <= data <= fim


def exige_nota_fiscal(valor_brl: Decimal, limite: Decimal) -> bool:
    return valor_brl > limite


def classificar_status(valor_ref_brl: Decimal, valor_reembolsavel: Decimal) -> str:
    if valor_reembolsavel <= Decimal("0"):
        return "nao_reembolsavel"
    if valor_reembolsavel < valor_ref_brl:
        return "reembolsado_parcial"
    return "reembolsado_integral"


def calcular(
    payload: dict[str, Any],
    *,
    politica: PoliticaConfig | None = None,
    cambio: TabelaCambio | None = None,
    politica_versao: str = "v3-compat",
) -> ResultadoCalculo:
    politica = politica or PoliticaConfig.v3_compat()
    cambio = cambio or TabelaCambio.apenas_brl()

    colaborador = payload["colaborador"]
    colaborador_id = str(colaborador["id"])
    centro_custo = str(colaborador.get("centro_custo", ""))
    periodo = payload["periodo"]
    competencia = str(periodo["competencia"])
    inicio = str(periodo["inicio"])
    fim = str(periodo["fim"])
    em_viagem = bool(payload.get("em_viagem", False))

    despesas = [Despesa.from_dict(d) for d in payload["despesas"]]
    despesas.sort(key=lambda d: (d.data, d.id))

    vistos_duplicata: set[tuple[str, str, str, Decimal, str, str]] = set()
    uso_diario: dict[tuple[str, str], Decimal] = defaultdict(lambda: Decimal("0"))

    itens: list[ItemResultado] = []
    total_solicitado = Decimal("0")
    total_reembolsavel = Decimal("0")

    for d in despesas:
        motivos: list[str] = []
        cat_norm = normalizar_categoria(d.categoria)
        valor_reembolsavel = Decimal("0")

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
                    moeda=d.moeda,
                )
            )
            continue

        dup = chave_duplicata(d)
        if dup in vistos_duplicata:
            motivos.append(
                "RN-007: duplicata detectada (mesma data, categoria, fornecedor, "
                "valor, descricao e moeda); apenas a primeira ocorrencia e processada."
            )
            itens.append(
                ItemResultado(
                    id=d.id,
                    status="nao_reembolsavel",
                    valor_informado=d.valor,
                    valor_reembolsavel=Decimal("0"),
                    motivos=motivos,
                    moeda=d.moeda,
                )
            )
            continue
        vistos_duplicata.add(dup)

        valor_brl, motivos_cambio = cambio.converter_para_brl(d.data, d.moeda, d.valor)
        motivos.extend(motivos_cambio)
        if valor_brl is None:
            itens.append(
                ItemResultado(
                    id=d.id,
                    status="nao_reembolsavel",
                    valor_informado=d.valor,
                    valor_reembolsavel=Decimal("0"),
                    motivos=motivos,
                    moeda=d.moeda,
                )
            )
            continue

        if d.valor > Decimal("0"):
            total_solicitado += valor_brl

        if not politica.categoria_coberta(centro_custo, cat_norm):
            motivos.append(
                f"RN-008: categoria '{d.categoria}' nao esta coberta pela politica "
                f"do centro de custo {centro_custo or '(padrao)'}."
            )
            itens.append(
                ItemResultado(
                    id=d.id,
                    status="nao_reembolsavel",
                    valor_informado=d.valor,
                    valor_reembolsavel=Decimal("0"),
                    motivos=motivos,
                    moeda=d.moeda,
                    valor_em_brl=valor_brl,
                )
            )
            continue

        limite = politica.limite_diario(centro_custo, cat_norm, em_viagem)
        if limite is not None and limite <= Decimal("0"):
            motivos.append(
                f"RN-014: categoria '{cat_norm}' com limite zero para {centro_custo}."
            )
            itens.append(
                ItemResultado(
                    id=d.id,
                    status="nao_reembolsavel",
                    valor_informado=d.valor,
                    valor_reembolsavel=Decimal("0"),
                    motivos=motivos,
                    moeda=d.moeda,
                    valor_em_brl=valor_brl,
                )
            )
            continue

        if valor_brl < Decimal("0"):
            chave_dia = (d.data, cat_norm)
            credito = min(-valor_brl, uso_diario[chave_dia])
            uso_diario[chave_dia] -= credito
            valor_reembolsavel = -credito
            motivos.append(
                "RN-010: estorno reduz o reembolso ja acumulado na categoria "
                f"para o dia {d.data} (ate zerar o saldo do dia)."
            )
            status = classificar_status(valor_brl, valor_reembolsavel)
            itens.append(
                ItemResultado(
                    id=d.id,
                    status=status,
                    valor_informado=d.valor,
                    valor_reembolsavel=valor_reembolsavel,
                    motivos=motivos,
                    moeda=d.moeda,
                    valor_em_brl=valor_brl,
                )
            )
            total_reembolsavel += valor_reembolsavel
            continue

        if exige_nota_fiscal(valor_brl, politica.nf_obrigatoria_acima_de) and not d.tem_nota_fiscal:
            motivos.append(
                "RN-004: nota fiscal obrigatoria para despesas com valor em BRL "
                f"estritamente maior que R$ {politica.nf_obrigatoria_acima_de}."
            )
            itens.append(
                ItemResultado(
                    id=d.id,
                    status="nao_reembolsavel",
                    valor_informado=d.valor,
                    valor_reembolsavel=Decimal("0"),
                    motivos=motivos,
                    moeda=d.moeda,
                    valor_em_brl=valor_brl,
                )
            )
            continue

        chave_dia = (d.data, cat_norm)
        usado = uso_diario[chave_dia]
        restante = money(limite - usado) if limite is not None else valor_brl

        if restante <= Decimal("0"):
            valor_reembolsavel = Decimal("0")
            motivos.append(
                f"RN-001: limite diario de R$ {limite} para {cat_norm} "
                f"em {d.data} ja foi atingido."
            )
        else:
            valor_reembolsavel = min(valor_brl, restante)
            uso_diario[chave_dia] = money(usado + valor_reembolsavel)
            if valor_reembolsavel < valor_brl:
                motivos.append(
                    f"RN-003: reembolso parcial — excedente de R$ "
                    f"{money(valor_brl - valor_reembolsavel)} acima do limite "
                    f"diario de R$ {limite} para {cat_norm}."
                )
            else:
                motivos.append("RN-001: valor dentro do limite diario da categoria.")

        if em_viagem and limite is not None:
            motivos.append(
                f"RN-005: limites ampliados em "
                f"{politica.acrescimo_em_viagem_percentual}% por colaborador em viagem."
            )

        status = classificar_status(valor_brl, valor_reembolsavel)
        itens.append(
            ItemResultado(
                id=d.id,
                status=status,
                valor_informado=d.valor,
                valor_reembolsavel=valor_reembolsavel,
                motivos=motivos,
                moeda=d.moeda,
                valor_em_brl=valor_brl,
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
        politica_versao=politica_versao,
    )
