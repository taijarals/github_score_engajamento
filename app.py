import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta

# -----------------------------
# CONFIG
# -----------------------------
try:
    GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
except:
    HEADERS = {}

# -----------------------------
# API
# -----------------------------
def fetch(url):
    r = requests.get(url, headers=HEADERS)
    try:
        data = r.json()
    except:
        return []

    if isinstance(data, dict) and "message" in data:
        st.error(data["message"])
        return []

    return data

def get_contributors(owner, repo):
    return fetch(f"https://api.github.com/repos/{owner}/{repo}/contributors")

def get_pulls(owner, repo):
    return fetch(f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all&per_page=100")

def get_issues(owner, repo):
    return fetch(f"https://api.github.com/repos/{owner}/{repo}/issues?state=all&per_page=100")

# -----------------------------
# UI
# -----------------------------
st.title("🚀 GitHub Engagement Intelligence")

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

        data[c["login"]] = {
            "commits": c.get("contributions", 0),
            "prs_opened": 0,
            "prs_merged": 0,
            "issues": 0,
            "last_activity": None
        }

    # -----------------------------
    # PRs
    # -----------------------------
    for pr in pulls:
        if not pr.get("user"):
            continue

        user = pr["user"]["login"]

        if user not in data:
            data[user] = {"commits": 0, "prs_opened": 0, "prs_merged": 0, "issues": 0, "last_activity": None}

        data[user]["prs_opened"] += 1

        if pr.get("merged_at"):
            data[user]["prs_merged"] += 1

        created = pr.get("created_at")
        if created:
            date = created[:10]
            timeline.append({"date": date, "user": user})
            data[user]["last_activity"] = date

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
            data[user] = {"commits": 0, "prs_opened": 0, "prs_merged": 0, "issues": 0, "last_activity": None}

        data[user]["issues"] += 1

        created = issue.get("created_at")
        if created:
            date = created[:10]
            timeline.append({"date": date, "user": user})
            data[user]["last_activity"] = date

    # -----------------------------
    # DATAFRAME
    # -----------------------------
    df = pd.DataFrame.from_dict(data, orient="index")

    df["score"] = (
        df["commits"] +
        df["prs_opened"] * 2 +
        df["prs_merged"] * 5 +
        df["issues"]
    )

    # -----------------------------
    # 🧠 INATIVIDADE
    # -----------------------------
    today = datetime.now().date()

    def check_inactive(date):
        if pd.isna(date):
            return "🔴 Nunca ativo"
        diff = (today - datetime.strptime(date, "%Y-%m-%d").date()).days
        if diff > 30:
            return "🔴 Inativo"
        elif diff > 7:
            return "🟡 Atenção"
        else:
            return "🟢 Ativo"

    df["status"] = df["last_activity"].apply(check_inactive)

    # -----------------------------
    # 🏅 BADGES
    # -----------------------------
    def badge(row):
        if row["score"] > 100:
            return "🏆 Lenda"
        elif row["prs_merged"] > 10:
            return "🔥 Especialista em PR"
        elif row["commits"] > 50:
            return "💻 Dev Ativo"
        elif row["issues"] > 10:
            return "🐛 Caçador de Bugs"
        else:
            return "🌱 Iniciante"

    df["badge"] = df.apply(badge, axis=1)

    df = df.sort_values("score", ascending=False)

    # 🔥 SALVAR PARA OUTRAS PÁGINAS
    st.session_state["df"] = df
    st.session_state["timeline"] = timeline

    # -----------------------------
    # 🏆 LEADERBOARD
    # -----------------------------
    st.subheader("🏆 Leaderboard")

    for i, (user, row) in enumerate(df.head(10).iterrows(), start=1):
        medal = ["🥇", "🥈", "🥉"]
        prefix = medal[i-1] if i <= 3 else f"{i}º"

        st.write(f"{prefix} {user} | {row['badge']} | Score: {row['score']} | {row['status']}")

    st.dataframe(df)

    # -----------------------------
    # 📊 HEATMAP
    # -----------------------------
    if timeline:
        df_time = pd.DataFrame(timeline)
        df_time["date"] = pd.to_datetime(df_time["date"])

        heatmap = df_time.groupby("date").size().reset_index(name="atividade")

        st.subheader("📊 Atividade ao longo do tempo")
        st.bar_chart(heatmap.set_index("date"))

    # -----------------------------
    # 🔔 ALERTA
    # -----------------------------
    if timeline:
        df_time = pd.DataFrame(timeline)
        df_time["date"] = pd.to_datetime(df_time["date"])

        last_7 = df_time[df_time["date"] > datetime.now() - timedelta(days=7)].shape[0]
        prev_7 = df_time[
            (df_time["date"] <= datetime.now() - timedelta(days=7)) &
            (df_time["date"] > datetime.now() - timedelta(days=14))
        ].shape[0]

        if prev_7 > 0 and last_7 < prev_7:
            st.error("🔔 Queda de engajamento detectada!")
        else:
            st.success("Engajamento estável ou crescente 🚀")