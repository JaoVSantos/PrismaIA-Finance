# Documentação do Agente — PrismaIA Finance (FinaBot CFO)

## 1. Visão geral

O **PrismaIA Finance (FinaBot CFO)** é um assistente virtual com IA generativa para apoiar o **financeiro de empresas de pequeno e médio porte** nas rotinas de controle, análise e tomada de decisão com base em dados internos (lançamentos, contas a pagar/receber, orçamento).

A proposta é unir:
- **Chat (linguagem natural)** para perguntas e explicações;
- **Ferramentas (tools)** para cálculos e consultas confiáveis;
- **Guardrails de segurança** para evitar alucinação e reduzir risco de uso indevido.

> Princípio central: **números só saem de dados** (CSV/JSON/SQL). O agente não “inventará” valores.

---

## 2. Público-alvo e contexto

### Usuário final
- Analista financeiro
- Assistente financeiro
- Controller (em empresas menores)
- Dono/gestor (com visão gerencial)

### Cenários comuns
- Fechamento mensal (DRE gerencial)
- Fluxo de caixa (realizado e projeção curta)
- Conferência de contas a pagar/receber
- Acompanhamento de inadimplência (aging)
- Comparação realizado vs orçado
- Investigação de variações (margem, despesas, receitas)

---

## 3. Casos de uso (MVP)

### 3.1 DRE gerencial mensal
**Perguntas típicas**
- “Feche a DRE de 2026-01.”
- “Por que a margem caiu vs mês anterior?”
- “Quais despesas cresceram mais?”

**Saída esperada**
- Tabela DRE (Receita, Impostos/Devoluções se existirem, CSP/CMV, Margem, Despesas por natureza, EBITDA, Resultado)
- Comparativo MoM e vs orçamento (se houver)
- Explicação baseada em variações relevantes e dados

---

### 3.2 Fluxo de caixa (curto prazo)
**Perguntas típicas**
- “Qual meu caixa projetado nos próximos 30 dias?”
- “Quais vencimentos críticos existem essa semana?”
- “O caixa fecha negativo em algum dia?”

**Saída esperada**
- Visão de entradas previstas (A/R) e saídas previstas (A/P)
- Projeção diária ou semanal (dependendo da granularidade)
- Alertas de risco (ex.: “dia X fica negativo”)

---

### 3.3 Contas a receber (inadimplência)
**Perguntas típicas**
- “Top 10 clientes inadimplentes e impacto.”
- “Aging por faixa: 0–15, 16–30, 31–60, 60+.”
- “Quais clientes pioraram vs mês anterior?”

**Saída esperada**
- Tabelas (top clientes, total por faixa)
- Recomendações (ex.: priorizar cobrança, renegociação) sem inventar valores

---

### 3.4 Classificação de lançamentos (plano de contas e centro de custo)
**Perguntas típicas**
- “Classifique estes lançamentos sem conta/CC.”
- “Reclassifique a transação ID X para ‘Despesas de TI’.”

**Saída esperada**
- Sugestão de conta/CC com justificativa (palavras-chave, fornecedor, histórico)
- **Mudanças efetivas só com confirmação explícita do usuário** (ver segurança)

---

### 3.5 Realizado vs orçado
**Perguntas típicas**
- “Como está o orçamento de despesas administrativas em 2026-01?”
- “Onde estou estourando o orçamento?”

**Saída esperada**
- Tabela comparativa (realizado, orçado, desvio, %)
- Principais contas com desvio relevante

---

## 4. Requisitos funcionais

### RF-01 — Chat com contexto
O agente deve manter contexto de conversa (mês, regime, filtros) e permitir follow-ups:
- “E agora compara com o mês anterior”
- “Mostre apenas o centro de custo Produção”

### RF-02 — Consultas confiáveis por tools
Sempre que houver cálculo, agregação ou lista baseada em dados, o agente deve chamar ferramentas internas (tools) em vez de “calcular no texto”.

### RF-03 — Explicabilidade
Toda resposta numérica deve indicar:
- quais dados/arquivos/tabelas foram usados
- quais filtros foram aplicados (mês, status, regime)
- quaisquer premissas (ex.: competência = data do lançamento)

### RF-04 — Ações controladas
Reclassificar, marcar como pago/recebido, alterar status:
- só após confirmação do usuário
- com registro de auditoria (timestamp, usuário, antes/depois, justificativa)

---

## 5. Requisitos não funcionais

### RNF-01 — Segurança e anti-alucinação
- Proibido inventar números, datas de pagamento, saldos e totais.
- Se a base não tiver dado, o agente deve dizer claramente: “não consta na base”.

### RNF-02 — Rastreabilidade
Toda operação de escrita (se habilitada) deve gerar log/registro.

### RNF-03 — Reprodutibilidade
Cálculos devem ser determinísticos dado o mesmo dataset e os mesmos filtros.

### RNF-04 — Modularidade
Separar:
- UI (app)
- Orquestração (agente)
- Tools (consultas e cálculos)
- Acesso a dados (CSV/SQL)
- Guardrails (regras)

---

## 6. Arquitetura (MVP)

### 6.1 Visão de alto nível

- **UI**: app em Streamlit (chat + dashboards simples)
- **Orquestrador**: recebe pergunta, resolve intenção, chama tools, monta resposta
- **Tools**: funções para DRE, KPIs, fluxo de caixa, A/R e A/P, busca de transações
- **Dados**: arquivos CSV/JSON (fase 1), evoluindo para SQL (fase 2)
- **RAG (opcional no MVP)**: políticas internas e regras de classificação

### 6.2 Estrutura de pastas recomendada

