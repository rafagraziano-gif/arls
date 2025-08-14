import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
import re
import string

st.set_page_config(page_title="Controle de Entrega de Trabalhos - APRENDIZES", page_icon="📘", layout="wide")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcp_service_account"], scope)
client = gspread.authorize(creds)

SHEET_ID = "1YnLFqXtLq95nV2gT6AU_5WTdfkk88cbWyL8e_duj0_Y"
sheet = client.open_by_key(SHEET_ID).sheet1

COLS = ["Aprendiz", "Atividade", "Entregue", "Data Iniciação"]

ATIVIDADES_PADRAO = [
    "Minha Iniciação", "1ª Instrução", "2ª Instrução", "3ª Instrução", "4ª Instrução",
    "5ª Instrução", "6ª Instrução", "7ª Instrução", "O Livro da Lei", "A Coluna Booz",
    "O Templo de Salomão", "A Pedra Bruta", "O Avental de Aprendiz", "O Bode na Maçonaria",
    "A Cadeia de União", "Questionário de Aprendiz"
]

def _to_bool(v):
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

def uppercase_nome(nome: str) -> str:
    """Converte para letras maiúsculas, removendo espaços extras."""
    if not isinstance(nome, str):
        return ""
    return nome.strip().upper()

RE_DDMMYYYY = re.compile(r"^\s*(\d{2})/(\d{2})/(\d{4})\s*$")

def parse_ddmmyyyy(s: str):
    if not isinstance(s, str):
        return None
    m = RE_DDMMYYYY.match(s)
    if not m:
        return None
    try:
        d, mth, y = map(int, m.groups())
        return date(y, mth, d)
    except ValueError:
        return None

def format_ddmmyyyy(d: date) -> str:
    if pd.isna(d) or d is None:
        return ""
    return d.strftime("%d/%m/%Y")

def anos_meses_desde(d: date, hoje: date = None) -> str:
    if d is None or pd.isna(d):
        return "—"
    if hoje is None:
        hoje = date.today()
    if d > hoje:
        return "—"
    months = (hoje.year - d.year) * 12 + (hoje.month - d.month)
    if hoje.day < d.day:
        months -= 1
    anos = months // 12
    meses = months % 12
    a_txt = f"{anos} ano" if anos == 1 else f"{anos} anos"
    m_txt = f"{meses} mês" if meses == 1 else f"{meses} meses"
    return f"{a_txt} e {m_txt}"

def coerce_to_date_from_gs(v):
    if v is None or (isinstance(v, float) and pd.isna(v)) or (isinstance(v, str) and v.strip() == ""):
        return None
    if isinstance(v, (int, float)):
        base = pd.to_datetime("1899-12-30")
        dt = base + pd.to_timedelta(int(v), unit="D")
        return dt.date()
    if isinstance(v, str):
        d = parse_ddmmyyyy(v)
        if d:
            return d
        try:
            return pd.to_datetime(v, dayfirst=True).date()
        except Exception:
            return None
    return None

@st.cache_data(show_spinner=False)
def carregar_dados_google():
    data = sheet.get_all_records(value_render_option='UNFORMATTED_VALUE')
    if data:
        df = pd.DataFrame(data)
        for c in COLS:
            if c not in df.columns:
                df[c] = None
        df["Aprendiz"] = df["Aprendiz"].astype(str)
        df["Atividade"] = df["Atividade"].astype(str)
        df["Entregue"] = df["Entregue"].map(_to_bool)
        df["Data Iniciação"] = df["Data Iniciação"].apply(coerce_to_date_from_gs)
        return df[COLS]
    return pd.DataFrame(columns=COLS)

def salvar_dados_google(df: pd.DataFrame):
    df = df.copy()
    df["Aprendiz"] = df["Aprendiz"].fillna("")
    df["Atividade"] = df["Atividade"].fillna("")
    df["Entregue"] = df["Entregue"].map(lambda x: True if x is True else False)
    df["Data Iniciação"] = df["Data Iniciação"].apply(lambda d: format_ddmmyyyy(d) if isinstance(d, (date, datetime)) else (d if isinstance(d, str) else ""))
    sheet.clear()
    sheet.update(
        [df.columns.tolist()] + df.values.tolist(),
        value_input_option='USER_ENTERED'
    )

def inicializa_planilha_se_vazia():
    df = carregar_dados_google()
    if df.empty:
        aprendizes = [""]
        df = pd.DataFrame(
            [(a, at, False, None) for a in aprendizes for at in ATIVIDADES_PADRAO],
            columns=COLS
        )
        salvar_dados_google(df)
        carregar_dados_google.clear()
        return carregar_dados_google()
    return df

if "df" not in st.session_state:
    st.session_state.df = inicializa_planilha_se_vazia()
if "ultima_atualizacao" not in st.session_state:
    st.session_state.ultima_atualizacao = datetime.now()
# inicializa a variável de estado para o botão da lista de atividades
if "show_lista_atividades" not in st.session_state:
    st.session_state.show_lista_atividades = False

col_tit, col_btn = st.columns([0.8, 0.2])
with col_tit:
    st.title("📘 Controle de Entrega de Trabalhos - APRENDIZES - A.R.L.S. Tropeiros de Sorocaba nº824")
with col_btn:
    if st.button("🔄 Atualizar do Google Sheets", use_container_width=True, help="Recarrega os dados diretamente da planilha"):
        carregar_dados_google.clear()
        st.session_state.df = carregar_dados_google()
        st.session_state.ultima_atualizacao = datetime.now()
        st.success("Dados atualizados a partir do Google Sheets.")

st.caption(f"Última atualização local: {st.session_state.ultima_atualizacao.strftime('%d/%m/%Y %H:%M:%S')}")

df = st.session_state.df.copy()

# Botão para gerar lista de atividades
def gerar_lista_atividades():
    """Gera a lista de atividades padrão."""
    lista = "\n- ".join(ATIVIDADES_PADRAO)
    return f"Lista de Atividades:\n\n- {lista}"

# usa o estado de sessão para controlar a exibição
if st.button("📋 Gerar Lista de Atividades"):
    st.session_state.show_lista_atividades = not st.session_state.show_lista_atividades
    st.session_state.lista_atividades_texto = gerar_lista_atividades()

if st.session_state.show_lista_atividades and "lista_atividades_texto" in st.session_state:
    st.text_area("Lista de Atividades (copie o texto abaixo)", value=st.session_state.lista_atividades_texto, height=250)


st.divider()

st.subheader("Filtros")
aprendizes_lista = sorted([a for a in df["Aprendiz"].unique() if a is not None])
atividades_unicas = list(dict.fromkeys(df["Atividade"].dropna().tolist()))
atividades_ordenadas = [a for a in ATIVIDADES_PADRAO if a in atividades_unicas] + [a for a in atividades_unicas if a not in ATIVIDADES_PADRAO]

filtro_aprendiz = st.selectbox("Filtrar por Aprendiz", ["Todos"] + aprendizes_lista, index=0)
filtro_atividade = st.selectbox("Filtrar por Atividade", ["Todas"] + atividades_ordenadas, index=0)

df_filtrado = df.copy()
if filtro_aprendiz != "Todos":
    df_filtrado = df_filtrado[df_filtrado["Aprendiz"] == filtro_aprendiz]
if filtro_atividade != "Todas":
    df_filtrado = df_filtrado[df_filtrado["Atividade"] == filtro_atividade]

if df_filtrado.empty:
    st.info("Nenhum registro encontrado com os filtros aplicados.")
else:
    atividades_unicas_filtrado = list(dict.fromkeys(df_filtrado["Atividade"].dropna().tolist()))
    atividades_ordenadas_filtrado = [a for a in ATIVIDADES_PADRAO if a in atividades_unicas_filtrado] + [a for a in atividades_unicas_filtrado if a not in ATIVIDADES_PADRAO]

    df_ord = df_filtrado.copy()
    df_ord["Atividade"] = pd.Categorical(df_ord["Atividade"], categories=atividades_ordenadas_filtrado, ordered=True)

    df_display = (
        df_ord
        .pivot(index="Aprendiz", columns="Atividade", values="Entregue")
        .reindex(columns=atividades_ordenadas_filtrado)
        .fillna(False)
        .sort_index(axis=0)
        .applymap(lambda x: "🟢" if x is True else "🔴")
    )

    datas_por_aprendiz = (
        df_ord[['Aprendiz', 'Data Iniciação']]
        .drop_duplicates()
        .sort_values('Data Iniciação')
        .groupby('Aprendiz', as_index=True)['Data Iniciação']
        .apply(lambda s: next((d for d in s if d is not None), None))
    )

    data_fmt = datas_por_aprendiz.apply(lambda d: format_ddmmyyyy(d) if d else "—")
    tempo_fmt = datas_por_aprendiz.apply(lambda d: anos_meses_desde(d))

    df_display.insert(0, "Tempo desde Iniciação", tempo_fmt.reindex(df_display.index).fillna("—"))
    df_display.insert(0, "Data de Iniciação", data_fmt.reindex(df_display.index).fillna("—"))

    def destacar_linha_completa(valores):
        if all(v == "🟢" for v in valores if v in ("🟢", "🔴")):
            return ["background-color: lightgreen; font-weight: bold"] * len(valores)
        return ["font-weight: bold"] * len(valores)

    styled_df = df_display.style.apply(destacar_linha_completa, axis=1)
    
    st.dataframe(styled_df, use_container_width=True)

st.divider()

st.sidebar.header("Gerenciar Aprendizes")

def _normalizar_input_novo_aprendiz():
    valor = st.session_state.get("novo_aprendiz_input", "")
    st.session_state["novo_aprendiz_input"] = uppercase_nome(valor)

novo_aprendiz = st.sidebar.text_input(
    "Adicionar novo aprendiz",
    key="novo_aprendiz_input",
    on_change=_normalizar_input_novo_aprendiz
)

novo_aprendiz_data_str = st.sidebar.text_input(
    "Data de iniciação (dd/mm/aaaa)",
    placeholder="dd/mm/aaaa",
    key="novo_aprendiz_data_input",
    help="Digite no formato dd/mm/aaaa. Ex.: 05/03/2024"
)

if st.sidebar.button("Adicionar", key="botao_adicionar_aprendiz"):
    novo_aprendiz_norm = uppercase_nome(st.session_state.get("novo_aprendiz_input", ""))
    data_ok = parse_ddmmyyyy(st.session_state.get("novo_aprendiz_data_input", ""))

    if not novo_aprendiz_norm:
        st.sidebar.warning("Informe um nome válido.")
    elif not data_ok:
        st.sidebar.warning("Informe uma data de iniciação válida no formato dd/mm/aaaa.")
    elif data_ok > date.today():
        st.sidebar.warning("A data de iniciação não pode ser futura.")
    else:
        nomes_existentes_norm = pd.Series(df["Aprendiz"].fillna("")).apply(uppercase_nome)
        if novo_aprendiz_norm in nomes_existentes_norm.values:
            st.sidebar.warning("Este aprendiz já existe.")
        else:
            atividades_unicas_all = list(dict.fromkeys(df["Atividade"].dropna().tolist()))
            atividades_existentes = [a for a in ATIVIDADES_PADRAO if a in atividades_unicas_all] + [a for a in atividades_unicas_all if a not in ATIVIDADES_PADRAO]
            if len(atividades_existentes) == 0:
                atividades_existentes = ATIVIDADES_PADRAO

            novos_registros = pd.DataFrame(
                [(novo_aprendiz_norm, at, False, data_ok) for at in atividades_existentes],
                columns=COLS
            )

            df = pd.concat([df, novos_registros], ignore_index=True)
            salvar_dados_google(df)
            st.session_state.df = df
            st.sidebar.success(f"{novo_aprendiz_norm} adicionado com iniciação em {format_ddmmyyyy(data_ok)}!")

if len(aprendizes_lista) > 0:
    aprendiz_remover = st.sidebar.selectbox("Remover aprendiz", aprendizes_lista)
    if st.sidebar.button("Remover"):
        df = df[df["Aprendiz"] != aprendiz_remover]
        salvar_dados_google(df)
        st.session_state.df = df
        st.sidebar.warning(f"{aprendiz_remover} removido!")
else:
    st.sidebar.info("Não há aprendizes para remover.")

st.sidebar.header("Marcar Entregas")
if len(aprendizes_lista) > 0:
    # adiciona um callback para limpar o extrato quando o aprendiz muda
    aprendiz_sel_old = st.session_state.get('aprendiz_sel_old', None)
    
    def on_aprendiz_change():
        for key in st.session_state.keys():
            if key.startswith('extrato_texto_') or key.startswith('show_extrato_'):
                del st.session_state[key]
    
    aprendiz_sel = st.sidebar.selectbox("Selecionar Aprendiz", aprendizes_lista, key="aprendiz_sel_input", on_change=on_aprendiz_change)
    st.session_state['aprendiz_sel_old'] = aprendiz_sel
    
    # Botão de extrato no menu lateral, com show/hide
    # A largura da coluna foi ajustada para evitar a quebra de linha
    col_extrato1, col_extrato2 = st.sidebar.columns([0.4, 0.6])
    with col_extrato1:
        if st.button("📋 Extrato", key=f"btn_extrato_sidebar_{aprendiz_sel}", help=f"Gerar/Ocultar extrato de {aprendiz_sel}"):
            if f"extrato_texto_{aprendiz_sel}" not in st.session_state:
                # Se o extrato ainda não foi gerado, gere-o
                extrato_df = df[df['Aprendiz'] == aprendiz_sel].copy()
                data_iniciacao = extrato_df['Data Iniciação'].iloc[0]
                data_iniciacao_fmt = format_ddmmyyyy(data_iniciacao)
                
                extrato_df['Entregue'] = extrato_df['Entregue'].map({True: '✅', False: '❌'})
                
                texto = f"Extrato de Entregas - Aprendiz {aprendiz_sel}\n"
                texto += f"Iniciação: {data_iniciacao_fmt}\n\n"
                
                for _, row in extrato_df.iterrows():
                    texto += f" - {row['Atividade']}: {row['Entregue']}\n"
                
                st.session_state[f"extrato_texto_{aprendiz_sel}"] = texto
            
            # Inverte o estado de show/hide para o extrato
            if f"show_extrato_{aprendiz_sel}" not in st.session_state:
                st.session_state[f"show_extrato_{aprendiz_sel}"] = True
            else:
                st.session_state[f"show_extrato_{aprendiz_sel}"] = not st.session_state[f"show_extrato_{aprendiz_sel}"]


    # Renderiza o text_area apenas se o estado for True
    if st.session_state.get(f"show_extrato_{aprendiz_sel}", False):
        if f"extrato_texto_{aprendiz_sel}" in st.session_state:
            st.sidebar.text_area(
                f"Extrato de {aprendiz_sel}",
                value=st.session_state[f"extrato_texto_{aprendiz_sel}"],
                height=250,
                key=f"text_area_extrato_{aprendiz_sel}"
            )


    # Checkboxes para marcar entregas
    atividades_sel = df[df["Aprendiz"] == aprendiz_sel]["Atividade"].tolist()
    alterou = False
    for at in atividades_sel:
        entregue_atual = bool(df[(df["Aprendiz"] == aprendiz_sel) & (df["Atividade"] == at)]["Entregue"].values[0])
        novo_valor = st.sidebar.checkbox(at, value=entregue_atual, key=f"{aprendiz_sel}_{at}")
        if novo_valor != entregue_atual:
            df.loc[(df["Aprendiz"] == aprendiz_sel) & (df["Atividade"] == at), "Entregue"] = novo_valor
            alterou = True

    if alterou:
        salvar_dados_google(df)
        st.session_state.df = df
        st.sidebar.success("Entregas atualizadas!")
else:
    st.sidebar.info("Cadastre um aprendiz para marcar entregas.")
