# 📊 Dashboard de Faturamento - HOCO

Este é um projeto desenvolvido em **Streamlit** para visualização automática dos dados de faturamento do Hospital de Olhos do Centro-Oeste (HOCO), com foco em:

- Faturamento por médico
- Faturamento por convênio
- Distribuição percentual entre particular e convênios
- Métricas chave (KPI) do negócio

---

## 🚀 Acesse o dashboard online:

🔗 [https://seu-usuario-relatorio-hoco.streamlit.app/](https://seu-usuario-relatorio-hoco.streamlit.app/)

---

## 📂 Como usar

1. Faça upload de um arquivo `.csv` com os dados.
2. As colunas obrigatórias são:
   - `Médico`
   - `Convênio`
   - `Faturamento`
3. O dashboard mostrará:
   - Tabela com os dados brutos
   - Gráficos de barras
   - Métricas de negócio

---

## 💻 Tecnologias utilizadas

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Seaborn](https://seaborn.pydata.org/)

---

## 📁 Exemplo de estrutura da base de dados

| Médico   | Convênio     | Faturamento |
|----------|--------------|-------------|
| Dr. Z    | PARTICULAR   | 1500        |
| Dr. Y    | UNIMED       | 1230        |
| Dr. X    | BRADESCO     | 890         |

---

## 🧠 Observações

Este projeto é apenas um modelo visual. A base de dados deve ser exportada mensalmente do sistema original no formato `.csv`.

---
