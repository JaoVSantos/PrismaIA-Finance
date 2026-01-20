import json
import re
import difflib
from pathlib import Path

import pandas as pd
import streamlit as st


# -----------------------------
# Configuração do app
# -----------------------------
st.set_page_config(
    page_title="Prisma-IA Finance",
    layout="centered"
)

st.title("🤖 Prisma-IA Finance")
st.caption("Assistente financeiro corporativo (MVP). Pode escrever do seu jeito — eu tento entender 😊")


DATA_DIR = Path(__file__).resolve().parents[1] / "data"


# -----------------------------
# Carregamento de arquivos
# -----------------------------
def carregar_json(nome_arquivo: str) -> dict:
    caminho = DATA_DIR / nome_arquivo
    if not caminho.exists():
        return {}
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def carregar_csv(nome_arquivo: str) -> pd.DataFrame:
    caminho = DATA_DIR / nome_arquivo
    if not caminho.exists():
        return pd.DataFrame()

    try:
        return pd.read_csv(caminho, sep=";", encoding="utf-8")
    except Exception:
        try:
            return pd.read_csv(caminho, sep=",", encoding="utf-8")
        except Exception:
            return pd.DataFrame()


# -----------------------------
# Helpers de texto
# -----------------------------
def normalizar_texto(txt: str) -> str:
    txt = txt.strip().lower()
    txt = re.sub(r"\s+", " ", txt)
    return txt


def extrair_mes(txt: str) -> str | None:
    """
    Encontra mês no formato YYYY-MM ou YYYY/MM e retorna YYYY-MM.
    """
    t = txt.replace("/", "-")
    m = re.search(r"\b(20\d{2})-(0[1-9]|1[0-2])\b", t)
    return m.group(0) if m else None


def formatar_brl(valor: float) -> str:
    s = f"{valor:,.2f}"
    s = s.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {s}"


def pediu_lista_perguntas(txt: str) -> bool:
    """
    Detecta se o usuário quer exemplos do que pode perguntar.
    """
    t = normalizar_texto(txt)
    gatilhos = [
        "quais perguntas", "que perguntas", "o que posso perguntar", "o que eu posso perguntar",
        "como posso perguntar", "exemplos de perguntas", "me dê exemplos", "me de exemplos",
        "o que você responde", "o que voce responde", "assuntos que você responde", "assuntos que voce responde",
        "lista de perguntas", "perguntas que você responde", "perguntas que voce responde"
    ]
    return any(g in t for g in gatilhos)


def listar_perguntas_faq(faq_df: pd.DataFrame, limite: int = 30) -> str:
    """
    Lista as perguntas do CSV (até 'limite').
    """
    if faq_df.empty or "pergunta" not in faq_df.columns:
        return (
            "Eu ainda não encontrei o arquivo `data/perguntas_frequentes.csv` (ou ele está sem a coluna `pergunta`).\n\n"
            "Se você criar/colar esse CSV, eu consigo listar exemplos do que posso responder."
        )

    perguntas = (
        faq_df["pergunta"]
        .dropna()
        .astype(str)
        .map(lambda x: x.strip())
        .tolist()
    )

    if not perguntas:
        return "O arquivo `perguntas_frequentes.csv` está vazio na coluna `pergunta`."

    perguntas = perguntas[:limite]

    texto = "Aqui estão alguns exemplos de perguntas que eu consigo responder:\n\n"
    texto += "\n".join([f"- {p}" for p in perguntas])
    texto += "\n\nSe quiser, você também pode perguntar do seu jeito — eu tento entender mesmo fora desses exemplos."
    return texto


# -----------------------------
# FAQ (banco de perguntas)
# -----------------------------
def buscar_resposta_faq(pergunta: str, faq_df: pd.DataFrame) -> str | None:
    """
    Busca resposta aproximada no perguntas_frequentes.csv.
    """
    if faq_df.empty:
        return None

    colunas_ok = {"pergunta", "resposta_exemplo"}
    if not colunas_ok.issubset(set(faq_df.columns)):
        return None

    user = normalizar_texto(pergunta)

    melhor_score = 0.0
    melhor_resposta = None

    for _, row in faq_df.iterrows():
        q = str(row.get("pergunta", "")).strip()
        a = str(row.get("resposta_exemplo", "")).strip()
        if not q or not a:
            continue

        qn = normalizar_texto(q)

        contem = 1.0 if (qn in user or user in qn) else 0.0
        sim = difflib.SequenceMatcher(None, user, qn).ratio()

        score = max(contem, sim)
        if score > melhor_score:
            melhor_score = score
            melhor_resposta = a

    if melhor_score >= 0.83:
        return melhor_resposta

    return None


# -----------------------------
# Regras do MVP (dados)
# -----------------------------
def transacoes_ok(df: pd.DataFrame) -> tuple[bool, str]:
    if df.empty:
        return False, (
            "Eu ainda não encontrei transações em `data/transacoes.csv`.\n\n"
            "Se você colar um dataset lá, eu consigo calcular entradas e saídas por mês."
        )

    esperados = {"data", "tipo", "valor", "descricao"}
    faltando = [c for c in esperados if c not in set(df.columns)]
    if faltando:
        return False, (
            "Seu `transacoes.csv` existe, mas está faltando algumas colunas:\n"
            f"- {', '.join(faltando)}\n\n"
            "Colunas mínimas esperadas: **data;tipo;valor;descricao**."
        )

    return True, ""


def preparar_transacoes(df: pd.DataFrame) -> pd.DataFrame:
    df2 = df.copy()

    df2["tipo"] = df2["tipo"].astype(str).str.lower().str.strip()
    df2["data"] = pd.to_datetime(df2["data"], errors="coerce")

    df2["valor"] = (
        df2["valor"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
    )
    df2["valor"] = pd.to_numeric(df2["valor"], errors="coerce").fillna(0.0)

    return df2


def calcular_caixa(df: pd.DataFrame, mes: str | None) -> dict:
    df2 = preparar_transacoes(df)

    if mes:
        ano, m = mes.split("-")
        ano, m = int(ano), int(m)
        df2 = df2[(df2["data"].dt.year == ano) & (df2["data"].dt.month == m)]

    entradas = df2.loc[df2["tipo"].isin(["entrada", "credito", "crédito"]), "valor"].sum()
    saidas = df2.loc[df2["tipo"].isin(["saida", "saída", "debito", "débito"]), "valor"].sum()
    liquido = entradas - saidas

    return {
        "entradas": float(entradas),
        "saidas": float(saidas),
        "liquido": float(liquido),
        "qtd": int(len(df2))
    }


# -----------------------------
# Interpretação de intenção (mais flexível)
# -----------------------------
def detectar_intencao(txt: str) -> str:
    t = normalizar_texto(txt)

    fora = [
        "previsao do tempo", "previsão do tempo", "clima", "temperatura",
        "jogo", "futebol", "noticias", "notícias", "horoscopo", "horóscopo"
    ]
    if any(x in t for x in fora):
        return "fora_escopo"

    if any(x in t for x in ["o que voce faz", "o que você faz", "ajuda", "como funciona", "quem e voce", "quem é voce", "quem é você"]):
        return "ajuda"

    if any(x in t for x in ["modulos", "módulos", "recursos", "funcionalidades", "o que tem", "o que você tem", "o que voce tem"]):
        return "modulos"

    caixa_keywords = [
        "caixa", "fluxo", "saldo",
        "entrou", "entrada", "recebi", "recebimento", "recebimentos",
        "saiu", "saida", "saída", "paguei", "pagamento", "pagamentos",
        "gastei", "gasto", "gastos", "despesa", "despesas"
    ]
    if any(k in t for k in caixa_keywords):
        return "caixa"

    if any(x in t for x in ["dre", "lucro", "resultado", "margem", "ebitda"]):
        return "dre"

    return "geral"


def detectar_subpedido_caixa(txt: str) -> str:
    t = normalizar_texto(txt)

    quer_saida = any(x in t for x in ["saiu", "saida", "saída", "gastos", "gasto", "despesa", "despesas", "paguei", "pagamentos", "pagar"])
    quer_entrada = any(x in t for x in ["entrou", "entrada", "recebi", "recebimento", "recebimentos", "receber"])

    if quer_saida and not quer_entrada:
        return "somente_saidas"
    if quer_entrada and not quer_saida:
        return "somente_entradas"

    return "resumo"


# -----------------------------
# Respostas (mais amigáveis)
# -----------------------------
def responder(pergunta: str, perfil: dict, catalogo: dict, faq_df: pd.DataFrame, transacoes_df: pd.DataFrame) -> str:
    # 0) Se o usuário pedir exemplos do que pode perguntar, lista as 30 perguntas do FAQ
    if pediu_lista_perguntas(pergunta):
        return listar_perguntas_faq(faq_df, limite=30)

    # 1) Tentar FAQ primeiro (banco de perguntas “próximas”)
    resposta_faq = buscar_resposta_faq(pergunta, faq_df)
    if resposta_faq:
        return resposta_faq

    # 2) Intent detection
    intencao = detectar_intencao(pergunta)
    mes = extrair_mes(pergunta)

    if intencao == "fora_escopo":
        return (
            "Eu não consigo ajudar com isso 😅\n\n"
            "Mas posso ajudar com **finanças da empresa**, como entradas/saídas do caixa e (mais pra frente) DRE.\n"
            "Se quiser, me pergunte algo como: “quanto saiu em 2025-12?”"
        )

    if intencao == "ajuda":
        return (
            "Claro! Eu sou o **Prisma-IA Finance (Seu bot de auxílio financeiro)**.\n\n"
            "Você pode perguntar de um jeito bem simples, por exemplo:\n"
            "- “quanto saiu em 2025-12?”\n"
            "- “quanto entrou em 2026-01?”\n"
            "- “como foi o caixa em 2025-11?”\n\n"
            "Se quiser ver uma lista maior do que eu respondo, pergunte: **“quais perguntas você responde?”**"
        )

    if intencao == "modulos":
        modulos = catalogo.get("modulos", [])
        if not modulos:
            return (
                "Eu não encontrei o arquivo `data/produtos_financeiros.json`.\n"
                "Se você criar/colar ele, eu consigo listar as funcionalidades direitinho."
            )

        nomes = [m.get("nome", "Módulo") for m in modulos]
        return (
            "Aqui estão as funcionalidades do assistente:\n\n"
            + "\n".join([f"- {n}" for n in nomes])
        )

    if intencao == "dre":
        return (
            "Boa! Eu consigo chegar em **DRE gerencial**, mas ainda falta evoluir o `transacoes.csv`.\n\n"
            "Para montar a DRE, a gente vai precisar adicionar colunas como **conta** e **centro de custo** "
            "(e definir um plano de contas).\n"
            "Quando você quiser, eu te passo exatamente o modelo."
        )

    if intencao == "caixa":
        ok, msg = transacoes_ok(transacoes_df)
        if not ok:
            return msg

        subpedido = detectar_subpedido_caixa(pergunta)
        resumo = calcular_caixa(transacoes_df, mes)

        periodo = mes if mes else "no período total disponível"

        if subpedido == "somente_saidas":
            return (
                f"Beleza! Somando **tudo o que saiu** {periodo}, eu encontrei:\n\n"
                f"➡️ **Saídas:** {formatar_brl(resumo['saidas'])}\n\n"
                f"(Baseado em {resumo['qtd']} movimentações do seu `transacoes.csv`.)"
            )

        if subpedido == "somente_entradas":
            return (
                f"Certo! Somando **tudo o que entrou** {periodo}, eu encontrei:\n\n"
                f"➡️ **Entradas:** {formatar_brl(resumo['entradas'])}\n\n"
                f"(Baseado em {resumo['qtd']} movimentações do seu `transacoes.csv`.)"
            )

        return (
            f"Aqui vai um resumo do **caixa** {periodo}:\n\n"
            f"✅ Entrou: **{formatar_brl(resumo['entradas'])}**\n"
            f"✅ Saiu: **{formatar_brl(resumo['saidas'])}**\n"
            f"📌 Resultado do período: **{formatar_brl(resumo['liquido'])}**\n\n"
            f"(Baseado em {resumo['qtd']} movimentações do seu `transacoes.csv`.)\n\n"
            "Se quiser, pode perguntar só uma parte, tipo: “quanto saiu em 2025-12?”"
        )

    return (
        "Entendi parcialmente — deixa eu te guiar rapidinho 😊\n\n"
        "Eu consigo ajudar principalmente com **entradas e saídas do caixa**.\n"
        "Tente perguntar assim:\n"
        "- “quanto saiu em 2025-12?”\n"
        "- “quanto entrou em 2026-01?”\n"
        "- “como foi o caixa em 2025-11?”\n\n"
        "Se você quiser ver uma lista maior do que eu respondo, pergunte: **“quais perguntas você responde?”**"
    )


# -----------------------------
# UI
# -----------------------------
perfil = carregar_json("perfil_usuario.json")
catalogo = carregar_json("produtos_financeiros.json")
faq_df = carregar_csv("perguntas_frequentes.csv")
transacoes_df = carregar_csv("transacoes.csv")

empresa_nome = perfil.get("empresa", {}).get("nome_fantasia", "sua empresa")
st.write(f"Olá! Eu posso ajudar você a entender as movimentações financeiras da **{empresa_nome}**.")

pergunta_usuario = st.text_input("Digite sua pergunta (ex.: “quanto saiu em 2025-12?”):")

if pergunta_usuario:
    resposta = responder(pergunta_usuario, perfil, catalogo, faq_df, transacoes_df)
    st.success(resposta)
