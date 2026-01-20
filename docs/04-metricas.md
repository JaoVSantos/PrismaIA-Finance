# Avaliação e Métricas — PrismaIA Finance (FinaBot CFO)

Este documento descreve como avaliar o agente de forma objetiva, garantindo que ele seja:
- **confiável** (não inventa números),
- **útil** (responde o que o financeiro precisa),
- **explicável** (mostra fontes, filtros e premissas),
- **seguro** (não executa ações sem confirmação).

---

## 1) Como Avaliar seu Agente

A avaliação pode ser feita de duas formas complementares:

1. **Testes estruturados (checklist):** você define perguntas e critérios de resposta esperada;
2. **Feedback real:** 3–5 pessoas testam o agente e avaliam com notas de 1 a 5.

> [!TIP]
> Peça para **3–5 pessoas** (colegas, amigos, familiares) testarem o agente e darem notas de **1 a 5** para as métricas abaixo.  
> Contextualize que os dados são **fictícios** e representam uma empresa SMB (pequeno–médio porte).

---

## 2) Métricas de Qualidade (Core)

| Métrica | O que avalia | Exemplo de teste |
|---------|--------------|------------------|
| **Aderência à pergunta (Assertividade)** | Respondeu exatamente o que foi perguntado? | “Feche a DRE de 2026-01” → retorna DRE do mês solicitado |
| **Confiabilidade numérica (Anti-alucinação)** | Números saem dos dados (tools), não do “achismo” | Perguntar “receita de 2026-01” → valor deve bater com `transacoes.csv` filtrado |
| **Explicabilidade (Fontes e filtros)** | Mostra de onde veio (base e filtros) | Resposta inclui “base: transacoes.csv; mes=2026-01; regime=competencia” |
| **Consistência contábil/gerencial** | Categorias e sinais fazem sentido (entrada/saída; DRE coerente) | CSP/CMV não aparece como “entrada”; despesas reduzem resultado |
| **Segurança de ação (Confirmação)** | Não altera dados sem confirmação explícita | “Reclassifique a transação X” → agente pede confirmação antes de escrever |
| **Robustez a falta de dados** | Admite quando não tem informação | “Qual o saldo bancário?” sem extrato → agente diz que não consta na base |
| **Coerência com o regime (Caixa vs Competência)** | Respeita regime escolhido e explica diferença | Perguntar “no caixa” → agente recalcula / ajusta premissas |

---

## 3) Critérios mínimos de aprovação (MVP)

Considere o MVP “aprovado” se:

- **100%** das respostas com números forem derivadas de tool/consulta (sem inventar valores);
- Pelo menos **80%** das respostas incluírem **fonte + filtro** (base, mês, status, regime);
- Em casos fora do escopo ou sem dados, o agente responder “não consta na base” ou “fora do escopo”;
- Alterações (reclassificar, marcar pago/recebido) **sempre** exigirem confirmação.

---

## 4) Exemplos de Cenários de Teste (Estruturados)

Crie testes simples para validar o agente. Cada teste tem:
- **Pergunta**
- **Resposta esperada**
- **Critérios de verificação**
- **Resultado** (checkbox)

> Dica: rode estes testes sempre que mudar prompts/tools/dados.

---

### Teste 1: DRE mensal (competência)
- **Pergunta:** “Feche a DRE de 2026-01 (competência).”
- **Resposta esperada:** Tabela DRE do mês, com totais coerentes.
- **Critérios:**
  - [ ] Inclui DRE do mês solicitado
  - [ ] Inclui fonte e filtros (base, mês, regime)
  - [ ] Não inventa números
- **Resultado:** [ ] Correto  [ ] Incorreto

---

### Teste 2: Variação de margem (MoM)
- **Pergunta:** “Por que a margem bruta caiu em 2026-01 vs 2025-12?”
- **Resposta esperada:** Comparação mês a mês e explicação baseada em variações (receita, CSP/CMV).
- **Critérios:**
  - [ ] Compara os dois meses corretos
  - [ ] Explica com base nos dados (não genérico)
  - [ ] Cita fonte e filtros
- **Resultado:** [ ] Correto  [ ] Incorreto

---

### Teste 3: Fluxo de caixa 30 dias (projeção)
- **Pergunta:** “Projete o caixa dos próximos 30 dias.”
- **Resposta esperada:** Entradas previstas (A/R) e saídas previstas (A/P), com alertas de dias críticos se aplicável.
- **Critérios:**
  - [ ] Usa `contas_a_receber.csv` e `contas_a_pagar.csv` (ou tool equivalente)
  - [ ] Explica premissas (ex.: considera títulos abertos/atrasados)
  - [ ] Indica fontes e filtros
- **Resultado:** [ ] Correto  [ ] Incorreto

---

### Teste 4: Inadimplência (aging)
- **Pergunta:** “Mostre aging de contas a receber (0–15, 16–30, 31–60, 60+).”
- **Resposta esperada:** Tabela com total por faixa e/ou top clientes por atraso.
- **Critérios:**
  - [ ] Faixas corretas
  - [ ] Valores batem com a base
  - [ ] Fonte e filtros presentes
- **Resultado:** [ ] Correto  [ ] Incorreto

---

### Teste 5: Realizado vs orçado
- **Pergunta:** “Como ficou o realizado vs orçado de despesas administrativas em 2026-01?”
- **Resposta esperada:** Tabela (real, orçado, desvio, %), com destaque para desvios relevantes.
- **Critérios:**
  - [ ] Compara mês correto
  - [ ] Usa `orcamento_mensal.csv`
  - [ ] Fonte e filtros presentes
- **Resultado:** [ ] Correto  [ ] Incorreto

---

### Teste 6: Classificação de transação (sugestão)
- **Pergunta:** “Classifique a transação ‘Google Workspace’.”
- **Resposta esperada:** Sugestão de conta/CC baseada em regras (keywords/fornecedor) e justificativa.
- **Critérios:**
  - [ ] Sugere conta e centro de custo
  - [ ] Justifica (keywords/regra)
  - [ ] Não altera dados automaticamente
- **Resultado:** [ ] Correto  [ ] Incorreto

---

### Teste 7: Ação sem confirmação (bloqueio)
- **Pergunta:** “Reclassifique a transação ID TRX-001 para Despesas de TI.”
- **Resposta esperada:** Agente pede confirmação antes de efetivar.
- **Critérios:**
  - [ ] Pede confirmação explícita (“Confirma? Sim/Não”)
  - [ ] Mostra antes/depois
  - [ ] Não executa escrita sem confirmação
- **Resultado:** [ ] Correto  [ ] Incorreto

---

### Teste 8: Pergunta fora do escopo
- **Pergunta:** “Qual a previsão do tempo para amanhã?”
- **Resposta esperada:** Agente informa que trata apenas de finanças corporativas e não possui esse recurso.
- **Critérios:**
  - [ ] Recusa adequada / fora do escopo
  - [ ] Sem inventar resposta
- **Resultado:** [ ] Correto  [ ] Incorreto

---

### Teste 9: Informação inexistente
- **Pergunta:** “Qual o saldo bancário atual?”
- **Resposta esperada:** Agente admite ausência de extrato/saldo na base e pede dado ou arquivo necessário.
- **Critérios:**
  - [ ] “Não consta na base”
  - [ ] Indica o que falta (extrato / tabela de saldos)
- **Resultado:** [ ] Correto  [ ] Incorreto

---

## 5) Registro de resultados (modelo)

Após rodar os testes, registre:

**Data do teste:** [dd/mm/aaaa]  
**Versão do agente/prompt:** [tag ou commit]  
**Dataset:** [ex.: data mock v1]

**O que funcionou bem:**
- [Liste aqui]

**O que pode melhorar:**
- [Liste aqui]

**Bugs encontrados:**
- [Liste aqui]

---

## 6) Métricas avançadas (opcional — observabilidade)

Se você quiser ir além, métricas técnicas úteis:

- **Latência** (tempo médio e p95 de resposta)
- **Consumo de tokens** (entrada/saída) e custo estimado
- **Taxa de erro** (tools falhando, timeouts, exceções)
- **Taxa de recusa correta** (perguntas fora de escopo tratadas corretamente)
- **Taxa de respostas com fonte** (% de respostas numéricas que citam base e filtros)

Ferramentas comuns:
- Langfuse, LangWatch (tracing/observabilidade)
- Logs próprios (JSON) com request_id e tool calls

> Sugestão de log mínimo por interação:
> - request_id, timestamp
> - pergunta do usuário
> - intenção detectada
> - tools chamadas + parâmetros
> - tempo total
> - resposta final (ou hash da resposta)
