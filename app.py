import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit_authenticator as stauth

# === LOGIN CONFIG ===
names = ['Admin User', 'Gestor HOCO']
usernames = ['admin', 'gestor']
# Hash da senha '123'
hashed_passwords = [
    "$2b$12$uECzIYHMbFfW5FfpP0RZeePRv9tNW7oibvxn43AO80gjKjswTE6Ta",
    "$2b$12$uECzIYHMbFfW5FfpP0RZeePRv9tNW7oibvxn43AO80gjKjswTE6Ta"
]

credentials = {
    "usernames": {
        usernames[0]: {"name": names[0], "password": hashed_passwords[0]},
        usernames[1]: {"name": names[1], "password": hashed_passwords[1]},
    }
}

authenticator = stauth.Authenticate(
    credentials,
    "dashboard_hoco_cookie",
    "random_signature_key",
    cookie_expiry_days=1
)

# ✅ Localização do formulário de login corrigida para "main"
name, authentication_status, username = authenticator.login("Login")


if authentication_status == False:
    st.error("❌ Usuário ou senha incorretos")

if authentication_status == None:
    st.warning("👋 Faça login para acessar o dashboard.")

# ==== APÓS LOGIN VALIDADO ====
if authentication_status:
    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"👤 Bem-vindo, {name}!")

    st.set_page_config(page_title="Dashboard HOCO", layout="wide")
    st.title("📊 Dashboard de Faturamento - Simulação")

    st.markdown("""
    Faça o upload do arquivo `.csv` com as seguintes colunas:

    - Número
    - Paciente
    - Categoria
    - Médico
    - Atendimento
    - Valor Unitário
    - Data de realização
    - Dia da semana
    - Mês
    - Ano
    - Unidade da Clínica
    """)

    uploaded_file = st.file_uploader("📂 Upload do arquivo .csv", type=["csv"])

    if uploaded_file:
        try:
            df = pd.read_csv(
                uploaded_file,
                encoding="latin1",
                sep=";",
                on_bad_lines="skip",
                engine="python"
            )

            df["Valor Unitário"] = pd.to_numeric(df["Valor Unitário"], errors="coerce")
            df.dropna(subset=["Valor Unitário"], inplace=True)

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

            df_filtrado["Ano-Mês"] = pd.to_datetime(df_filtrado["Ano"].astype(str) + "-" + df_filtrado["Mês"].astype(str) + "-01")

            aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
                "📊 Visão Geral",
                "👨‍⚕️ Médicos",
                "💳 Planos",
                "🏢 Unidades",
                "📈 Tendência Temporal",
                "📋 Resumo Executivo"
            ])

            with aba1:
                st.header("📊 Visão Geral")

                faturamento_total = df_filtrado["Valor Unitário"].sum()
                particular_total = df_filtrado[df_filtrado["Categoria"].str.upper() == "PARTICULAR"]["Valor Unitário"].sum()
                perc_particular = (particular_total / faturamento_total * 100) if faturamento_total > 0 else 0

                ticket_medio_geral = df_filtrado["Valor Unitário"].mean()
                pacientes_unicos = df_filtrado["Paciente"].nunique()
                total_atendimentos = len(df_filtrado)

                col1, col2, col3 = st.columns(3)
                col1.metric("🎯 Ticket Médio Geral", f"R$ {ticket_medio_geral:,.2f}")
                col2.metric("👥 Pacientes Atendidos", f"{pacientes_unicos}")
                col3.metric("🧾 Total de Atendimentos", f"{total_atendimentos:,}")

                st.subheader("📄 Visualização da Base")
                st.dataframe(df_filtrado.head(100))

            with aba2:
                st.header("👨‍⚕️ Análises por Médico")

                ticket_medio_medico = df_filtrado.groupby("Médico")["Valor Unitário"].mean().reset_index().sort_values(by="Valor Unitário", ascending=False)
                fig_tm, ax_tm = plt.subplots(figsize=(10, 5))
                sns.barplot(data=ticket_medio_medico, y="Médico", x="Valor Unitário", ax=ax_tm, palette="viridis")
                ax_tm.set_xlabel("Ticket Médio (R$)")
                st.pyplot(fig_tm)

                fat_medico = df_filtrado.groupby("Médico")["Valor Unitário"].sum().reset_index().sort_values(by="Valor Unitário", ascending=False)
                fig1, ax1 = plt.subplots(figsize=(10, 5))
                sns.barplot(y="Médico", x="Valor Unitário", data=fat_medico, ax=ax1)
                ax1.set_xlabel("Faturamento (R$)")
                st.pyplot(fig1)

            with aba3:
                st.header("💳 Análises por Plano")

                faturamento_categoria = df_filtrado.groupby("Categoria")["Valor Unitário"].sum().reset_index()
                faturamento_categoria["%"] = (faturamento_categoria["Valor Unitário"] / faturamento_total) * 100
                faturamento_categoria = faturamento_categoria.sort_values(by="Valor Unitário", ascending=False)

                st.dataframe(faturamento_categoria.style.format({"Valor Unitário": "R$ {:,.2f}", "%": "{:.1f}%"}))

                fig2, ax2 = plt.subplots(figsize=(10, 5))
                sns.barplot(y="Categoria", x="Valor Unitário", data=faturamento_categoria, ax=ax2)
                ax2.set_xlabel("Faturamento (R$)")
                st.pyplot(fig2)

            with aba4:
                st.header("🏢 Análises por Unidade")

                fat_unidade = df_filtrado.groupby("Unidade da Clínica")["Valor Unitário"].sum().reset_index()
                fig_u, ax_u = plt.subplots(figsize=(10, 4))
                sns.barplot(y="Unidade da Clínica", x="Valor Unitário", data=fat_unidade, ax=ax_u)
                st.pyplot(fig_u)

            with aba5:
                st.header("📈 Tendência Temporal")

                evolucao_total = df_filtrado.groupby("Ano-Mês")["Valor Unitário"].sum().reset_index()
                fig_ev, ax_ev = plt.subplots(figsize=(10, 4))
                sns.lineplot(data=evolucao_total, x="Ano-Mês", y="Valor Unitário", marker="o", ax=ax_ev)
                ax_ev.set_title("Faturamento Total por Mês")
                st.pyplot(fig_ev)

                st.subheader("👨‍⚕️ Top 5 Médicos - Evolução Mensal")
                top5_medicos = df_filtrado.groupby("Médico")["Valor Unitário"].sum().sort_values(ascending=False).head(5).index
                df_top5 = df_filtrado[df_filtrado["Médico"].isin(top5_medicos)]
                evolucao_medicos = df_top5.groupby(["Ano-Mês", "Médico"])["Valor Unitário"].sum().reset_index()
                fig_ev2, ax_ev2 = plt.subplots(figsize=(12, 5))
                sns.lineplot(data=evolucao_medicos, x="Ano-Mês", y="Valor Unitário", hue="Médico", marker="o", ax=ax_ev2)
                st.pyplot(fig_ev2)

                st.subheader("💳 Evolução por Plano")
                evolucao_plano = df_filtrado.groupby(["Ano-Mês", "Categoria"])["Valor Unitário"].sum().reset_index()
                fig_ev3, ax_ev3 = plt.subplots(figsize=(12, 5))
                sns.lineplot(data=evolucao_plano, x="Ano-Mês", y="Valor Unitário", hue="Categoria", marker="o", ax=ax_ev3)
                st.pyplot(fig_ev3)

                st.subheader("🏢 Evolução por Unidade")
                evolucao_unidade = df_filtrado.groupby(["Ano-Mês", "Unidade da Clínica"])["Valor Unitário"].sum().reset_index()
                fig_ev4, ax_ev4 = plt.subplots(figsize=(12, 5))
                sns.lineplot(data=evolucao_unidade, x="Ano-Mês", y="Valor Unitário", hue="Unidade da Clínica", marker="o", ax=ax_ev4)
                st.pyplot(fig_ev4)

                st.subheader("🚨 Alerta de Variação Recente")
                ultimos_meses = evolucao_total.sort_values(by="Ano-Mês").tail(2)
                if len(ultimos_meses) == 2:
                    val_1 = ultimos_meses.iloc[0]["Valor Unitário"]
                    val_2 = ultimos_meses.iloc[1]["Valor Unitário"]
                    delta = val_2 - val_1
                    perc = (delta / val_1 * 100) if val_1 > 0 else 0
                    if perc >= 10:
                        st.success(f"📈 Crescimento de {perc:.1f}% no faturamento em relação ao mês anterior.")
                    elif perc <= -10:
                        st.error(f"📉 Queda de {abs(perc):.1f}% no faturamento em relação ao mês anterior.")
                    else:
                        st.info(f"⚖️ Estabilidade: variação de {perc:.1f}% no último mês.")

            with aba6:
                st.header("📋 Resumo Executivo por Médico")

                resumo = df_filtrado.groupby("Médico").agg({
                    "Paciente": "count",
                    "Valor Unitário": ["mean", "sum"]
                }).reset_index()
                resumo.columns = ["Médico", "Atendimentos", "Ticket Médio", "Faturamento Total"]
                resumo = resumo.sort_values(by="Faturamento Total", ascending=False)

                st.dataframe(resumo.style.format({
                    "Ticket Médio": "R$ {:,.2f}",
                    "Faturamento Total": "R$ {:,.2f}"
                }))

                st.subheader("🔁 Frequência de Pacientes")
                paciente_freq = df_filtrado["Paciente"].value_counts().reset_index()
                paciente_freq.columns = ["Paciente", "Qtd de Atendimentos"]
                top_pacientes = paciente_freq.head(10)
                st.markdown("**👥 Top 10 Pacientes Mais Frequentes**")
                st.dataframe(top_pacientes)

                media_atend_por_paciente = paciente_freq["Qtd de Atendimentos"].mean()
                st.metric("📊 Média de Atendimentos por Paciente", f"{media_atend_por_paciente:.2f}")

                atend_por_medico = df_filtrado.groupby("Médico")["Paciente"].count()
                media_por_medico = atend_por_medico.mean()
                st.metric("👨‍⚕️ Média de Atendimentos por Médico", f"{media_por_medico:.2f}")

        except Exception as e:
            st.error(f"❌ Erro ao processar o arquivo: {e}")
    else:
        st.warning("👆 Faça upload de um arquivo .csv com a estrutura correta.")
