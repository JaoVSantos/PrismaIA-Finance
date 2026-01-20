# 🤖 Prisma-IA Finance (FinaBot CFO) — Agente Financeiro Inteligente com IA Generativa

## Contexto

Assistentes virtuais no setor financeiro estão evoluindo de chatbots reativos para **agentes inteligentes e proativos**.  
Este repositório é o protótipo do **Prisma-IA Finance (FinaBot CFO)**, um assistente focado em **finanças corporativas (SMB)** para apoiar rotinas como:

- **Entender rapidamente o caixa** (quanto entrou, quanto saiu, resultado do mês)
- **Organizar e explicar dados** de forma simples (sem exigir linguagem técnica)
- **Personalizar respostas** com base no contexto da empresa (perfil do usuário)
- **Evitar alucinações**: números sempre vêm de dados (`CSV/JSON`), não de “achismo”
- Evoluir para um agente com **IA Generativa + tools** (onde o modelo conversa e o código calcula)

> [!TIP]
> Na pasta [`examples/`](./examples/) você pode manter referências e inspirações de implementação.

---

## O que este agente resolve (caso de uso)

Empresas pequenas e médias normalmente têm dados espalhados e pouco tempo para análise.  
O PrismaIA Finance ajuda a responder perguntas do dia a dia como:

- “**Quanto saiu em 2025-12?**”
- “**Quanto entrou em 2026-01?**”
- “**Como foi o caixa em 2025-11?**”
- “Quais módulos/funcionalidades o assistente oferece?”

Hoje (MVP) ele trabalha com **caixa realizado** (entradas/saídas do `transacoes.csv`) e conteúdos de apoio (FAQ e catálogo).  
Nas próximas etapas, ele evolui para DRE gerencial, orçamento e análises mais completas.

---

## Persona e Tom de Voz

- **Claro e amigável**, sem termos técnicos desnecessários
- **Direto e didático**, como alguém do financeiro explicando para qualquer pessoa
- Sempre propõe **próximos passos** (ex.: pedir um mês, explicar o que falta no dado)
- Quando algo está fora do escopo (ex.: previsão do tempo), responde com educação e redireciona

---

## Como evitar “alucinações” (segurança)

Regras do projeto:

- **NÚMEROS** (entradas/saídas/totais) só aparecem quando o cálculo vem dos dados (`CSV`).
- Se faltar dado, o agente responde: **“não encontrei essa informação na base”** e diz o que precisa ser adicionado.
- Perguntas fora do escopo são recusadas com educação.
- O MVP não faz ações destrutivas nem altera dados automaticamente.

---

## O que você deve entregar (no estilo deste projeto)

### 1) Documentação do Agente
Defina **o que** o agente faz e **como** ele funciona:

- Caso de uso (finanças corporativas SMB)
- Persona / Tom de voz
- Arquitetura (fluxo de dados)
- Segurança (anti-alucinação, escopo)

📄 Arquivo: [`docs/01-documentacao-agente.md`](./docs/01-documentacao-agente.md)

---

### 2) Base de Conhecimento (dados mockados)

Os dados ficam na pasta [`data/`](./data/). Este projeto usa:

| Arquivo | Formato | Para que serve |
|--------|---------|----------------|
| `transacoes.csv` | CSV | Base para cálculo de **caixa realizado** (entradas/saídas por período) |
| `historico.csv` | CSV | Glossário / histórico textual (apoio para respostas consistentes e didáticas) |
| `perfil_usuario.json` | JSON | Contexto da empresa e políticas do agente (defaults e segurança) |
| `produtos_financeiros.json` | JSON | Catálogo de módulos/funcionalidades do assistente |
| `perguntas_frequentes.csv` | CSV | Banco de perguntas/respostas (FAQ), usado como “memória de ajuda” |

📄 Arquivo: [`docs/02-base-conhecimento.md`](./docs/02-base-conhecimento.md)

---

### 3) Prompts do Agente (fase IA Generativa)
Documente os prompts que definem comportamento e restrições:

- System Prompt (regras e segurança)
- Exemplos de interação (entrada/saída esperada)
- Edge cases (fora do escopo, falta de dados)

📄 Arquivo: [`docs/03-prompts.md`](./docs/03-prompts.md)

> Obs.: O MVP atual funciona sem LLM. A parte de prompts entra na fase 2, quando integrar IA Generativa.

---

### 4) Aplicação Funcional

O protótipo está na pasta [`src/`](./src/), usando **Streamlit**.

✅ O app foi pensado para aceitar **texto livre** e entender perguntas simples do dia a dia, como:
- “quanto saiu em 2025-12”
- “quanto entrou em 2026-01”
- “como foi o caixa em 2025-11”

📁 Pasta: [`src/`](./src/)  
📄 Arquivo: [`src/app.py`](./src/app.py)

---

### 5) Avaliação e Métricas

A qualidade do agente é medida por:
- Assertividade (responder o que foi pedido)
- Segurança (não inventar números, recusar fora do escopo)
- Clareza (resposta fácil de entender)
- Consistência (mesmo padrão em respostas parecidas)

📄 Arquivo: [`docs/04-metricas.md`](./docs/04-metricas.md)



## Como rodar o projeto (local)

Na raiz do repositório:

pip install streamlit pandas
streamlit run src/app.py

### 📂 Estrutura do Repositório

```text
📁 PRISMAIA-FINANCE/
│
├── 📄 README.md
│
├── 📁 data/                          # Dados mockados para o agente
│   ├── historico.csv                 # Glossário/histórico (CSV)
│   ├── perfil_usuario.json           # Perfil da empresa/usuário (JSON)
│   ├── produtos_financeiros.json     # Catálogo de módulos (JSON)
│   ├── perguntas_frequentes.csv      # FAQ (CSV)
│   └── transacoes.csv                # Transações para cálculo de caixa (CSV)
│
├── 📁 docs/                          # Documentação do projeto
│   ├── 01-documentacao-agente.md     # Caso de uso e arquitetura
│   ├── 02-base-conhecimento.md       # Estratégia de dados
│   ├── 03-prompts.md                 # Engenharia de prompts (fase 2)
│   ├── 04-metricas.md                # Avaliação e métricas
│   └── 05-pitch.md                   # (opcional) roteiro do pitch
│
├── 📁 src/                           # Código da aplicação
│   └── app.py                        # Streamlit (MVP)
│
├── 📁 assets/                        # Imagens e diagramas
│   └── ...
│
└── 📁 examples/                      # Referências e exemplos
    └── README.md
```

### 🔐 Segurança e Confiabilidade

- Não há uso de LLMs
- Não há geração de texto livre
- Todas as respostas são previamente definidas
- Perguntas fora do escopo recebem respostas neutras e seguras

Isso garante:

- previsibilidade
- controle
- ausência de alucinações

---
