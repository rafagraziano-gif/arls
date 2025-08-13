import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

st.set_page_config(page_title="Plataforma de Entregas", page_icon="📘", layout="wide")

# =======================
# Configuração do Google Sheets
# =======================
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

SHEET_ID = "1YnLFqXtLq95nV2gT6AU_5WTdfkk88cbWyL8e_duj0_Y"
sheet = client.open_by_key(SHEET_ID).sheet1

COLS = ["Aprendiz", "Atividade", "Entregue"]
ATIVIDADES_PADRAO = [
    "Minha Iniciação", "1ª Instrução", "2ª Instrução", "3ª Instrução", "4ª Instrução",
    "5ª Instrução", "6ª Instrução", "7ª Instrução", "O Livro da Lei", "A Coluna Booz",
    "O Templo de Salomão", "A Pedra Bruta", "O Avental de Aprendiz", "O Bode na Maçonaria",
    "A Cadeia de União", "Questionário de Aprendiz"
]

# =======================
# Funções utilitárias
# =======================

def _to_bool(v):
    """Converte qualquer coisa para bool de forma segura e previsível."""
    if isinstance(v, bool):
        return v
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return False
    if isinstance(v, (int, float)):
        return v != 0
    if isinstance(v, str):
        s = v.strip().lower()
        if s in ("true", "1", "yes", "y", "sim", "verdadeiro"):
            return True
        if s in ("false", "0", "no", "n", "não", "nao", "falso", ""):
            return False
    return False

@st.cache_data(show_spinner=False)
def carregar_dados_google():
    """Lê do Google Sheets e retorna um DataFrame padronizado."""
    data = sheet.get_all_records(value_render_option='UNFORMATTED_VALUE')
    if data:
        df = pd.DataFrame(data)
        for c in COLS:
            if c not in df.columns:
                df[c] = None

        df["Aprendiz"] = df["Aprendiz"].astype(str)
        df["Atividade"] = df["Atividade"].astype(str)
        df["Entregue"] = df["Entregue"].map(_to_bool)

        return df[COLS]
    return pd.DataFrame(columns=COLS)

def salvar_dados_google(df: pd.DataFrame):
    """Sobrescreve a planilha com o DataFrame atual."""
    df = df.copy()
    df["Aprendiz"] = df["Aprendiz"].fillna("")
    df["Atividade"] = df["Atividade"].fillna("")
    df["Entregue"] = df["Entregue"].map(lambda x: True if x is True else False)

    sheet.clear()
    sheet.update
