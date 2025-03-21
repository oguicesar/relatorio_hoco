import streamlit as st
import pandas as pd
import plotly.express as px
import bcrypt
import os

st.set_page_config("Dashboard HOCO", layout="wide")

USER_FILE = "usuarios.csv"

def carregar_usuarios():
    if os.path.exists(USER_FILE):
        return pd.read_csv(USER_FILE)
    else:
        return pd.DataFrame(columns=["username", "name", "hashed_password"])

def salvar_usuarios(df):
    df.to_csv(USER_FILE, index=False)

def autenticar(username, senha, df_usuarios):
    user = df_usuarios[df_usuarios["username"] == username]
    if not user.empty:
        hashed = user.iloc[0]["hashed_password"]
        return bcrypt.checkpw(senha.encode(), hashed.encode()), user.iloc[0]["name"]
    return False, None

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.title("🔐 Acesso ao Dashboard HOCO")
    aba_login, aba_cadastro = st.tabs(["🔑 Já tenho cadastro", "📝 Quero me cadastrar"])
    df_usuarios = carregar_usuarios()

    with aba_login:
        login_user = st.text_input("Usuário")
        login_senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            ok, nome = autenticar(login_user, login_senha, df_usuarios)
            if ok:
                st.session_state["logado"] = True
                st.session_state["usuario"] = login_user
                st.session_state["nome"] = nome
                st.success(f"✅ Login realizado com sucesso! Bem-vindo, {nome}.")
                st.stop()
            else:
                st.error("❌ Usuário ou senha incorretos.")

    with aba_cadastro:
        new_name = st.text_input("Seu nome completo")
        new_user = st.text_input("Novo nome de usuário")
        new_pass = st.text_input("Nova senha", type="password")
        if st.button("Cadastrar"):
            if new_user in df_usuarios["username"].values:
                st.warning("⚠️ Usuário já existe.")
            elif not new_name or not new_user or not new_pass:
                st.warning("Preencha todos os campos.")
            else:
                hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt()).decode()
                novo = pd.DataFrame([[new_user, new_name, hashed]], columns=df_usuarios.columns)
                df_usuarios = pd.concat([df_usuarios, novo], ignore_index=True)
                salvar_usuarios(df_usuarios)
                st.success("✅ Cadastro realizado com sucesso!")
                st.download_button("⬇ Baixar novo arquivo de usuários", df_usuarios.to_csv(index=False), file_name="usuarios.csv")
                st.stop()

if st.session_state.get("logado"):
    st.sidebar.success(f"👤 Bem-vindo, {st.session_state['nome']}!")

    st.title("📊 Dashboard de Faturamento - HOCO")
    uploaded_file = st.file_uploader("📂 Upload do arquivo .csv", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file, encoding="latin1", sep=";", on_bad_lines="skip", engine="python")
            df["Valor Unitário"] = pd.to_numeric(df["Valor Unitário"], errors="coerce")
            df.dropna(subset=["Valor Unitário"], inplace=True)

            df["Data de realização"] = pd.to_datetime(df["Data de realização"], errors="coerce")
            df["Ano-Mês"] = df["Data de realização"].dt.to_period("M").astype(str)
            df["Dia da semana"] = df["Data de realização"].dt.day_name()

            st.sidebar.header("🎯 Filtros")
            anos = st.sidebar.multiselect("Ano", sorted(df["Ano"].unique()), default=sorted(df["Ano"].unique()))
            meses = st.sidebar.multiselect("Mês", sorted(df["Mês"].unique()), default=sorted(df["Mês"].unique()))
            medicos = st.sidebar.multiselect("Médico", df["Médico"].unique(), default=df["Médico"].unique())
            unidades = st.sidebar.multiselect("Unidade da Clínica", df["Unidade da Clínica"].unique(), default=df["Unidade da Clínica"].unique())
            atendimentos = st.sidebar.multiselect("Atendimento", df["Atendimento"].unique(), default=df["Atendimento"].unique())
            planos = st.sidebar.multiselect("Categoria", df["Categoria"].unique(), default=df["Categoria"].unique())

            df_filtrado = df[
                (df["Ano"].isin(anos)) &
                (df["Mês"].isin(meses)) &
                (df["Médico"].isin(medicos)) &
                (df["Unidade da Clínica"].isin(unidades)) &
                (df["Atendimento"].isin(atendimentos)) &
                (df["Categoria"].isin(planos))
            ]

            abas = st.tabs([
                "📊 Visão Geral",
                "👨‍⚕️ Médicos",
                "💳 Planos",
                "🏢 Unidades",
                "📈 Tendência Temporal",
                "📋 Resumo Executivo",
                "📈 Evolução por Tipo de Atendimento"
            ])

            with abas[0]:  # Visão Geral
                st.header("📊 Visão Geral")
                faturamento_total = df_filtrado["Valor Unitário"].sum()
                ticket_medio_geral = df_filtrado["Valor Unitário"].mean()
                pacientes_unicos = df_filtrado["Paciente"].nunique()
                total_atendimentos = len(df_filtrado)

                col1, col2, col3 = st.columns(3)
                col1.metric("🎯 Ticket Médio Geral", f"R$ {ticket_medio_geral:,.2f}")
                col2.metric("👥 Pacientes Atendidos", f"{pacientes_unicos}")
                col3.metric("🧾 Total de Atendimentos", f"{total_atendimentos:,}")

            with abas[3]:  # Unidades
                st.header("🏢 Análises por Unidade")
                fat_uni = df_filtrado.groupby("Unidade da Clínica")["Valor Unitário"].sum().reset_index()
                fig = px.bar(fat_uni, x="Unidade da Clínica", y="Valor Unitário", title="Faturamento por Unidade")
                st.plotly_chart(fig, use_container_width=True)

            with abas[5]:  # Resumo Executivo
                st.header("📋 Resumo Executivo")
                resumo = df_filtrado.groupby("Médico").agg({
                    "Paciente": "count",
                    "Valor Unitário": ["mean", "sum"]
                }).reset_index()
                resumo.columns = ["Médico", "Atendimentos", "Ticket Médio", "Faturamento Total"]
                st.dataframe(resumo.style.format({"Ticket Médio": "R$ {:,.2f}", "Faturamento Total": "R$ {:,.2f}"}))

            with abas[6]:  # Evolução por Tipo de Atendimento
                st.subheader("📈 Evolução por Tipo de Atendimento")
                evolucao_tipo = df_filtrado.groupby(["Ano-Mês", "Atendimento"])["Valor Unitário"].sum().reset_index()
                fig = px.line(evolucao_tipo, x="Ano-Mês", y="Valor Unitário", color="Atendimento", title="Tendência por Tipo de Atendimento")
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {e}")

    else:
        st.info("⬆ Faça upload de um arquivo .csv com os dados de faturamento para começar.")
