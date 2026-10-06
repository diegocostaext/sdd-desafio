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

**Fonte:** https://gist.github.com/Sassine/c9c7d72a4aae51306752c4f9f87a32dc

**Caminho seguido:** spec v2.0 → `DECISIONS.md` D-002 → tasks T-013..T-018 → código → testes.

**Arquivos tocados (implementação v4):** `spec.md`, `DECISIONS.md`, `tasks.md`, `politica_config.py`,
`cambio.py`, `engine.py`, `models.py`, `__main__.py`, `tests/test_envelope.py`, `exemplos/envelope/*`.

**O que a arquitetura absorveu:** política externa e câmbio injetados na CLI; v3-compat sem flags.

**O que resistiu:** categorias parciais por CC (AMB-012) exigiram regra explícita na spec.

**Item C (> R$ 500):** não implementado (opcional no envelope).

**Números de aceite:** envelope comercial → R$ 1143,26; CC desconhecido → R$ 373,76.

---

## Referências

- Spec: `specs/001-motor-reembolso/spec.md`
- Testes: `tests/test_engine.py`
- Sessão: `docs/sessions/01-implementacao-inicial.md`
