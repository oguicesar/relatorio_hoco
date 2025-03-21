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
            on_bad_lines="skip",  # Ignora linhas com erro
            engine="python"
        )

        # Conversão de dados
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

        # KPIs
        faturamento_total = df_filtrado["Valor Unitário"].sum()
        particular_total = df_filtrado[df_filtrado["Categoria"].str.upper() == "PARTICULAR"]["Valor Unitário"].sum()
        perc_particular = (particular_total / faturamento_total * 100) if faturamento_total > 0 else 0

        col1, col2 = st.columns(2)
        col1.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")
        col2.metric("🏥 Particular vs Convênios", f"{perc_particular:.1f}% / {100 - perc_particular:.1f}%")

        st.subheader("📊 Dados Filtrados")
        st.dataframe(df_filtrado.head(100))

        # Faturamento por Médico
        st.subheader("👨‍⚕️ Faturamento por Médico")
        fat_medico = df_filtrado.groupby("Médico")["Valor Unitário"].sum().reset_index().sort_values(by="Valor Unitário", ascending=False)
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.barplot(y="Médico", x="Valor Unitário", data=fat_medico, ax=ax1)
        ax1.set_xlabel("Faturamento (R$)")
        st.pyplot(fig1)

        # Faturamento por Plano
        st.subheader("📋 Faturamento por Categoria (Plano)")
        fat_plano = df_filtrado.groupby("Categoria")["Valor Unitário"].sum().reset_index().sort_values(by="Valor Unitário", ascending=False)
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        sns.barplot(y="Categoria", x="Valor Unitário", data=fat_plano, ax=ax2)
        ax2.set_xlabel("Faturamento (R$)")
        st.pyplot(fig2)

        # Faturamento por Tipo de Atendimento
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
