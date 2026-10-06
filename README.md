# Motor de Cálculo de Reembolso (Desafio SDD)

CLI que processa despesas corporativas conforme a política v3 documentada em
`specs/001-motor-reembolso/spec.md`.

## Pré-requisitos

- Python 3.10 ou superior
- `pytest` (opcional, para testes): `pip install pytest`

## Como rodar

Na raiz do repositório:

```bash
export PYTHONPATH=src
# Política v3-compat (sem arquivos externos):
python -m reembolso calcular --input exemplos/despesas-exemplo.json --output resultado.json

# Política v4 (envelope Dia 2):
python -m reembolso calcular \
  --input exemplos/envelope/despesas-envelope.json \
  --output resultado-envelope.json \
  --politica exemplos/envelope/politica-v4.json \
  --cambio exemplos/envelope/cambio.json
```

PowerShell:

```powershell
$env:PYTHONPATH = "src"
python -m reembolso calcular --input exemplos/despesas-exemplo.json --output resultado.json
```

O arquivo `resultado.json` conterá totais e a avaliação item a item (`status`, `valor_reembolsavel`, `motivos`).

## Como testar

```bash
export PYTHONPATH=src
python -m pytest tests/ -v
```

## Estrutura

| Caminho | Conteúdo |
|---------|----------|
| `specs/001-motor-reembolso/` | Spec, plano, tasks, decisões |
| `src/reembolso/` | Motor e CLI |
| `tests/` | Testes por requisito (RN/AMB) |
| `docs/RELATORIO.md` | Relatório do desafio |
| `docs/sessions/` | Exports de sessões com o agente |
| `exemplos/envelope/` | Política v4, câmbio e JSONs do envelope |

## Documentação do desafio

Enunciado original: `DESAFIO.md` · Rubrica: `RUBRICA.md` · FAQ: `FAQ.md`
