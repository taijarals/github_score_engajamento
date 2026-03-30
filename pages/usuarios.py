import streamlit as st
import pandas as pd
from datetime import datetime

st.title("👤 Análise Individual do Usuário")

# -----------------------------
# 🔒 VERIFICA SE TEM DADOS
# -----------------------------
if "df" not in st.session_state:
    st.warning("⚠️ Execute a análise na página principal primeiro")
    st.stop()

df = st.session_state["df"]
timeline = st.session_state["timeline"]

# -----------------------------
# 🎯 SELEÇÃO DO USUÁRIO
# -----------------------------
selected_user = st.selectbox("Selecione um usuário", df.index)

user_data = df.loc[selected_user]

st.markdown(f"## 👤 {selected_user}")

# -----------------------------
# 📊 MÉTRICAS BÁSICAS
# -----------------------------
col1, col2, col3, col4 = st.columns(4)

col1.metric("💻 Commits", int(user_data["commits"]))
col2.metric("📌 PRs Abertos", int(user_data["prs_opened"]))
col3.metric("✅ PRs Aprovados", int(user_data["prs_merged"]))
col4.metric("🐛 Issues", int(user_data["issues"]))

st.markdown("---")

# -----------------------------
# 📊 INDICADORES AVANÇADOS
# -----------------------------

# Engajamento
engajamento = user_data["score"]

# Aderência
if user_data["prs_opened"] > 0:
    aderencia = user_data["prs_merged"] / user_data["prs_opened"]
else:
    aderencia = 0

# Adesão
if user_data["last_activity"]:
    dias = (datetime.now() - datetime.strptime(user_data["last_activity"], "%Y-%m-%d")).days
    
    if dias <= 7:
        adesao_user = "Alta 🟢"
    elif dias <= 30:
        adesao_user = "Média 🟡"
    else:
        adesao_user = "Baixa 🔴"
else:
    adesao_user = "Nenhuma 🔴"

# -----------------------------
# 🧠 PERFIL AUTOMÁTICO
# -----------------------------
def perfil(row):
    if row["score"] > 80 and row["prs_merged"] > 5:
        return "🚀 Alta Performance"
    elif row["score"] > 30:
        return "📈 Engajado"
    elif row["status"] == "🔴 Inativo":
        return "⚠️ Inativo"
    else:
        return "🌱 Baixa participação"

perfil_user = perfil(user_data)

# -----------------------------
# 📊 EXIBIÇÃO DOS INDICADORES
# -----------------------------
st.subheader("📊 Indicadores do Usuário")

col5, col6, col7, col8 = st.columns(4)

col5.metric("⚡ Engajamento", int(engajamento))
col6.metric("🎯 Aderência", f"{aderencia:.1%}")
col7.metric("📌 Adesão", adesao_user)
col8.metric("🧠 Perfil", perfil_user)

# -----------------------------
# 🏅 BADGE E STATUS
# -----------------------------
st.markdown("---")

col9, col10 = st.columns(2)

col9.metric("🏅 Badge", user_data["badge"])
col10.metric("📊 Status", user_data["status"])

# -----------------------------
# 📈 HISTÓRICO DO USUÁRIO
# -----------------------------
user_timeline = [t for t in timeline if t["user"] == selected_user]

if user_timeline:
    df_user_time = pd.DataFrame(user_timeline)
    df_user_time["date"] = pd.to_datetime(df_user_time["date"])

    df_user_time = df_user_time.groupby("date").size().reset_index(name="atividades")

    st.subheader("📈 Evolução do Usuário")
    st.line_chart(df_user_time.set_index("date"))
else:
    st.warning("Sem histórico de atividades")

# -----------------------------
# 📊 DISTRIBUIÇÃO DE ATIVIDADES
# -----------------------------
st.subheader("📊 Distribuição de Atividades")

df_bar = pd.DataFrame({
    "tipo": ["Commits", "PRs Abertos", "PRs Aprovados", "Issues"],
    "quantidade": [
        user_data["commits"],
        user_data["prs_opened"],
        user_data["prs_merged"],
        user_data["issues"]
    ]
})

st.bar_chart(df_bar.set_index("tipo"))