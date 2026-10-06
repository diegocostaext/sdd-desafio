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

## Pendentes (Dia 2)

- [ ] **T-013** — Absorver mudança do envelope lacrado
  - **Atende:** (a definir após anúncio)
  - **Aceite:** spec atualizada + testes verdes
