import streamlit as st
import requests
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
except:
    HEADERS = {}

# -----------------------------
# FUNÇÃO GENÉRICA (TRATAMENTO DE ERRO)
# -----------------------------
def fetch_github_data(url):
    response = requests.get(url, headers=HEADERS)

    try:
        data = response.json()
    except:
        st.error("Erro ao interpretar resposta da API")
        return []

    # Se vier erro da API
    if isinstance(data, dict) and "message" in data:
        st.error(f"Erro da API: {data['message']}")
        return []

    return data

# -----------------------------
# FUNÇÕES
# -----------------------------
def get_contributors(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    return fetch_github_data(url)

def get_pulls(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all"
    return fetch_github_data(url)

def get_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"
    return fetch_github_data(url)

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("📊 Engajamento no GitHub")

owner = st.text_input("Owner (usuário ou org)")
repo = st.text_input("Repositório")

if st.button("Analisar"):

    if not owner or not repo:
        st.warning("Preencha owner e repositório")
        st.stop()

    contributors = get_contributors(owner, repo)
    pulls = get_pulls(owner, repo)
    issues = get_issues(owner, repo)

    data = {}

    # -----------------------------
    # COMMITS
    # -----------------------------
    for c in contributors:
        if "login" not in c:
            continue

        user = c["login"]
        data[user] = {
            "commits": c.get("contributions", 0),
            "pull_requests": 0,
            "issues": 0
        }

    # -----------------------------
    # PRs
    # -----------------------------
    for pr in pulls:
        if "user" not in pr or pr["user"] is None:
            continue

        user = pr["user"].get("login")
        if not user:
            continue

        if user not in data:
            data[user] = {"commits": 0, "pull_requests": 0, "issues": 0}

        data[user]["pull_requests"] += 1

    # -----------------------------
    # ISSUES (filtrar PRs)
    # -----------------------------
    for issue in issues:

        # GitHub mistura PR com issue → ignorar PR
        if "pull_request" in issue:
            continue

        if "user" not in issue or issue["user"] is None:
            continue

        user = issue["user"].get("login")
        if not user:
            continue

        if user not in data:
            data[user] = {"commits": 0, "pull_requests": 0, "issues": 0}

        data[user]["issues"] += 1

    # -----------------------------
    # DATAFRAME
    # -----------------------------
    if not data:
        st.warning("Nenhum dado encontrado. Verifique o repositório ou permissões.")
        st.stop()

    df = pd.DataFrame.from_dict(data, orient="index")

    df["score"] = (
        df["commits"] +
        df["pull_requests"] * 2 +
        df["issues"]
    )

    df = df.sort_values("score", ascending=False)

    # -----------------------------
    # OUTPUT
    # -----------------------------
    st.subheader("📋 Tabela de Engajamento")
    st.dataframe(df)

    st.subheader("📊 Gráfico")
    st.bar_chart(df[["commits", "pull_requests", "issues"]])