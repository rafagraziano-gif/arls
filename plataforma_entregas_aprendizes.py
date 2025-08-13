import streamlit as st
import pandas as pd

# Título da aplicação
st.title("📋 Plataforma de Entregas de Atividades")

# Lista de atividades conforme a imagem
atividades = [
    "Minha Iniciação", "1ª Instrução", "2ª Instrução", "3ª Instrução", "4ª Instrução", "5ª Instrução", "6ª Instrução", "7ª Instrução",
    "O Livro da Lei", "A Coluna Booz", "O Templo de Salomão", "A Pedra Bruta", "O Avental de Aprendiz", "O Bode na Maçonaria",
    "A Cadeia de União", "Questionário de Aprendiz"
]

# Inicialização da sessão
if "aprendizes" not in st.session_state:
    st.session_state.aprendizes = ["Aprendiz 1", "Aprendiz 2", "Aprendiz 3", "Aprendiz 4", "Aprendiz 5", "Aprendiz 6"]
if "entregas" not in st.session_state:
    st.session_state.entregas = pd.DataFrame(False, index=st.session_state.aprendizes, columns=atividades)

# Sidebar para adicionar ou remover aprendizes
st.sidebar.header("👥 Gerenciar Aprendizes")
novo_aprendiz = st.sidebar.text_input("Adicionar novo aprendiz")
if st.sidebar.button("Adicionar"):
    if novo_aprendiz and novo_aprendiz not in st.session_state.aprendizes:
        st.session_state.aprendizes.append(novo_aprendiz)
        st.session_state.entregas.loc[novo_aprendiz] = [False] * len(atividades)

aprendiz_remover = st.sidebar.selectbox("Remover aprendiz", st.session_state.aprendizes)
if st.sidebar.button("Remover"):
    st.session_state.aprendizes.remove(aprendiz_remover)
    st.session_state.entregas.drop(index=aprendiz_remover, inplace=True)

# Filtros
st.subheader("🔍 Filtros")
filtro_aprendiz = st.selectbox("Filtrar por aprendiz", ["Todos"] + st.session_state.aprendizes)
filtro_atividade = st.selectbox("Filtrar por atividade", ["Todas"] + atividades)

# Edição da tabela de entregas
st.subheader("✅ Marcar Entregas")
for aprendiz in st.session_state.aprendizes:
    if filtro_aprendiz != "Todos" and aprendiz != filtro_aprendiz:
        continue
    st.markdown(f"**{aprendiz}**")
    cols = st.columns(len(atividades))
    for i, atividade in enumerate(atividades):
        if filtro_atividade != "Todas" and atividade != filtro_atividade:
            continue
        st.session_state.entregas.at[aprendiz, atividade] = cols[i].checkbox(
            atividade, value=st.session_state.entregas.at[aprendiz, atividade], key=f"{aprendiz}_{atividade}"
        )

# Exibição da tabela final
st.subheader("📊 Tabela de Entregas")
tabela_filtrada = st.session_state.entregas.copy()
if filtro_aprendiz != "Todos":
    tabela_filtrada = tabela_filtrada.loc[[filtro_aprendiz]]
if filtro_atividade != "Todas":
    tabela_filtrada = tabela_filtrada[[filtro_atividade]]

st.dataframe(tabela_filtrada.astype(str))
