import streamlit as st
import pandas as pd

st.title("👤 Análise Individual")

if "df" not in st.session_state:
    st.warning("Execute a análise na página principal primeiro")
    st.stop()

df = st.session_state["df"]
timeline = st.session_state["timeline"]

selected_user = st.selectbox("Selecione um usuário", df.index)

user_data = df.loc[selected_user]

st.subheader(f"👤 {selected_user}")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Commits", int(user_data["commits"]))
col2.metric("PRs", int(user_data["prs_opened"]))
col3.metric("PRs Merged", int(user_data["prs_merged"]))
col4.metric("Issues", int(user_data["issues"]))

st.metric("Score", int(user_data["score"]))
st.metric("Status", user_data["status"])
st.metric("Badge", user_data["badge"])

# timeline individual
user_timeline = [t for t in timeline if t["user"] == selected_user]

if user_timeline:
    df_user_time = pd.DataFrame(user_timeline)
    df_user_time["date"] = pd.to_datetime(df_user_time["date"])
    df_user_time = df_user_time.groupby("date").size().reset_index(name="atividades")

    st.line_chart(df_user_time.set_index("date"))