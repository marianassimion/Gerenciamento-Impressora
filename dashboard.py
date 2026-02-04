import streamlit as st
import time
from functions import card, card_planejamento, disparar_envio

st.set_page_config(page_title="Monitoramento de Impressoras", layout="wide")
st.title("Monitoramento de Toner")

# ===============================
# Estado da lista
# ===============================
if "impressoras" not in st.session_state:
    st.session_state.impressoras = None


# ===============================
# FORM DE INPUT
# ===============================
if st.session_state.impressoras is None:

    texto = st.text_area(
        "Lista de impressoras:",
        height=150,
        placeholder="Recepção, 20.200.2.22\nPlanejamento, 10.100.9.82"
    )

    if st.button("Carregar impressoras"):
        lista = []

        for linha in texto.splitlines():
            if "," in linha:
                nome, ip = linha.split(",", 1)
                lista.append({
                    "nome": nome.strip(),
                    "ip": ip.strip()
                })

        if lista:
            st.session_state.impressoras = lista
            st.rerun()
        else:
            st.error("Insira pelo menos uma impressora válida")


# ===============================
# DASHBOARD
# ===============================
else:

    IMPRESSORAS = st.session_state.impressoras

    linhas = [IMPRESSORAS[i:i+3] for i in range(0, len(IMPRESSORAS), 3)]

    for grupo in linhas:
        cols = st.columns(3)
        for col, impressora in zip(cols, grupo):
            with col:
                if impressora["nome"].lower() == "planejamento":
                    card_planejamento(impressora, impressora["ip"])
                else:
                    card(impressora)

    # Botão pra editar lista se quiser
    if st.button("Editar lista de impressoras"):
        st.session_state.impressoras = None
        st.rerun()


# ===============================
# RELATÓRIO
# ===============================
with st.expander("Enviar relatório por e-mail"):
    st.text_input("E-mail de destino", key="input_email")

    if st.button("Enviar agora"):
        disparar_envio(st.session_state.impressoras)


if st.session_state.get('sucesso_envio'):
    msg = st.success("Relatório enviado com sucesso!")
    time.sleep(3)
    msg.empty()
    st.session_state.sucesso_envio = False
    st.rerun()
