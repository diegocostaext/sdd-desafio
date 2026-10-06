"""Testes alinhados a RN/AMB da spec 001-motor-reembolso."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from reembolso.engine import calcular, exige_nota_fiscal, normalizar_categoria
from reembolso.models import money

ROOT = Path(__file__).resolve().parents[1]
EXEMPLO = ROOT / "exemplos" / "despesas-exemplo.json"


def _payload(**overrides):
    base = {
        "colaborador": {"id": "c-1", "nome": "Teste"},
        "periodo": {
            "competencia": "2026-07",
            "inicio": "2026-07-01",
            "fim": "2026-07-31",
        },
        "despesas": [],
    }
    base.update(overrides)
    return base


def _item(resultado, despesa_id: str):
    for it in resultado.itens:
        if it.id == despesa_id:
            return it
    raise KeyError(despesa_id)


def test_rn004_nf_obrigatoria_apenas_acima_de_100():
    assert exige_nota_fiscal(Decimal("100.00")) is False
    assert exige_nota_fiscal(Decimal("100.01")) is True


def test_amb009_normaliza_categoria():
    assert normalizar_categoria("ALIMENTACAO") == "alimentacao"


def test_rn006_fora_competencia():
    p = _payload(
        despesas=[
            {
                "id": "d-x",
                "data": "2026-04-15",
                "categoria": "alimentacao",
                "descricao": "x",
                "fornecedor": "F",
                "valor": 41.0,
                "tem_nota_fiscal": True,
            }
        ]
    )
    r = calcular(p)
    assert _item(r, "d-x").valor_reembolsavel == Decimal("0")


def test_rn007_duplicata():
    dup = {
        "id": "d-1",
        "data": "2026-07-09",
        "categoria": "alimentacao",
        "descricao": "Almoco",
        "fornecedor": "Bistro Central",
        "valor": 54.90,
        "tem_nota_fiscal": True,
    }
    p = _payload(despesas=[dup, {**dup, "id": "d-2"}])
    r = calcular(p)
    assert _item(r, "d-1").valor_reembolsavel == Decimal("54.90")
    assert _item(r, "d-2").valor_reembolsavel == Decimal("0")


def test_rn001_limite_diario_agregado_alimentacao():
    p = _payload(
        despesas=[
            {
                "id": "d-1",
                "data": "2026-07-03",
                "categoria": "alimentacao",
                "descricao": "a",
                "fornecedor": "R1",
                "valor": 72.50,
                "tem_nota_fiscal": True,
            },
            {
                "id": "d-2",
                "data": "2026-07-03",
                "categoria": "alimentacao",
                "descricao": "b",
                "fornecedor": "R2",
                "valor": 38.00,
                "tem_nota_fiscal": True,
            },
        ]
    )
    r = calcular(p)
    assert _item(r, "d-1").valor_reembolsavel == Decimal("60.00")
    assert _item(r, "d-2").valor_reembolsavel == Decimal("0.00")


def test_rn004_transporte_100_sem_nf():
    p = _payload(
        despesas=[
            {
                "id": "d-3",
                "data": "2026-07-06",
                "categoria": "transporte_urbano",
                "descricao": "t",
                "fornecedor": "Taxi",
                "valor": 100.00,
                "tem_nota_fiscal": False,
            },
            {
                "id": "d-4",
                "data": "2026-07-06",
                "categoria": "transporte_urbano",
                "descricao": "t2",
                "fornecedor": "Taxi",
                "valor": 100.01,
                "tem_nota_fiscal": False,
            },
        ]
    )
    r = calcular(p)
    assert _item(r, "d-3").valor_reembolsavel == Decimal("80.00")
    assert _item(r, "d-4").valor_reembolsavel == Decimal("0.00")


def test_rn008_categoria_nao_elegivel():
    p = _payload(
        despesas=[
            {
                "id": "d-5",
                "data": "2026-07-07",
                "categoria": "coworking",
                "descricao": "x",
                "fornecedor": "Hub",
                "valor": 89.0,
                "tem_nota_fiscal": True,
            }
        ]
    )
    assert _item(calcular(p), "d-5").valor_reembolsavel == Decimal("0")


def test_rn010_estorno_reduz_saldo_dia():
    p = _payload(
        despesas=[
            {
                "id": "d-t1",
                "data": "2026-07-11",
                "categoria": "transporte_urbano",
                "descricao": "corrida",
                "fornecedor": "Taxi",
                "valor": 50.0,
                "tem_nota_fiscal": False,
            },
            {
                "id": "d-t2",
                "data": "2026-07-11",
                "categoria": "transporte_urbano",
                "descricao": "estorno",
                "fornecedor": "Taxi",
                "valor": -45.0,
                "tem_nota_fiscal": False,
            },
        ]
    )
    r = calcular(p)
    assert _item(r, "d-t1").valor_reembolsavel == Decimal("50.00")
    assert _item(r, "d-t2").valor_reembolsavel == Decimal("-45.00")
    assert r.total_reembolsavel == Decimal("5.00")


def test_rn002_hospedagem_limite_por_lancamento():
    p = _payload(
        despesas=[
            {
                "id": "d-10",
                "data": "2026-07-14",
                "categoria": "hospedagem",
                "descricao": "Hotel 2 diarias",
                "fornecedor": "Hotel",
                "valor": 480.0,
                "tem_nota_fiscal": True,
            }
        ]
    )
    assert _item(calcular(p), "d-10").valor_reembolsavel == Decimal("250.00")


def test_rn005_viagem_amplia_limite():
    p = _payload(
        em_viagem=True,
        despesas=[
            {
                "id": "d-v",
                "data": "2026-07-03",
                "categoria": "alimentacao",
                "descricao": "almoco",
                "fornecedor": "R",
                "valor": 85.0,
                "tem_nota_fiscal": True,
            }
        ],
    )
    assert _item(calcular(p), "d-v").valor_reembolsavel == Decimal("85.00")


def test_arquivo_exemplo_integracao():
    payload = json.loads(EXEMPLO.read_text(encoding="utf-8"))
    r = calcular(payload)
    assert len(r.itens) == 14
    assert _item(r, "d-007").valor_reembolsavel == Decimal("0")
    assert _item(r, "d-013").valor_reembolsavel == Decimal("0")
    assert _item(r, "d-014").valor_reembolsavel == Decimal("0")
    assert r.total_reembolsavel == money("585.43")
