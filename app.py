import streamlit as st
import requests
import pandas as pd

# -----------------------------
# CONFIG
# -----------------------------
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}

# -----------------------------
# FUNÇÕES
# -----------------------------
def get_contributors(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_pulls(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls?state=all"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_issues(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/issues?state=all"
    response = requests.get(url, headers=HEADERS)
    return response.json()

# -----------------------------
# STREAMLIT UI
# -----------------------------
st.title("📊 Engajamento no GitHub")

owner = st.text_input("Owner (usuário ou org)")
repo = st.text_input("Repositório")

if st.button("Analisar"):

    contributors = get_contributors(owner, repo)
    pulls = get_pulls(owner, repo)
    issues = get_issues(owner, repo)

    data = {}

    # Commits
    for c in contributors:
        user = c["login"]
        data[user] = {
            "commits": c["contributions"],
            "pull_requests": 0,
            "issues": 0
        }

    # PRs
    for pr in pulls:
        user = pr["user"]["login"]
        if user not in data:
            data[user] = {"commits": 0, "pull_requests": 0, "issues": 0}
        data[user]["pull_requests"] += 1

    # Issues
    for issue in issues:
        user = issue["user"]["login"]
        if user not in data:
            data[user] = {"commits": 0, "pull_requests": 0, "issues": 0}
        data[user]["issues"] += 1

    df = pd.DataFrame.from_dict(data, orient="index")
    df["score"] = df["commits"] + df["pull_requests"]*2 + df["issues"]

    df = df.sort_values("score", ascending=False)

    st.dataframe(df)

    st.bar_chart(df[["commits", "pull_requests", "issues"]])