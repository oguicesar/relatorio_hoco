# 📊 Dashboard HOCO - Faturamento Hospital de Olhos do Centro-Oeste

Este projeto é um **dashboard interativo em Streamlit** desenvolvido para analisar mensalmente os dados de faturamento do HOCO, a partir de uma planilha `.csv` exportada do sistema.

O objetivo é facilitar a visualização de dados financeiros, operacionais e clínicos, com filtros dinâmicos e KPIs relevantes.

---

## 🚀 Acesse o dashboard online:

👉 [https://seu-usuario-relatorio-hoco.streamlit.app](https://seu-usuario-relatorio-hoco.streamlit.app)

> *Substitua `seu-usuario` pelo seu nome de usuário do GitHub.*

---

## 📂 Estrutura esperada do arquivo `.csv`

O arquivo deve conter colunas como:

Nome da Origem, Núm, Paciente, Categoria, Médico, Guia, Atendimento, Procedimento_validado, valor, Tipo_procedimento, Mês, Ano, Qtde_com_Facectomia, Clinica, Data, Dia_semana_nr, Plano


- Separador: `;`
- Encoding: `Latin1` (padrão Excel no Brasil)

---

## 🧰 Funcionalidades do Dashboard

- ✅ Faturamento total filtrado
- ✅ Comparativo Particular vs Convênios
- ✅ Faturamento por Médico (ranking)
- ✅ Faturamento por Plano
- ✅ Filtros interativos:
  - Mês
  - Ano
  - Tipo de Procedimento
  - Clínica
  - Plano

---

## 🖥️ Como usar

1. Acesse o link do app online
2. Faça upload do `.csv` extraído do sistema
3. Use os filtros no menu lateral para visualizar os dados
4. Veja gráficos e indicadores automaticamente atualizados

---

## 🧪 Tecnologias utilizadas

- [Streamlit](https://streamlit.io/)
- [Pandas](https://pandas.pydata.org/)
- [Matplotlib](https://matplotlib.org/)
- [Seaborn](https://seaborn.pydata.org/)
- Python 3.10+

---

## 💡 Exemplo de uso

Você pode testar o dashboard com o arquivo de exemplo abaixo:

📥 **[Download base exemplo](https://github.com/seu-usuario/relatorio-hoco/raw/main/exemplo_arquivo_completo.csv)**

---

## 👨‍🔧 Manutenção

Caso a estrutura do `.csv` seja alterada no futuro, basta atualizar o `app.py` para reconhecer os novos campos.

Para mais ajuda ou melhorias, abra uma issue ou contribua com um pull request. 😉

---

## 🧑‍💼 Desenvolvido por

Guilherme (com suporte do ChatGPT e Streamlit ❤️)
