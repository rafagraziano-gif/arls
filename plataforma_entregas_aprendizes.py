import streamlit as st
import pandas as pd

# Lista inicial de aprendizes
aprendizes = ["Aprendiz 1", "Aprendiz 2", "Aprendiz 3", "Aprendiz 4", "Aprendiz 5", "Aprendiz 6"]

# Lista de atividades
atividades = [
    "Minha Iniciação", "1ª Instrução", "2ª Instrução", "3ª Instrução", "4ª Instrução", "5ª Instrução", "6ª Instrução", "7ª Instrução",
    "O Livro da Lei", "A Coluna Booz", "O Templo de Salomão", "A Pedra Bruta", "O Avental de Aprendiz", "O Bode na Maçonaria",
    "A Cadeia de União", "Questionário de Aprendiz"
]

# Inicializa o estado da sessão
if "entregas" not in st.session_state:
    st.session_state.entregas = {aprendiz: {atividade: False for atividade in atividades} for aprendiz in aprendizes}

if "aprendizes" not in st.session_state:
    st.session_state.aprendizes = aprendizes.copy()

# Sidebar - Gerenciar aprendizes
st.sidebar.header("Gerenciar Aprendizes")
novo_aprendiz = st.sidebar.text_input("Adicionar novo aprendiz")
if st.sidebar.button("Adicionar"):
    if novo_aprendiz and novo_aprendiz not in st.session_state.aprendizes:
        st.session_state.aprendizes.append(novo_aprendiz)
        st.session_state.entregas[novo_aprendiz] = {atividade: False for atividade in atividades}

aprendiz_remover = st.sidebar.selectbox("Remover aprendiz", st.session_state.aprendizes)
if st.sidebar.button("Remover"):
    st.session_state.aprendizes.remove(aprendiz_remover)
    st.session_state.entregas.pop(aprendiz_remover, None)

# Sidebar - Marcar entregas
st.sidebar.header("Marcar Entregas")
aprendiz_selecionado = st.sidebar.selectbox("Selecionar Aprendiz", st.session_state.aprendizes)
for atividade in atividades:
    st.session_state.entregas[aprendiz_selecionado][atividade] = st.sidebar.checkbox(
        label=atividade,
        value=st.session_state.entregas[aprendiz_selecionado][atividade],
        key=f"{aprendiz_selecionado}_{atividade}"
    )

# Título
st.title("📘 Plataforma de Entregas de Atividades")

# Filtros
st.subheader("Filtros")
filtro_aprendiz = st.selectbox("Filtrar por Aprendiz", ["Todos"] + st.session_state.aprendizes)
filtro_atividade = st.selectbox("Filtrar por Atividade", ["Todas"] + atividades)

# Monta a tabela completa
tabela = pd.DataFrame(index=st.session_state.aprendizes, columns=atividades)
for aprendiz in st.session_state.aprendizes:
    for atividade in atividades:
        tabela.loc[aprendiz, atividade] = "✔️" if st.session_state.entregas
