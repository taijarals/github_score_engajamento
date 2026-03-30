import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# -----------------------------
# CONFIG
# -----------------------------
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
except:
    HEADERS = {}

# -----------------------------
# FUNÇÃO BASE
# -----------------------------
def fetch(url):
    response = requests.get(url, headers=HEADERS)
    try:
        data = response.json()
    except:
        return []

    if isinstance(data, dict) and "message" in data:
        st.error(data["message"])
        return []

    return data

# -----------------------------
# API CALLS
# -----------------------------
def get_contributors(owner, repo):
    return fetch(f"https://api.github.com/repos/{owner}/{repo}/contributors")

def get_pulls(owner, repo):
    return fetch(f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=100")

def get_issues(owner, repo):
    return fetch(f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100")

# -----------------------------
# UI
# -----------------------------
st.title("🚀 GitHub Engagement Analytics")

owner = st.text_input("Owner")
repo = st.text_input("Repositório")

if st.button("Analisar"):

    contributors = get_contributors(owner, repo)
    pulls = get_pulls(owner, repo)
    issues = get_issues(owner, repo)

    data = {}
    timeline = []

    # -----------------------------
    # COMMITS
    # -----------------------------
    for c in contributors:
        if "login" not in c:
            continue

        user = c["login"]
        data[user] = {
            "commits": c.get("contributions", 0),
            "prs_opened": 0,
            "prs_merged": 0,
            "issues": 0
        }

    # -----------------------------
    # PRs
    # -----------------------------
    for pr in pulls:
        if not pr.get("user"):
            continue

        user = pr["user"]["login"]

        if user not in data:
            data[user] = {"commits": 0, "prs_opened": 0, "prs_merged": 0, "issues": 0}

        data[user]["prs_opened"] += 1

        # PR aprovado (merged)
        if pr.get("merged_at"):
            data[user]["prs_merged"] += 1

        # timeline
        created = pr.get("created_at")
        if created:
            timeline.append({
                "date": created[:10],
                "user": user,
                "type": "PR"
            })

    # -----------------------------
    # ISSUES
    # -----------------------------
    for issue in issues:
        if "pull_request" in issue:
            continue

        if not issue.get("user"):
            continue

        user = issue["user"]["login"]

        if user not in data:
            data[user] = {"commits": 0, "prs_opened": 0, "prs_merged": 0, "issues": 0}

        data[user]["issues"] += 1

        created = issue.get("created_at")
        if created:
            timeline.append({
                "date": created[:10],
                "user": user,
                "type": "ISSUE"
            })

    # -----------------------------
    # DATAFRAME
    # -----------------------------
    df = pd.DataFrame.from_dict(data, orient="index")

    # 🧠 SCORE INTELIGENTE
    df["score"] = (
        df["commits"] * 1 +
        df["prs_opened"] * 2 +
        df["prs_merged"] * 5 +   # ⭐ PR aprovado vale mais
        df["issues"] * 1
    )

    df = df.sort_values("score", ascending=False)

    # -----------------------------
    # 🏆 LEADERBOARD
    # -----------------------------
    st.subheader("🏆 Leaderboard")

    top = df.head(10)
    for i, (user, row) in enumerate(top.iterrows(), start=1):
        medal = ["🥇", "🥈", "🥉"]
        prefix = medal[i-1] if i <= 3 else f"{i}º"

        st.write(f"{prefix} **{user}** → Score: {row['score']}")

    st.dataframe(df)

    # -----------------------------
    # 📊 GRÁFICO GERAL
    # -----------------------------
    st.subheader("📊 Distribuição")
    st.bar_chart(df[["commits", "prs_opened", "prs_merged", "issues"]])

    # -----------------------------
    # 📈 EVOLUÇÃO NO TEMPO
    # -----------------------------
    if timeline:
        df_time = pd.DataFrame(timeline)
        df_time["date"] = pd.to_datetime(df_time["date"])

        df_time = df_time.groupby("date").size().reset_index(name="atividades")

        st.subheader("📈 Evolução do Engajamento")
        st.line_chart(df_time.set_index("date"))

    else:
        st.warning("Sem dados de timeline")