# Data — PrismaIA Finance (FinaBot CFO)

Esta pasta contém a **base de conhecimento** (knowledge base) do agente, com dados fictícios e conteúdos de apoio (glossário, perfil e FAQ).
O objetivo é permitir que o agente responda com consistência e que as ferramentas (tools) consultem informações padronizadas.

> Importante: neste MVP, estes arquivos servem como **conhecimento e regras**.  
> As bases operacionais (transações, contas a pagar/receber, orçamento) serão adicionadas depois (ex.: `transacoes.csv`, `contas_a_pagar.csv`, etc.).

---

## Arquivos do dataset (MVP)

| Arquivo | Formato | O que contém | Como o agente usa |
|--------|---------|--------------|-------------------|
| `glossario_financeeiro.csv` | CSV (separador `;`) | Termos e definições de finanças corporativas | Explicar conceitos (competência vs caixa, DRE, margem, EBITDA...) e padronizar linguagem |
| `perfil_usuario.json` | JSON | Perfil da empresa/usuário (preferências, regime, moeda, centros de custo) | Personalizar respostas, aplicar defaults (ex.: regime padrão), impor políticas (alçada, confirmações) |
| `perguntas_frequentes.csv` | CSV (separador `;`) | FAQ do agente (perguntas comuns e respostas padrão) | Responder dúvidas repetidas com consistência e acelerar atendimento |
| `produtos_financeiros.json` | JSON | “Catálogo” de módulos/serviços do agente (relatórios, rotinas e automações) | Sugerir funcionalidades do próprio assistente (ex.: gerar DRE, projeção de caixa, aging) |

---

## Convenções (padrões)

### 1) CSV
- Encoding: UTF-8
- Separador: `;`
- Cabeçalho obrigatório
- Datas no padrão: `YYYY-MM-DD` quando existirem
- Valores monetários sempre numéricos (sem “R$” dentro do CSV)

### 2) JSON
- UTF-8
- Chaves em `snake_case`
- Estrutura estável para facilitar leitura por tools

---

## Esquema (campos) por arquivo

### `glossario_financeeiro.csv`
Colunas:
- `termo`: nome do termo
- `categoria`: ex. `dre`, `caixa`, `contabil`, `indicadores`, `processos`
- `definicao`: explicação curta e objetiva
- `exemplo`: exemplo prático aplicado ao dia a dia do financeiro
- `observacao`: opcional (ex.: “pode variar por empresa”)

### `perfil_usuario.json`
Campos principais:
- `empresa`: nome, setor, porte, moeda, timezone
- `preferencias`: regime padrão (`competencia`/`caixa`), granularidade (`mensal`/`semanal`/`diaria`)
- `politicas`: confirmações obrigatórias para ações, alçada de aprovação, regras de segurança
- `centros_de_custo`: lista padrão de CCs
- `tags_classificacao`: palavras-chave que ajudam classificação (ex.: “frete”, “manutenção”, “SaaS”)

### `perguntas_frequentes.csv`
Colunas:
- `id`: identificador (FAQ-001…)
- `categoria`: ex. `dre`, `caixa`, `ap`, `ar`, `seguranca`, `dados`
- `pergunta`: forma comum da pergunta
- `resposta_exemplo`: resposta padrão (sem números inventados)
- `observacao`: quando usar / o que pedir se faltar dado

### `produtos_financeiros.json`
Estrutura sugerida:
- `modulos`: lista de módulos (DRE, Fluxo de Caixa, A/P, A/R, Orçamento, Classificação)
- Cada módulo tem:
  - `nome`
  - `descricao`
  - `entradas` (o que precisa)
  - `saidas` (o que entrega)
  - `limitacoes` (o que não faz)
  - `exemplos_de_perguntas`

---

## Como validar rapidamente

Checklist:
- [ ] Arquivos existem e estão com os nomes corretos
- [ ] CSV abre sem quebrar colunas (separador `;`)
- [ ] JSON está válido (sem vírgula sobrando)
- [ ] Termos do glossário e FAQ não possuem dados sensíveis reais
- [ ] Nada depende de “inventar número”: sem valores não rastreáveis

---

## Próximos arquivos (fase operacional)

Depois destes 4 arquivos de knowledge base, adicionaremos:
- `transacoes.csv` (razão/lançamentos)
- `contas_a_pagar.csv` (A/P)
- `contas_a_receber.csv` (A/R)
- `orcamento_mensal.csv`
- `plano_contas.json`

Esses arquivos serão usados pelas tools para gerar números (DRE, KPIs, projeções).
