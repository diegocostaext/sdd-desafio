# Relatório — Desafio SDD

**Aluno:** (preencher) · **Repositório:** (link do fork) · **Data:** 2026-09-29

---

## Delegação

| Atividade | Quem | Por quê |
|---|---|---|
| Identificar ambiguidades | Humano + agente | Agente listou candidatos; humano valida decisões na spec |
| Decidir ambiguidades | Humano | Responsabilidade de negócio do desafio |
| Escrever spec/plan/tasks | Agente (rascunho) | Velocidade; revisão humana recomendada |
| Implementar motor e testes | Agente | Execução mecânica após spec fechada |
| Absorver envelope | Pendente Dia 2 | — |

**Onde deleguei e me arrependi:** (preencher após revisão do diff)

**Onde não deleguei e deveria ter delegado:** (preencher)

**Subagentes / MCP:** Cursor Agent para implementação em lote; `/export` adicional recomendado para sessões reais.

---

## Descrição

**Requisito ambíguo:** nota fiscal “acima de R$ 100”.

**Versão 1 (rascunho inicial):**
> Nota fiscal obrigatória para valores ≥ R$ 100.

**Versão final (spec RN-004 / AMB-003):**
> NF obrigatória apenas se `valor > 100,00`; R$ 100,00 exatos dispensam NF.

**Evolução:** Casos d-003 e d-004 no JSON de exemplo forçam fronteira exclusiva; inclusivo zeraria transporte de R$ 100 sem NF.

---

## Discernimento

**Caso concreto (preencher com sessão exportada real):**

- **Proposta do agente:** (ex.: usar float para dinheiro)
- **Por que estava errado:** diverge de RN-011 e reproduz erro de arredondamento
- **Como detectei:** revisão do plan.md / teste d-011
- **O que fiz:** manter `Decimal` — ver `src/reembolso/models.py`
- **Evidência:** `docs/sessions/01-implementacao-inicial.md`

> **Importante:** substituir este bloco por um erro real observado na sua sessão com Claude Code; sem caso verificável a seção vale zero na rubrica.

---

## Diligência

- Testes: `PYTHONPATH=src python -m pytest tests/ -v`
- CLI: processar `exemplos/despesas-exemplo.json` e conferir `total_reembolsavel` = 585,43
- Diff revisado: `src/reembolso/engine.py` vs ordem de regras seção 8 da spec

**Aceito sem verificar:** (preencher honestamente)

---

## Envelope (Dia 2)

**Status:** pendente até receber mudança às 10h.

**Plano:** atualizar `spec.md` → `DECISIONS.md` (D-002) → `tasks.md` (T-013) → código → testes.

**Arquivos tocados / tempo:** (preencher após envelope)

**Spec que facilitaria:** limites centralizados em `policy.py`; RN numeradas nos testes.

---

## Referências

- Spec: `specs/001-motor-reembolso/spec.md`
- Testes: `tests/test_engine.py`
- Sessão: `docs/sessions/01-implementacao-inicial.md`
