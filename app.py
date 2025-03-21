import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard HOCO", layout="wide")
st.title("📊 Dashboard de Faturamento - Simulação")

st.markdown("""
Faça o upload do arquivo `.csv` com as seguintes colunas:

- Número
- Paciente
- Categoria (Plano)
- Médico
- Atendimento (Consulta, Exame ou Procedimento)
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

        # Sidebar - Filtros
        st.sidebar.header("🎯 Filtros")
        anos = st.sidebar.multiselect("Ano", sorted(df["Ano"].unique()), default=sorted(df["Ano"].unique()))
        meses = st.sidebar.multiselect("Mês", sorted(df["Mês"].unique()), default=sorted(df["Mês"].unique()))
        medicos = st.sidebar.multiselect("Médico", df["Médico"].unique(), default=df["Médico"].unique())
        unidades = st.sidebar.multiselect("Unidade da Clínica", df["Unidade da Clínica"].unique(), default=df["Unidade da Clínica"].unique())
        atendimentos = st.sidebar.multiselect("Atendimento", df["Atendimento"].unique(), default=df["Atendimento"].unique())
        planos = st.sidebar.multiselect("Categoria", df["Categoria"].unique(), default=df["Categoria"].unique())

        # Aplicar filtros
        df_filtrado = df[
            (df["Ano"].isin(anos)) &
            (df["Mês"].isin(meses)) &
            (df["Médico"].isin(medicos)) &
            (df["Unidade da Clínica"].isin(unidades)) &
            (df["Atendimento"].isin(atendimentos)) &
            (df["Categoria"].isin(planos))
        ]

        faturamento_total = df_filtrado["Valor Unitário"].sum()
        particular_total = df_filtrado[df_filtrado["Categoria"].str.upper() == "PARTICULAR"]["Valor Unitário"].sum()
        perc_particular = (particular_total / faturamento_total * 100) if faturamento_total > 0 else 0

        st.subheader("📊 Dados Filtrados")
        st.dataframe(df_filtrado.head(100))

        # ====== KPIs Estratégicos ======
        st.subheader("📈 Indicadores Estratégicos")

        ticket_medio_geral = df_filtrado["Valor Unitário"].mean()
        pacientes_unicos = df_filtrado["Paciente"].nunique()
        total_atendimentos = len(df_filtrado)

        ticket_medio_medico = df_filtrado.groupby("Médico")["Valor Unitário"].mean().reset_index().sort_values(by="Valor Unitário", ascending=False)
        volume_atendimento = df_filtrado["Atendimento"].value_counts().reset_index()
        volume_atendimento.columns = ["Tipo", "Quantidade"]

        faturamento_categoria = df_filtrado.groupby("Categoria")["Valor Unitário"].sum().reset_index()
        faturamento_categoria["%"] = (faturamento_categoria["Valor Unitário"] / faturamento_total) * 100
        faturamento_categoria = faturamento_categoria.sort_values(by="Valor Unitário", ascending=False)

        col1, col2, col3 = st.columns(3)
        col1.metric("🎯 Ticket Médio Geral", f"R$ {ticket_medio_geral:,.2f}")
        col2.metric("👥 Pacientes Atendidos", f"{pacientes_unicos}")
        col3.metric("🧾 Total de Atendimentos", f"{total_atendimentos:,}")

        # ====== Gráficos ======

        # Ticket médio por médico
        st.subheader("💵 Ticket Médio por Médico")
        fig_tm, ax_tm = plt.subplots(figsize=(10, 5))
        sns.barplot(data=ticket_medio_medico, y="Médico", x="Valor Unitário", ax=ax_tm, palette="viridis")
        ax_tm.set_xlabel("Ticket Médio (R$)")
        st.pyplot(fig_tm)

        # Volume por tipo de atendimento
        st.subheader("📊 Volume de Atendimentos por Tipo")
        fig_vol, ax_vol = plt.subplots(figsize=(6, 4))
        sns.barplot(data=volume_atendimento, y="Tipo", x="Quantidade", ax=ax_vol, palette="pastel")
        st.pyplot(fig_vol)

        # Receita por plano
        st.subheader("📋 Receita por Categoria (Plano)")
        st.dataframe(faturamento_categoria.style.format({"Valor Unitário": "R$ {:,.2f}", "%": "{:.1f}%"}))

        # Receita por médico
        st.subheader("👨‍⚕️ Faturamento por Médico")
        fat_medico = df_filtrado.groupby("Médico")["Valor Unitário"].sum().reset_index().sort_values(by="Valor Unitário", ascending=False)
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.barplot(y="Médico", x="Valor Unitário", data=fat_medico, ax=ax1)
        ax1.set_xlabel("Faturamento (R$)")
        st.pyplot(fig1)

        # Receita por plano gráfico
        st.subheader("📋 Faturamento por Categoria (Gráfico)")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.barplot(y="Categoria", x="Valor Unitário", data=faturamento_categoria, ax=ax2)
        ax2.set_xlabel("Faturamento (R$)")
        st.pyplot(fig2)

        # Faturamento por tipo de atendimento
        st.subheader("🩺 Faturamento por Tipo de Atendimento")
        fat_atendimento = df_filtrado.groupby("Atendimento")["Valor Unitário"].sum().reset_index().sort_values(by="Valor Unitário", ascending=False)
        fig3, ax3 = plt.subplots(figsize=(10, 5))
        sns.barplot(y="Atendimento", x="Valor Unitário", data=fat_atendimento, ax=ax3)
        ax3.set_xlabel("Faturamento (R$)")
        st.pyplot(fig3)

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.warning("👆 Faça upload de um arquivo .csv gerado com as colunas indicadas.")
