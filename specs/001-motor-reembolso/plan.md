# Plano Técnico — Motor de Cálculo de Reembolso

**Versão:** 2.0 · **Baseado na spec:** 2.0

---

## 1. Stack

| Escolha | O quê | Por quê | Descartado |
|---|---|---|---|
| Linguagem | Python 3.10+ | CLI rápida, Decimal nativo, pytest comum no desafio | Node (menos familiar para aritmética decimal) |
| Testes | pytest | Nomes descritivos, execução simples | unittest (mais verboso) |
| Parsing | `json` stdlib | Entrada já é JSON; sem validação schema externa | pydantic (dependência extra) |
| Aritmética monetária | `decimal.Decimal` + quantize 0.01 HALF_UP | Evita erro de ponto flutuante | float |

## 2. Arquitetura

```
JSON entrada → __main__.py (CLI) → engine.calcular() → ResultadoCalculo.to_dict() → JSON saída
                      ↓
                 models.Despea / ItemResultado
                      ↓
                 policy.py (constantes de limite)
```

**Fronteiras:** `engine.py` concentra regras RN (testável sem I/O). CLI só lê/escreve arquivos.
`policy.py` espelha números da política para facilitar mudança futura (envelope).

## 3. Modelo de dados

- **Despesa:** dataclass imutável a partir do dict de entrada; `valor` já quantizado.
- **ItemResultado:** id, status, valores, lista `motivos`.
- **ResultadoCalculo:** metadados + lista de itens + totais.

Estado mutável interno durante cálculo: mapa `(data, categoria) → reembolso acumulado no dia`.

## 4. Como a política é representada

- **v3-compat:** `PoliticaConfig.v3_compat()` embutido (sem `--politica`).
- **v4:** JSON externo `politica-v4.json` → `PoliticaConfig.from_dict`.
- **Câmbio:** `cambio.json` → `TabelaCambio`; omitido quando só BRL.

Limites **não** ficam mais hardcoded em produção v4.

## 5. Decisões técnicas

### DT-001 — Pacote em `src/reembolso`

**Contexto:** Entrega pede pasta `src/`.  
**Decisão:** Módulo `reembolso` importável com `PYTHONPATH=src`.  
**Alternativa descartada:** script único `main.py` (difícil testar regras isoladas).  
**Consequência:** Comando documentado com `PYTHONPATH=src`.

### DT-002 — Ordenação estável antes do loop

**Contexto:** Duplicata e limite diário dependem de ordem.  
**Decisão:** Sort por `(data, id)` conforme RN-012.  
**Alternativa descartada:** ordem do array original (não determinística entre ambientes).

### DT-003 — Motivos com prefixo RN-xxx

**Contexto:** Rastreabilidade spec → código → saída.  
**Decisão:** Strings em português referenciando IDs da spec.  
**Consequência:** Correção manual pode cruzar saída com spec.

## 6. Estratégia de testes

- **Nível:** unitário sobre `calcular()`; um teste de integração com `despesas-exemplo.json`.
- **Cada RN:** funções `test_rn*` ou cenários dedicados em `tests/test_engine.py`.
- **Borda seção 7 da spec:** arquivo exemplo valida totais e ids críticos (d-007, d-013, d-014).
- **Nomenclatura:** `test_rn004_limite_diario_agregado_alimentacao`, etc.

## 7. Riscos

| Risco | Probabilidade | Mitigação |
|---|---|---|
| Envelope altera limites | Alta (Dia 2) | Constantes centralizadas + DECISIONS |
| Interpretação de estorno | Média | Teste RN-010 + doc AMB-008 |
| Shell sem PYTHONPATH | Média | README explícito |
