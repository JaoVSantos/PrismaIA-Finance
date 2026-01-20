# Base de Conhecimento — PrismaIA Finance (FinaBot CFO)

Esta base de conhecimento reúne os **dados operacionais e gerenciais** necessários para o agente responder com confiabilidade a perguntas sobre **DRE**, **fluxo de caixa**, **contas a pagar/receber**, **inadimplência** e **realizado vs orçado**.

> Princípio do projeto: **números e listas sempre vêm de consultas aos dados** (CSV/JSON/SQL). O agente não inventa valores.

---

## 1) Dados Utilizados

Os dados do MVP ficarão na pasta `data/` e serão consumidos pelo agente via camada de acesso (`src/tools/data_access.py`).

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `transacoes.csv` | CSV | Razão simplificado (entradas/saídas). Base para KPIs, DRE gerencial e análises de variação. |
| `contas_a_pagar.csv` | CSV | Títulos de A/P. Base para alertas de vencimento, projeção de caixa (saídas previstas) e despesas futuras. |
| `contas_a_receber.csv` | CSV | Títulos de A/R. Base para inadimplência, aging e projeção de caixa (entradas previstas). |
| `orcamento_mensal.csv` | CSV | Orçado por mês/conta/centro de custo. Base para “realizado vs orçado” e alertas de estouro. |
| `plano_contas.json` | JSON | Estrutura do plano de contas + centros de custo + regras de classificação (keywords/fornecedores → conta/CC sugeridos). |
| `cadastro.json` | JSON | Metadados da empresa (nome fictício, moeda, timezone, políticas simples como alçada/aprovação). |
| `politicas_classificacao.md` | Markdown | Regras internas de classificação (o que entra em cada conta, exceções e exemplos). Usado para RAG e consistência. |
| `glossario_financeiro.md` | Markdown | Glossário de termos (competência vs caixa, margem, EBITDA etc.). Usado para explicações didáticas. |

> [!TIP]
> **Quer dados mais robustos?** Podemos gerar mais volume de dados mockados (ex.: 12–24 meses, milhares de transações) e também incorporar datasets públicos (Hugging Face/Kaggle), desde que estejam coerentes com o contexto corporativo e não introduzam dados sensíveis.

---

## 2) Adaptações nos Dados

Como este projeto é voltado a **finanças empresariais (SMB)**, os dados mockados serão criados com:

- **Empresa fictícia** (nome, setor e estrutura de centros de custo)
- **Plano de contas padronizado** (Receitas, CSP/CMV, Despesas, Financeiras etc.)
- **Transações com descrições realistas** (fornecedores, meios de pagamento, documentos)
- **Títulos A/P e A/R** coerentes com transações (vencimentos, status, competência)
- **Orçamento mensal** alinhado ao tamanho da operação (para o “real vs orçado” fazer sentido)

> A ideia é que os arquivos se “conversem” entre si (ex.: pagamentos em `transacoes.csv` batem com títulos baixados em `contas_a_pagar.csv`).

---

## 3) Estratégia de Integração

### 3.1 Como os dados são carregados?
No MVP (arquivos locais), a estratégia será:

- Carregar CSV/JSON sob demanda via `src/tools/data_access.py`
- Aplicar filtros (mês, competência, status, centro de custo, conta) na camada de tool
- Retornar dados agregados e/ou tabelas ao orquestrador

**Por que assim?**
- Evita colocar datasets grandes no prompt
- Dá respostas reproduzíveis
- Reduz risco de “alucinação de número” (o agente usa resultado de tool)

> Evolução futura: trocar o backend CSV por SQLite/PostgreSQL mantendo a mesma interface de tools.

### 3.1.1 Como os dados se relacionam (MVP)
- `contas_a_pagar.id_titulo` pode aparecer em `transacoes.documento_ref` quando o título for pago.
- `contas_a_receber.id_titulo` pode aparecer em `transacoes.documento_ref` quando o título for recebido.
- `transacoes.conta` e `transacoes.centro_custo` seguem o catálogo em `plano_contas.json`.

---

### 3.2 Como os dados são usados no prompt?
O agente vai usar **duas formas** de conhecimento:

1) **Dados estruturados (CSV/JSON)**
   - Consultados dinamicamente por tools (ex.: `get_dre(mes)`, `get_cashflow(periodo)`)
   - O resultado volta para o LLM como “evidência” (tabelas e métricas)

2) **Conhecimento textual (Markdown) — RAG / contexto curto**
   - `politicas_classificacao.md` e `glossario_financeiro.md` entram como:
     - Trechos relevantes recuperados (RAG) **ou**
     - Contexto fixo pequeno (resumo) no system prompt
   - Serve para padronizar explicações e reduzir respostas inconsistentes

**Regra de ouro:**
- **NÚMEROS** → tool/consulta
- **DEFINIÇÕES/REGRAS** → RAG ou contexto fixo (Markdown)

---

## 4) Exemplo de Contexto Montado

Abaixo um exemplo de como o orquestrador pode montar contexto para uma pergunta como:
“Feche a DRE de 2026-01 e explique variações”.

```text
Empresa:
- Nome: MetalNorte Serviços Industriais Ltda. (fictícia)
- Moeda: BRL
- Regime padrão: Competência (se o usuário pedir "caixa", alternar para Caixa)
- Mês em análise: 2026-01

Resultado da Tool: get_dre(mes="2026-01", regime="competencia")
- Receita líquida: R$ 1.245.300
- CSP/CMV: R$ 702.110
- Margem bruta: R$ 543.190 (43,6%)
- Despesas administrativas: R$ 188.450
- Despesas comerciais: R$ 96.200
- Resultado operacional: R$ 258.540

Comparativo (Tool): get_dre(mes="2025-12", regime="competencia")
- Receita líquida: R$ 1.310.900
- Margem bruta: 46,8%

Trechos recuperados (RAG):
- Política: “Fretes de compra” classificar em CSP/CMV quando diretamente ligados à entrega de insumos.
- Glossário: diferença entre regime de competência e regime de caixa.

Fontes:
- base: transacoes.csv (filtro: mes=2026-01, status=confirmado)
- base: orcamento_mensal.csv (se houver comparação vs orçado)
