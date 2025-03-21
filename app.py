# KPIs Estratégicos
st.subheader("📈 Indicadores Estratégicos")

# 1. Ticket médio geral
ticket_medio_geral = df_filtrado["Valor Unitário"].mean()

# 2. Ticket médio por médico
ticket_medio_medico = df_filtrado.groupby("Médico")["Valor Unitário"].mean().reset_index().sort_values(by="Valor Unitário", ascending=False)

# 3. Volume por tipo de atendimento
volume_atendimento = df_filtrado["Atendimento"].value_counts().reset_index()
volume_atendimento.columns = ["Tipo", "Quantidade"]

# 4. Pacientes únicos
pacientes_unicos = df_filtrado["Paciente"].nunique()

# 5. Receita por plano com percentual
faturamento_categoria = df_filtrado.groupby("Categoria")["Valor Unitário"].sum().reset_index()
faturamento_categoria["%"] = (faturamento_categoria["Valor Unitário"] / faturamento_total) * 100
faturamento_categoria = faturamento_categoria.sort_values(by="Valor Unitário", ascending=False)

# Mostrar KPIs
col1, col2, col3 = st.columns(3)
col1.metric("🎯 Ticket Médio Geral", f"R$ {ticket_medio_geral:,.2f}")
col2.metric("👥 Pacientes Atendidos", f"{pacientes_unicos}")
col3.metric("🧾 Total de Atendimentos", f"{len(df_filtrado):,}")

# Gráfico: Ticket Médio por Médico
st.subheader("💵 Ticket Médio por Médico")
fig_tm, ax_tm = plt.subplots(figsize=(10, 5))
sns.barplot(data=ticket_medio_medico, y="Médico", x="Valor Unitário", ax=ax_tm, palette="viridis")
ax_tm.set_xlabel("Ticket Médio (R$)")
st.pyplot(fig_tm)

# Gráfico: Volume por Tipo de Atendimento
st.subheader("📊 Volume de Atendimentos por Tipo")
fig_vol, ax_vol = plt.subplots(figsize=(6, 4))
sns.barplot(data=volume_atendimento, y="Tipo", x="Quantidade", ax=ax_vol, palette="pastel")
st.pyplot(fig_vol)

# Tabela: Receita por plano
st.subheader("📋 Receita por Categoria (Plano)")
st.dataframe(faturamento_categoria.style.format({"Valor Unitário": "R$ {:,.2f}", "%": "{:.1f}%"}))
