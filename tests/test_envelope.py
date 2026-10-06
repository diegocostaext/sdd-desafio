"""Testes da mudança de requisito — envelope Dia 2 (política v4)."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

from reembolso.cambio import TabelaCambio
from reembolso.engine import calcular
from reembolso.models import money
from reembolso.politica_config import PoliticaConfig

ROOT = Path(__file__).resolve().parents[1]
ENV = ROOT / "exemplos" / "envelope"


def _v4():
    politica = PoliticaConfig.from_dict(
        json.loads((ENV / "politica-v4.json").read_text(encoding="utf-8"))
    )
    cambio = TabelaCambio.from_dict(
        json.loads((ENV / "cambio.json").read_text(encoding="utf-8"))
    )
    return politica, cambio


def _item(resultado, despesa_id: str):
    for it in resultado.itens:
        if it.id == despesa_id:
            return it
    raise KeyError(despesa_id)


def test_envelope_comercial_total():
    payload = json.loads((ENV / "despesas-envelope.json").read_text(encoding="utf-8"))
    politica, cambio = _v4()
    r = calcular(payload, politica=politica, cambio=cambio, politica_versao="v4")
    assert _item(r, "e-001").valor_reembolsavel == Decimal("300.00")
    assert _item(r, "e-005").valor_reembolsavel == Decimal("0")
    assert _item(r, "e-006").valor_reembolsavel == Decimal("0")
    assert _item(r, "e-007").valor_reembolsavel == Decimal("400.00")
    assert r.total_reembolsavel == money("1143.26")


def test_envelope_cc_desconhecido_usa_padrao():
    payload = json.loads(
        (ENV / "despesas-envelope-cc-desconhecido.json").read_text(encoding="utf-8")
    )
    politica, cambio = _v4()
    r = calcular(payload, politica=politica, cambio=cambio, politica_versao="v4")
    assert _item(r, "f-003").valor_reembolsavel == Decimal("0")
    assert r.total_reembolsavel == money("373.76")


def test_eng_plataforma_hospedagem_bloqueada_v4():
    payload = json.loads((ROOT / "exemplos" / "despesas-exemplo.json").read_text())
    politica, cambio = _v4()
    r = calcular(payload, politica=politica, cambio=cambio, politica_versao="v4")
    assert _item(r, "d-010").valor_reembolsavel == Decimal("0")
