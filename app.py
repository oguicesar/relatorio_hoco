import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import unicodedata

st.set_page_config(page_title="Dashboard HOCO", layout="wide")
st.title("📊 Dashboard de Faturamento - HOCO")

st.markdown("""
Faça o upload da base de dados **.csv** gerada pelo sistema do HOCO.

- O dashboard irá carregar automaticamente os dados
- Você poderá filtrar por **ano**, **mês**, **procedimento**, **clínica**, **médico** ou **plano**
""")

uploaded_file = st.file_uploader("📂 Upload do arquivo CSV", type=["csv"])

if uploaded_file:
    try:
        # Lê o arquivo corrigindo possíveis problemas de encoding e delimitador
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=None, engine='python')

        # Normalizar nomes das colunas
        def normalizar_coluna(col):
            col = unicodedata.normalize("NFKD", col).encode("ascii", "ignore").decode("utf-8")
            return col.strip().lower().replace(" ", "_")

        df.columns = [normalizar_coluna(c) for c in df.columns]

        # Verifica se colunas essenciais estão presentes
        colunas_obrigatorias = {"medico", "plano", "valor", "tipo_procedimento", "mes", "ano", "clinica"}
        if not colunas_obrigatorias.issubset(set(df.columns)):
            st.error(f"❌ Colunas obrigatórias ausentes: {colunas_obrigatorias - set(df.columns)}")
        else:
            df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
            df.dropna(subset=["valor"], inplace=True)

            # Filtros dinâmicos
            st.sidebar.header("🎯 Filtros")

            ano = st.sidebar.multiselect("Ano", sorted(df["ano"].dropna().unique()), default=sorted(df["ano"].dropna().unique()))
            mes = st.sidebar.multiselect("Mês", sorted(df["mes"].dropna().unique()), default=sorted(df["mes"].dropna().unique()))
            clinica = st.sidebar.multiselect("Clínica", df["clinica"].dropna().unique(), default=df["clinica"].dropna().unique())
            procedimento = st.sidebar.multiselect("Tipo de Procedimento", df["tipo_procedimento"].dropna().unique(), default=df["tipo_procedimento"].dropna().unique())
            plano = st.sidebar.multiselect("Plano", df["plano"].dropna().unique(), default=df["plano"].dropna().unique())

            df_filtros = df[
                df["ano"].isin(ano) &
                df["mes"].isin(mes) &
                df["clinica"].isin(clinica) &
                df["tipo_procedimento"].isin(procedimento) &
                df["plano"].isin(plano)
            ]

            st.subheader("📊 Dados Filtrados")
            st.dataframe(df_filtros)

            faturamento_total = df_filtros["valor"].sum()
            faturamento_medico = df_filtros.groupby("medico")["valor"].sum().reset_index().sort_values(by="valor", ascending=False)
            faturamento_plano = df_filtros.groupby("plano")["valor"].sum().reset_index().sort_values(by="valor", ascending=False)

            particular = faturamento_plano[faturamento_plano["plano"].str.upper() == "PARTICULAR"]["valor"].sum()
            perc_particular = (particular / faturamento_total) * 100 if faturamento_total > 0 else 0
            perc_convenio = 100 - perc_particular

            col1, col2 = st.columns(2)
            col1.metric("💰 Faturamento Total", f"R$ {faturamento_total:,.2f}")
            col2.metric("🏥 Particular vs Convênios", f"{perc_particular:.1f}% | {perc_convenio:.1f}%")

            # Gráfico por médico
            st.subheader("👨‍⚕️ Faturamento por Médico")
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            sns.barplot(y="medico", x="valor", data=faturamento_medico, ax=ax1)
            ax1.set_xlabel("Faturamento (R$)")
            st.pyplot(fig1)

            # Gráfico por plano
            st.subheader("📋 Faturamento por Plano")
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            sns.barplot(y="plano", x="valor", data=faturamento_plano, ax=ax2)
            ax2.set_xlabel("Faturamento (R$)")
            st.pyplot(fig2)

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.warning("👆 Faça upload de um arquivo .csv extraído do sistema HOCO.")
