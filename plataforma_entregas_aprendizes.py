import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuração do Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

SHEET_ID = "1YnLFqXtLq95nV2gT6AU_5WTdfkk88cbWyL8e_duj0_Y"
sheet = client.open_by_key(SHEET_ID).sheet1

# Funções para carregar e salvar dados
def carregar_dados():
    data = sheet.get_all_records()
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=["Aprendiz", "Atividade", "Entregue"])

def salvar_dados(df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# Carregar dados iniciais
df = carregar_dados()

# Se não houver dados, inicializa com exemplo
if df.empty:
    aprendizes = ["Aprendiz 1", "Aprendiz 2"]
    atividades = ["Minha Iniciação", "1ª Instrução"]
    df = pd.DataFrame([(a, at, False) for a in aprendizes for at in atividades], columns=["Aprendiz", "Atividade", "Entregue"])
    salvar_dados(df)

# Título
st.title("📘 Plataforma de Entregas de Atividades")

# Filtros
st.subheader("Filtros")
filtro_aprendiz = st.selectbox("Filtrar por Aprendiz", ["Todos"] + sorted(df["Aprendiz"].unique()))
filtro_atividade = st.selectbox("Filtrar por Atividade", ["Todas"] + sorted(df["Atividade"].unique()))

# Aplica filtros
df_filtrado = df.copy()
if filtro_aprendiz != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Aprendiz"] == filtro_aprendiz]
if filtro_atividade != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Atividade"] == filtro_atividade]

# Exibe tabela
df_display = df_filtrado.pivot(index="Aprendiz", columns="Atividade", values="Entregue").fillna(False)
df_display = df_display.applymap(lambda x: "✔️" if x else "")
st.dataframe(df_display)

# Barra lateral - Gerenciar aprendizes
st.sidebar.header("Gerenciar Aprendizes")
novo_aprendiz = st.sidebar.text_input("Adicionar novo aprendiz")
if st.sidebar.button("Adicionar"):
    if novo_aprendiz and novo_aprendiz not in df["Aprendiz"].unique():
        atividades_existentes = df["Atividade"].unique()
        novos_registros = pd.DataFrame([(novo_aprendiz, at, False) for at in atividades_existentes], columns=["Aprendiz", "Atividade", "Entregue"])
        df = pd.concat([df, novos_registros], ignore_index=True)
        salvar_dados(df)
        st.sidebar.success(f"{novo_aprendiz} adicionado!")

aprendiz_remover = st.sidebar.selectbox("Remover aprendiz", sorted(df["Aprendiz"].unique()))
if st.sidebar.button("Remover"):
    df = df[df["Aprendiz"] != aprendiz_remover]
    salvar_dados(df)
    st.sidebar.warning(f"{aprendiz_remover} removido!")

# Barra lateral - Marcar entregas
st.sidebar.header("Marcar Entregas")
aprendiz_sel = st.sidebar.selectbox("Selecionar Aprendiz", sorted(df["Aprendiz"].unique()))
atividades_sel = df[df["Aprendiz"] == aprendiz_sel]["Atividade"].tolist()

for at in atividades_sel:
    entregue = bool(df[(df["Aprendiz"] == aprendiz_sel) & (df["Atividade"] == at)]["Entregue"].values[0])
    novo_valor = st.sidebar.checkbox(at, value=entregue, key=f"{aprendiz_sel}_{at}")
    if novo_valor != entregue:
        df.loc[(df["Aprendiz"] == aprendiz_sel) & (df["Atividade"] == at), "Entregue"] = novo_valor
        salvar_dados(df)
