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
    # fallback
    return False

@st.cache_data(show_spinner=False)
def carregar_dados_google():
    """Lê do Google Sheets e retorna um DataFrame padronizado."""
    # Pede valores NÃO formatados para tentar receber booleanos reais
    data = sheet.get_all_records(value_render_option='UNFORMATTED_VALUE')
    if data:
        df = pd.DataFrame(data)
        # Garante colunas esperadas
        for c in COLS:
            if c not in df.columns:
                df[c] = None

        # Tipos / normalização
        df["Aprendiz"] = df["Aprendiz"].astype(str)
        df["Atividade"] = df["Atividade"].astype(str)
        df["Entregue"] = df["Entregue"].map(_to_bool)

        df = df[COLS]
        return df
    else:
        return pd.DataFrame(columns=COLS)

def salvar_dados_google(df: pd.DataFrame):
    """Sobrescreve a planilha com o DataFrame atual."""
    # Evita NaN nas colunas de texto
    df = df.copy()
    df["Aprendiz"] = df["Aprendiz"].fillna("")
    df["Atividade"] = df["Atividade"].fillna("")
    # Garante booleanos puros (True/False) antes de enviar
    df["Entregue"] = df["Entregue"].map(lambda x: True if x is True else False)

    sheet.clear()
    # IMPORTANTE: USER_ENTERED faz o Sheets interpretar como booleans
    sheet.update(
        [df.columns.tolist()] + df.values.tolist(),
        value_input_option='USER_ENTERED'
    )

def inicializa_planilha_se_vazia():
    """Se a planilha estiver vazia, cria linhas base para 1 aprendiz em branco e todas atividades."""
    df = carregar_dados_google()
    if df.empty:
        aprendizes = [""]
        df = pd.DataFrame(
            [(a, at, False) for a in aprendizes for at in ATIVIDADES_PADRAO],
            columns=COLS
        )
        salvar_dados_google(df)
        # Limpa cache e relê
        carregar_dados_google.clear()
        return carregar_dados_google()
    return df
# =======================
# Estado da sessão
# =======================
if "df" not in st.session_state:
    st.session_state.df = inicializa_planilha_se_vazia()
if "ultima_atualizacao" not in st.session_state:
    st.session_state.ultima_atualizacao = datetime.now()

# =======================
# Cabeçalho + Botão de atualização
# =======================
col_tit, col_btn = st.columns([0.8, 0.2])
with col_tit:
    st.title("📘 Plataforma de Entregas de Atividades")
with col_btn:
    if st.button("🔄 Atualizar do Google Sheets", use_container_width=True, help="Recarrega os dados diretamente da planilha"):
        # Limpa cache, recarrega e atualiza estado
        carregar_dados_google.clear()
        st.session_state.df = carregar_dados_google()
        st.session_state.ultima_atualizacao = datetime.now()
        st.success("Dados atualizados a partir do Google Sheets.")

st.caption(f"Última atualização local: {st.session_state.ultima_atualizacao.strftime('%d/%m/%Y %H:%M:%S')}")

# Trabalhamos sempre com a cópia atual
df = st.session_state.df.copy()

# =======================
# Filtros
# =======================
st.subheader("Filtros")
aprendizes_lista = sorted([a for a in df["Aprendiz"].unique() if a is not None])
atividades_lista = sorted([a for a in df["Atividade"].unique() if a is not None])

filtro_aprendiz = st.selectbox("Filtrar por Aprendiz", ["Todos"] + aprendizes_lista, index=0)
filtro_atividade = st.selectbox("Filtrar por Atividade", ["Todas"] + atividades_lista, index=0)

df_filtrado = df.copy()
if filtro_aprendiz != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Aprendiz"] == filtro_aprendiz]
if filtro_atividade != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Atividade"] == filtro_atividade]

# =======================
# Exibição da tabela
# =======================
if df_filtrado.empty:
    st.info("Nenhum registro encontrado com os filtros aplicados.")
else:
    df_display = (
        df_filtrado
        .pivot(index="Aprendiz", columns="Atividade", values="Entregue")
        .fillna(False)
        # Mostra o check somente se for exatamente True (booleano)
        .applymap(lambda x: "🟢" if x is True else "🔴")
        .sort_index(axis=0)
        .sort_index(axis=1)
    )
    st.dataframe(df_display, use_container_width=True)

# =======================
# Barra lateral - Gerenciar Aprendizes
# =======================
st.sidebar.header("Gerenciar Aprendizes")

# Adicionar
novo_aprendiz = st.sidebar.text_input("Adicionar novo aprendiz")
if st.sidebar.button("Adicionar"):
    if novo_aprendiz:
        if novo_aprendiz not in df["Aprendiz"].unique():
            atividades_existentes = df["Atividade"].unique()
            if len(atividades_existentes) == 0:
                atividades_existentes = ATIVIDADES_PADRAO
            novos_registros = pd.DataFrame(
                [(novo_aprendiz, at, False) for at in atividades_existentes],
                columns=COLS
            )
            df = pd.concat([df, novos_registros], ignore_index=True)
            salvar_dados_google(df)
            # Atualiza estado e mostra mensagem
            st.session_state.df = df
            st.sidebar.success(f"{novo_aprendiz} adicionado!")
        else:
            st.sidebar.warning("Este aprendiz já existe.")
    else:
        st.sidebar.warning("Informe um nome válido.")

# Remover
if len(aprendizes_lista) > 0:
    aprendiz_remover = st.sidebar.selectbox("Remover aprendiz", aprendizes_lista)
    if st.sidebar.button("Remover"):
        df = df[df["Aprendiz"] != aprendiz_remover]
        salvar_dados_google(df)
        st.session_state.df = df
        st.sidebar.warning(f"{aprendiz_remover} removido!")
else:
    st.sidebar.info("Não há aprendizes para remover.")

# =======================
# Barra lateral - Marcar Entregas
# =======================
st.sidebar.header("Marcar Entregas")
if len(aprendizes_lista) > 0:
    aprendiz_sel = st.sidebar.selectbox("Selecionar Aprendiz", aprendizes_lista)
    atividades_sel = df[df["Aprendiz"] == aprendiz_sel]["Atividade"].tolist()

    alterou = False
    for at in atividades_sel:
        entregue_atual = bool(df[(df["Aprendiz"] == aprendiz_sel) & (df["Atividade"] == at)]["Entregue"].values[0])
        novo_valor = st.sidebar.checkbox(at, value=entregue_atual, key=f"{aprendiz_sel}_{at}")
        if novo_valor != entregue_atual:
            df.loc[(df["Aprendiz"] == aprendiz_sel) & (df["Atividade"] == at), "Entregue"] = novo_valor
            alterou = True

    # Salva somente se houve alteração
    if alterou:
        salvar_dados_google(df)
        st.session_state.df = df
        st.sidebar.success("Entregas atualizadas!")
else:
    st.sidebar.info("Cadastre um aprendiz para marcar entregas.")
