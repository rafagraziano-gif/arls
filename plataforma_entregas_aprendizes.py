import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ============================
# CONFIGURAÇÃO GOOGLE SHEETS
# ============================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

# ID da planilha (copie da URL do Google Sheets)
SHEET_ID = "SEU_ID_DA_PLANILHA"
sheet = client.open_by_key(SHEET_ID).sheet1

# ============================
# FUNÇÕES PARA CARREGAR E SALVAR
# ============================
def carregar_dados():
    data = sheet.get_all_records()
    if data:
        return pd.DataFrame(data)
    else:
        return pd.DataFrame(columns=["Aprendiz", "Atividade", "Entregue"])

def salvar_dados(df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# ============================
# CARREGAR DADOS INICIAIS
# ============================
df = carregar_dados()

# Se não houver dados, inicializa com exemplo
if df.empty:
    aprendizes = ["Aprendiz 1", "Aprendiz 2"]
    atividades = ["Minha Iniciação", "1ª Instrução"]
    df = pd.DataFrame([(a, at, False) for a in aprendizes for at in atividades], columns=["Aprendiz", "Atividade", "Entregue"])
    salvar_dados(df)

# ============================
# INTERFACE PRINCIPAL
# ============================
st.title("📘 Plataforma de Entregas de Atividades")

# Filtros
st.subheader("Filtros")
filtro_aprendiz = st.selectbox("Filtrar por Aprendiz", ["Todos"] + sorted(df["Aprendiz"].unique()))
filtro_atividade = st.selectbox("Filtrar por Atividade", ["Todas"] + sorted(df["Atividade"].unique()))

# Botão para limpar filtros
if st.button("Remover Filtros"):
    filtro_aprendiz = "Todos"
    filtro_atividade = "Todas"

# Aplica filtros
df_filtrado = df.copy()
if filtro_aprendiz != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Aprendiz"] == filtro_aprendiz]
if filtro_atividade != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Atividade"] == filtro_atividade]

# Exibe tabela pivotada
df_display = df_filtrado.pivot(index="Aprendiz", columns="Atividade", values="Entregue").fillna(False)
df_display = df_display.applymap(lambda x: "✔️" if x else "")
st.write("### Tabela de Entregas")
st.dataframe(df_display)

# ============================
# MARCAR ENTREGAS NA SIDEBAR
# ============================
st.sidebar.header("Marcar Entregas")
aprendiz_sel = st.sidebar.selectbox("Selecionar Aprendiz", sorted(df["Aprendiz"].unique()))
atividades_sel = df[df["Aprendiz"] == aprendiz_sel]["Atividade"].tolist()

for at in atividades_sel:
    entregue = st.sidebar.checkbox(at, value=bool(df[(df["Aprendiz"] == aprendiz_sel) & (df["Atividade"] == at)]["Entregue"].values[0]))
    df.loc[(df["Aprendiz"] == aprendiz_sel) & (df["Atividade"] == at), "Entregue"] = entregue

# ============================
# BOTÃO PARA SALVAR NO GOOGLE SHEETS
# ============================
if st.button("Salvar Alterações"):
    salvar_dados(df)
    st.success("✅ Dados salvos no Google Sheets com sucesso!")
