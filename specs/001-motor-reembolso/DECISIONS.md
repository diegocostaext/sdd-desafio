# Log de Decisões e Mudanças de Spec

Ordem cronológica inversa.

---

## D-002 — Política v4 (envelope Dia 2) · 2026-10-06

**Gatilho:** Comunicado RH v4 — https://gist.github.com/Sassine/c9c7d72a4aae51306752c4f9f87a32dc

**O que mudou na spec:** Versão 2.0. RN-013 (câmbio), RN-014 (limites por CC). Entrada ganha
`moeda`. Política e câmbio externos. AMB-011 (PTAX em fim de semana), AMB-012 (padrão vs tabela
parcial). Fora de escopo: fila manual > R$ 500 (item C opcional).

**Por quê:** Auditoria exige limites por centro de custo e despesas internacionais; motor não
pode embutir limites no código.

**O que isso invalidou:** `policy.py` com constantes fixas; NF/limites sobre valor bruto sem
conversão; `centro_custo` apenas informativo.

**Tasks afetadas:** T-013 (spec), T-014 (plan/tasks), T-015 (politica_config), T-016 (cambio),
T-017 (engine/CLI), T-018 (testes envelope).

**Custo:** ~8 arquivos de código + 4 JSON em `exemplos/envelope/` + spec/docs.

---

## D-001 — Spec inicial v1.0 · 2026-09-29

**Gatilho:** Início do desafio; política RH ambígua cruzada com `exemplos/despesas-exemplo.json`.

**O que mudou na spec:** Criação da versão 1.0 com RN-001..RN-012 e AMB-001..AMB-010.

**Por quê:** Estabelecer fonte da verdade testável antes da implementação (SDD).

**Tasks afetadas:** T-001 a T-012 criadas.

**Custo:** Documentação + implementação inicial (~1 sessão).
