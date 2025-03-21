import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Dashboard HOCO", layout="wide")
st.title("📊 Dashboard de Faturamento - HOCO")

st.markdown("""
Este dashboard permite analisar o faturamento mensal do HOCO com base em uma planilha **.csv** exportada do sistema.

➡️ Faça o upload da planilha contendo as seguintes colunas obrigatórias:

- `Médico`
- `Plano`
- `valor`

**Formato esperado do arquivo:**

| Médico              | Plano      | valor |
|--------------------|------------|-------|
| Dr. Alencar Gomes  | PARTICULAR | 1500  |
| Dr. José Roberto   | UNIMED     | 900   |
""")

uploaded_file = st.file_uploader("📂 Faça upload do arquivo .csv", type=["csv"])

if uploaded_file:
    try:
        # Lê o CSV com encoding padrão brasileiro e separador ;
        df = pd.read_csv(uploaded_file, encoding='latin1', sep=';')

        # Verifica colunas obrigatórias
        colunas_esperadas = {"Médico", "Plano", "valor"}
        if not colunas_esperadas.issubset(set(df.columns)):
            st.error(f"❌ As colunas obrigatórias são: {', '.join(colunas_esperadas)}")
        else:
            # Garantir que 'valor' seja numérico
            df["valor"] = pd.to_numeric(df["valor"], errors='coerce')
            df.dropna(subset=["valor"], inplace=True)

            st.subheader("🔍 Dados Carregados")
            st.dataframe(df)

            faturamento_medico = df.groupby("Médico")["valor"].sum().reset_index().sort_values(by="valor", ascending=False)
            faturamento_plano = df.groupby("Plano")["valor"].sum().reset_index().sort_values(by="valor", ascending=False)

            total_faturamento = df["valor"].sum()
            particular = faturamento_plano[faturamento_plano["Plano"].str.upper() == "PARTICULAR"]["valor"].sum()
            percentual_particular = (particular / total_faturamento) * 100
            percentual_convenio = 100 - percentual_particular

            col1, col2 = st.columns(2)
            col1.metric("💰 Faturamento Total", f"R$ {total_faturamento:,.2f}")
            col2.metric("🏥 Particular vs Convênios", f"{percentual_particular:.2f}% | {percentual_convenio:.2f}%")

            st.subheader("👨‍⚕️ Faturamento por Médico")
            fig1, ax1 = plt.subplots(figsize=(10, 5))
            sns.barplot(y=faturamento_medico["Médico"], x=faturamento_medico["valor"], palette="Blues_r")
            ax1.set_xlabel("Faturamento (R$)")
            st.pyplot(fig1)

            st.subheader("📋 Faturamento por Plano")
            fig2, ax2 = plt.subplots(figsize=(10, 5))
            sns.barplot(y=faturamento_plano["Plano"], x=faturamento_plano["valor"], palette="Reds_r")
            ax2.set_xlabel("Faturamento (R$)")
            st.pyplot(fig2)

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo: {e}")
else:
    st.warning("👆 Faça upload de um arquivo .csv com colunas: Médico, Plano, valor")
