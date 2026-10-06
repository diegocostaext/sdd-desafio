# Spec — Motor de Cálculo de Reembolso

**Versão:** 1.0 · **Status:** aprovada para implementação · **Última alteração:** 2026-09-29

> Este arquivo descreve o QUÊ e o PORQUÊ. Não cita linguagem, biblioteca ou estrutura de pastas.

---

## 1. Problema

O financeiro valida manualmente despesas contra a política de reembolso. O processo é lento,
inconsistente e difícil de auditar. É necessário um motor determinístico que, dado um lote de
despesas de um colaborador em um período, calcule quanto é reembolsável e explique cada decisão.

## 2. Objetivo

Para cada despesa informada, o sistema produz valor reembolsável, status e motivos textuais
alinhados à política v3 (com ambiguidades resolvidas aqui), mais totais do lote.

## 3. Fora de escopo

- Aprovação humana, workflow, pagamento ou integração bancária.
- Cadastro ou edição de despesas; apenas cálculo sobre JSON recebido.
- Inferir viagem por heurística em descrição/fornecedor (sem campo explícito).
- Dividir automaticamente hospedagem multi-noite usando NLP na descrição.
- Conversão de moeda; todos os valores são BRL.
- Tolerância a JSON malformado além de falha explícita na CLI (erro de leitura).

## 4. Entrada e saída

**Entrada:** conforme `exemplos/despesas-exemplo.json`.

| Campo | Tipo | Significado | Obrigatório |
|---|---|---|---|
| `colaborador.id` | string | Identificador do colaborador | sim |
| `colaborador.nome` | string | Nome (informativo) | sim |
| `colaborador.centro_custo` | string | Centro de custo (informativo) | sim |
| `periodo.competencia` | string `YYYY-MM` | Competência contábil | sim |
| `periodo.inicio` | string `YYYY-MM-DD` | Primeiro dia elegível | sim |
| `periodo.fim` | string `YYYY-MM-DD` | Último dia elegível | sim |
| `despesas[]` | array | Lançamentos | sim |
| `despesas[].id` | string | Identificador único do lançamento | sim |
| `despesas[].data` | string `YYYY-MM-DD` | Data do gasto | sim |
| `despesas[].categoria` | string | Tipo de despesa | sim |
| `despesas[].descricao` | string | Descrição livre | sim |
| `despesas[].fornecedor` | string | Fornecedor | sim |
| `despesas[].valor` | number | Valor em BRL (pode ser negativo) | sim |
| `despesas[].tem_nota_fiscal` | boolean | Indica presença de NF | sim |
| `em_viagem` | boolean | Colaborador em viagem no período | não (default: `false`) |

**Saída:**

| Campo | Tipo | Significado |
|---|---|---|
| `colaborador.id` | string | Eco do colaborador |
| `periodo.competencia` | string | Eco da competência |
| `total_solicitado` | number | Soma dos `valor` **positivos** do lote |
| `total_reembolsavel` | number | Soma dos `valor_reembolsavel` (mínimo 0) |
| `itens[]` | array | Um elemento por despesa de entrada (mesma ordem de processamento) |
| `itens[].id` | string | Id da despesa |
| `itens[].status` | enum | `reembolsado_integral`, `reembolsado_parcial`, `nao_reembolsavel` |
| `itens[].valor_informado` | number | Valor original |
| `itens[].valor_reembolsavel` | number | Valor aprovado (pode ser negativo em estorno) |
| `itens[].motivos` | string[] | Justificativas referenciando RN-xxx |

**Exemplo reduzido:** duas alimentações no mesmo dia (R$ 72,50 e R$ 38,00) → primeiro item
parcial R$ 60,00; segundo R$ 0,00 por limite diário esgotado.

## 5. Regras de negócio

### RN-001 — Limites diários por categoria

**Regra:** Alimentação: R$ 60/dia; transporte urbano: R$ 80/dia; hospedagem: R$ 250/dia.
O limite aplica-se ao **total reembolsável** da categoria na **data** (`despesas[].data`),
somando todos os lançamentos elegíveis daquele dia.

**Origem:** política itens 1–3  
**Aceite:** No dia 2026-07-03, alimentação R$ 72,50 + R$ 38,00 → reembolsável R$ 60,00 + R$ 0,00.

### RN-002 — Unidade de hospedagem

**Regra:** Cada **lançamento** de hospedagem em uma data consome até R$ 250 da cota daquele dia.
Não se fraciona valor em múltiplas diárias inferidas da descrição.

**Origem:** política item 3  
**Aceite:** Lançamento único R$ 480,00 em 2026-07-14 → reembolsável R$ 250,00.

### RN-003 — Reembolso parcial acima do limite

**Regra:** Quando o valor elegível excede a cota restante do dia/categoria, reembolsa-se apenas
a cota restante; o excedente não é pago (não recusa-se o item inteiro por excesso isolado).

**Origem:** política item 4  
**Aceite:** Alimentação R$ 61,00 com cota cheia disponível → R$ 60,00 parcial.

### RN-004 — Nota fiscal acima de R$ 100

**Regra:** NF é obrigatória quando `valor` é **estritamente maior** que R$ 100,00.
Valor igual a R$ 100,00 não exige NF. Sem NF quando exigida → reembolso zero.

**Origem:** política item 5  
**Aceite:** Transporte R$ 100,00 sem NF → elegível; R$ 100,01 sem NF → R$ 0,00.

### RN-005 — Viagem amplia limites

**Regra:** Se `em_viagem` for `true`, limites diários (RN-001) multiplicam por 1,5 (50% a mais).

**Origem:** política item 6  
**Aceite:** `em_viagem: true`, alimentação R$ 85,00 em um dia → reembolsável R$ 85,00 (limite 90).

### RN-006 — Competência

**Regra:** Despesa com `data` fora do intervalo `[periodo.inicio, periodo.fim]` (inclusivo)
não é reembolsável.

**Origem:** política item 7  
**Aceite:** Data 2026-04-15 com período julho → R$ 0,00.

### RN-007 — Duplicatas

**Regra:** Duplicata = mesma combinação de `data`, categoria normalizada, `fornecedor`, `valor`
e `descricao`. Mantém-se a **primeira** ocorrência na ordem de processamento; demais → R$ 0,00.

**Origem:** política item 8  
**Aceite:** Dois lançamentos idênticos exceto `id` → segundo recusado.

### RN-008 — Categorias não cobertas

**Regra:** Categorias fora de `{alimentacao, transporte_urbano, hospedagem}` → reembolso zero.

**Origem:** política item 9  
**Aceite:** `coworking` → R$ 0,00.

### RN-009 — Normalização de categoria

**Regra:** Categoria comparada em minúsculas, sem espaços nas pontas; hífen vira underscore.

**Origem:** dados de exemplo (`ALIMENTACAO`)  
**Aceite:** `ALIMENTACAO` tratada como alimentação.

### RN-010 — Estornos (valor negativo)

**Regra:** Valor negativo reduz o reembolso já acumulado na mesma categoria/data, até zerar
o saldo daquele dia; não gera reembolso negativo além do estorno do item.

**Origem:** exemplo d-009  
**Aceite:** Estorno -R$ 45 após R$ 50 no mesmo dia/categoria → saldo líquido R$ 5 no dia.

### RN-011 — Arredondamento monetário

**Regra:** Valores reembolsáveis arredondados para 2 casas decimais (meio centavo para cima).

**Origem:** exemplo d-011 (33,333)  
**Aceite:** R$ 33,333 elegível → R$ 33,33 reembolsável.

### RN-012 — Ordem de processamento

**Regra:** Despesas ordenadas por `(data crescente, id crescente)` antes de aplicar regras.

**Origem:** necessidade de duplicata e limite diário determinísticos  
**Aceite:** Duplicatas: menor `id` prevalece.

## 6. Ambiguidades identificadas e decisões

### AMB-001 — “R$ 60 por dia” é por despesa ou por dia?

**Texto original:** "Alimentação tem limite de R$ 60 por dia."  
**O que não está claro:** Limite por lançamento ou agregado diário.  
**Decisão:** Agregado por `(data, categoria)`.  
**Justificativa:** Evita burlar limite com vários lançamentos pequenos no mesmo dia.  
**Regra afetada:** RN-001

### AMB-002 — Reembolso parcial

**Texto original:** "Despesas acima do limite são reembolsadas parcialmente."  
**O que não está claro:** Pagar até o limite ou recusar item inteiro.  
**Decisão:** Pagar até a cota restante (RN-003).  
**Justificativa:** Literalidade de “parcialmente” e melhor experiência do colaborador.  
**Regra afetada:** RN-003

### AMB-003 — Fronteira de R$ 100 e NF

**Texto original:** "Nota fiscal é obrigatória acima de R$ 100."  
**O que não está claro:** Inclusivo ou exclusivo.  
**Decisão:** Obrigatória apenas se `valor > 100,00`.  
**Justificativa:** “Acima de” interpretado como estritamente maior.  
**Regra afetada:** RN-004

### AMB-004 — “Em viagem” sem campo na entrada

**Texto original:** "Colaborador em viagem tem limites ampliados em 50%."  
**O que não está claro:** Como detectar viagem.  
**Decisão:** Campo opcional `em_viagem` no JSON raiz; default `false`.  
**Justificativa:** Política exige dado que a entrada não traz; extensão mínima explícita.  
**Regra afetada:** RN-005

### AMB-005 — Duplicatas

**Texto original:** "Duplicatas devem ser tratadas."  
**O que não está claro:** Ignorar, somar uma vez, recusar todas.  
**Decisão:** Ignorar ocorrências subsequentes (mesma chave de negócio).  
**Justificativa:** Evita pagamento em dobro mantendo rastreio do lançamento duplicado.  
**Regra afetada:** RN-007

### AMB-006 — Competência vs data do lançamento

**Texto original:** "Despesas devem ser lançadas dentro do período de competência."  
**O que não está claro:** Usar `competencia` string ou intervalo `inicio`/`fim`.  
**Decisão:** Validar `despesas[].data` contra `inicio` e `fim`.  
**Justificativa:** Intervalo é verificável e independente de parsing de mês.  
**Regra afetada:** RN-006

### AMB-007 — Hospedagem “2 diárias” em um lançamento

**Texto original:** "Hospedagem tem limite de R$ 250 por diária."  
**O que não está claro:** Uma diária ou várias no mesmo registro.  
**Decisão:** Um lançamento = uma aplicação do limite diário na data do registro (RN-002).  
**Justificativa:** Entrada não informa quantidade de noites de forma estruturada.  
**Regra afetada:** RN-002

### AMB-008 — Valores negativos (estorno)

**Texto original:** (silêncio)  
**O que não está claro:** Estorno reduz total, zera ou gera crédito global.  
**Decisão:** Reduz saldo reembolsado da categoria no dia (RN-010).  
**Justificativa:** Estorno típico de cancelamento ligado ao mesmo contexto de gasto.  
**Regra afetada:** RN-010

### AMB-009 — Categoria fora da lista / caixa alta

**Texto original:** "Categorias fora da política não são reembolsáveis."  
**O que não está claro:** Variações de escrita.  
**Decisão:** Normalização RN-009; demais categorias → zero.  
**Justificativa:** Dados reais chegam inconsistentes (`ALIMENTACAO`).  
**Regra afetada:** RN-008, RN-009

### AMB-010 — Fim de semana e plantão

**Texto original:** (silêncio)  
**O que não está claro:** Regra especial para sábado/domingo.  
**Decisão:** Mesmas regras qualquer dia da semana.  
**Justificativa:** Política não distingue; almoço de sábado segue limite de alimentação.  
**Regra afetada:** RN-001

## 7. Casos de borda

| Caso | Entrada | Comportamento esperado | Regra |
|---|---|---|---|
| Dois almoços no mesmo dia | d-001, d-002 | R$ 60 + R$ 0 | RN-001 |
| NF na fronteira | d-003, d-004 | R$ 80 parcial; R$ 0 | RN-004 |
| Coworking | d-005 | R$ 0 | RN-008 |
| Duplicata | d-006, d-007 | 54,90 + 0 | RN-007 |
| Fora do período | d-008 | R$ 0 | RN-006 |
| Estorno sem saldo | d-009 isolado | R$ 0 no estorno | RN-010 |
| Hotel valor alto | d-010 | R$ 250 parcial | RN-002, RN-003 |
| Centavos | d-011 | R$ 33,33 | RN-011 |
| Sábado | d-012 | Normal | AMB-010 |
| Hospedagem sem NF >100 | d-013 | R$ 0 | RN-004 |
| Categoria maiúscula | d-014 | R$ 60 parcial | RN-009 |

## 8. Ordem de aplicação das regras

Por despesa, após ordenação global:

1. Competência (RN-006)  
2. Duplicata (RN-007)  
3. Categoria elegível (RN-008/RN-009)  
4. Estorno se `valor < 0` (RN-010) — encerra item  
5. Nota fiscal (RN-004) — se falhar, zero  
6. Limite diário com viagem (RN-001, RN-005, RN-003)  
7. Arredondamento na escrita (RN-011)

## 9. Critérios de aceite

- [ ] CLI `calcular --input --output` produz JSON conforme seção 4.
- [ ] `exemplos/despesas-exemplo.json` → `total_reembolsavel` = R$ 585,43.
- [ ] Cada RN-001..RN-012 possui teste automatizado nomeado ou comentado.
- [ ] Cada item recusado ou parcial traz ao menos um motivo citando RN.

## 10. O que fica em aberto

- **Envelope Dia 2:** aguardando mudança oficial; registrar em `DECISIONS.md` quando publicada.
- **Viagem:** sem `em_viagem`, colaborador assume limites normais (pode divergir de viagem real não informada).
