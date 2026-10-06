# Tasks — Motor de Cálculo de Reembolso

**Formato do commit:** `feat(T-00N): ...` · `test(T-00N): ...`

---

## Fase 1 — Fundação

- [x] **T-001** — Esqueleto do pacote, modelos e constantes de política
  - **Atende:** RN-011 (money)
  - **Aceite:** Import de `reembolso.models` e `reembolso.policy` sem erro
  - **Commit:** (implementação inicial)

- [x] **T-002** — Ordenação e pipeline base de `calcular()`
  - **Atende:** RN-012
  - **Aceite:** `test_rn006_fora_competencia` passa

## Fase 2 — Regras de negócio

- [x] **T-003** — Competência e categorias
  - **Atende:** RN-006, RN-008, RN-009
  - **Aceite:** `test_rn006_*`, `test_rn008_*`, `test_amb009_*`

- [x] **T-004** — Nota fiscal e fronteira R$ 100
  - **Atende:** RN-004, AMB-003
  - **Aceite:** `test_rn004_*`

- [x] **T-005** — Limite diário agregado e parcial
  - **Atende:** RN-001, RN-003, AMB-001, AMB-002
  - **Aceite:** `test_rn001_limite_diario_agregado_alimentacao`

- [x] **T-006** — Duplicatas
  - **Atende:** RN-007, AMB-005
  - **Aceite:** `test_rn007_duplicata`

- [x] **T-007** — Hospedagem por lançamento
  - **Atende:** RN-002, AMB-007
  - **Aceite:** `test_rn002_hospedagem_limite_por_lancamento`

- [x] **T-008** — Estornos
  - **Atende:** RN-010, AMB-008
  - **Aceite:** `test_rn010_estorno_reduz_saldo_dia`

- [x] **T-009** — Viagem (+50%)
  - **Atende:** RN-005, AMB-004
  - **Aceite:** `test_rn005_viagem_amplia_limite`

## Fase 3 — Casos de borda

- [x] **T-010** — Arquivo `despesas-exemplo.json` end-to-end
  - **Atende:** seção 7 da spec, critério 9
  - **Aceite:** `test_arquivo_exemplo_integracao`

## Fase 4 — Saída e CLI

- [x] **T-011** — CLI `calcular --input --output`
  - **Atende:** interface fixa do desafio
  - **Aceite:** comando documentado no README gera `resultado.json`

## Fase 5 — Documentação

- [x] **T-012** — Spec, plan, DECISIONS, CLAUDE, RELATORIO, sessions
  - **Atende:** entrega SDD
  - **Aceite:** arquivos preenchidos em `specs/` e `docs/`

## Fase 5 — Envelope Dia 2 (v4)

- [x] **T-013** — Atualizar spec v2.0 e DECISIONS D-002
  - **Atende:** RN-013, RN-014, AMB-011, AMB-012
  - **Aceite:** `spec.md` e `DECISIONS.md` descrevem v4

- [x] **T-014** — Adicionar fixtures `exemplos/envelope/*.json`
  - **Atende:** dados oficiais do gist
  - **Aceite:** arquivos commitados localmente

- [x] **T-015** — Carregar `politica-v4.json` (`PoliticaConfig`)
  - **Atende:** RN-014
  - **Aceite:** CC desconhecido usa `padrao`; CC-ENG bloqueia hospedagem

- [x] **T-016** — Conversão `cambio.json` (`TabelaCambio`)
  - **Atende:** RN-013, AMB-011
  - **Aceite:** EUR fim de semana usa última PTAX; GBP sem taxa → zero

- [x] **T-017** — CLI `--politica` e `--cambio`; engine v4
  - **Atende:** interface envelope
  - **Aceite:** v3-compat quando flags omitidas

- [x] **T-018** — Testes `tests/test_envelope.py`
  - **Atende:** critérios de aceite v4 da spec
  - **Aceite:** totais 1143,26 e 373,76; testes v3 ainda passam

## Opcional (não implementado)

- [ ] **T-019** — Fila aprovação manual > R$ 500 (item C envelope)
  - **Motivo:** opcional; spec mantida consistente sem este estado
