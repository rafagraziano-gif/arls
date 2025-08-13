
import streamlit as st
import pandas as pd
import os

# Nome do arquivo onde os dados serão armazenados
DATA_FILE = "entregas.csv"

# Função para carregar os dados existentes
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Aluno", "Atividade", "Entregue"])

# Função para salvar os dados
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# Carregar dados existentes
df = load_data()

st.title("📚 Plataforma de Entregas de Atividades")

st.header("Registrar Nova Entrega")
with st.form("form_entrega"):
    aluno = st.text_input("Nome do Aluno")
    atividade = st.text_input("Nome da Atividade")
    entregue = st.checkbox("Entregue")
    submitted = st.form_submit_button("Registrar")

    if submitted and aluno and atividade:
        nova_entrega = pd.DataFrame([[aluno, atividade, entregue]], columns=["Aluno", "Atividade", "Entregue"])
        df = pd.concat([df, nova_entrega], ignore_index=True)
        save_data(df)
        st.success("Entrega registrada com sucesso!")

st.header("🔍 Visualizar Entregas")

# Filtros
alunos = ["Todos"] + sorted(df["Aluno"].unique())
atividades = ["Todos"] + sorted(df["Atividade"].unique())

filtro_aluno = st.selectbox("Filtrar por Aluno", alunos)
filtro_atividade = st.selectbox("Filtrar por Atividade", atividades)

df_filtrado = df.copy()
if filtro_aluno != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Aluno"] == filtro_aluno]
if filtro_atividade != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Atividade"] == filtro_atividade]

st.dataframe(df_filtrado.reset_index(drop=True))
