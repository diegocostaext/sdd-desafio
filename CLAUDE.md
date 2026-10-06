# CLAUDE.md

## O projeto

Motor de cálculo de reembolso de despesas corporativas. CLI que lê JSON de despesas
e emite JSON com valor reembolsável e justificativa por item.

## Fonte da verdade

- `specs/001-motor-reembolso/spec.md` — **o que** o sistema faz.
- `specs/001-motor-reembolso/plan.md` — **como**.
- `specs/001-motor-reembolso/tasks.md` — **ordem** de implementação.

Quando código e spec discordarem, corrigir a spec primeiro e registrar em `DECISIONS.md`.

**Antes de implementar, leia a task em `tasks.md`.** Se não houver task, avise antes de codar.

## Regras de trabalho

- Regra de negócio vive na spec, não no chat.
- Commit referencia task: `feat(T-003): ...`, docs: `docs(spec): ...`.
- Toda RN da spec tem teste automatizado.

## Stack e comandos

- Linguagem: Python 3.10+
- Rodar CLI: `PYTHONPATH=src python -m reembolso calcular --input <entrada.json> --output <saida.json>`
- Testes: `PYTHONPATH=src python -m pytest tests/ -v`

## Convenções de código

- Pacote em `src/reembolso/`; núcleo de regras em `engine.py`.
- Valores monetários: `Decimal`, arredondamento HALF_UP para 2 casas na saída.
- Ordem de processamento de despesas: `(data asc, id asc)`.

## Fora de escopo

- Interface web, persistência, aprovação humana, pagamento bancário.
- Inferência automática de viagem a partir de descrição ou fornecedor.
