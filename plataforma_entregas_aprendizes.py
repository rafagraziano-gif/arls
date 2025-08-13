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

# Inicializa o estado da sessão para armazenar entregas e lista de aprendizes
if "entregas" not in st.session_state:
    st.session_state.entregas = {aprendiz: {atividade: False for atividade in atividades} for aprendiz in aprendizes}

if "aprendizes" not in st.session_state:
    st.session_state.aprendizes = aprendizes.copy()

# Interface lateral para adicionar ou remover aprendizes
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

# Título da aplicação
st.title("📘 Plataforma de Entregas de Atividades")

# Exibe a tabela de entregas com checkboxes
st.write("### Marcar entregas")
for aprendiz in st.session_state.aprendizes:
    st.write(f"**{aprendiz}**")
    cols = st.columns(len(atividades))
    for i, atividade in enumerate(atividades):
        st.session_state.entregas[aprendiz][atividade] = cols[i].checkbox(
            label=atividade,
            value=st.session_state.entregas[aprendiz][atividade],
            key=f"{aprendiz}_{atividade}"
        )
