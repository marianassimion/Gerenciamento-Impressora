import streamlit as st
import time
#from impressoras import IMPRESSORAS
from functions import card, card_planejamento, disparar_envio

st.set_page_config(page_title="Monitoramento de Impressoras", layout="wide")
st.title("Monitoramento de Toner")

texto = st.text_area(
    "Lista de impressoras:",
    height=150,
    placeholder="Recepção, 20.200.2.22"
)
IMPRESSORAS = []

if texto:
    for linha in texto.splitlines():
        if "," in linha:
            nome, ip = linha.split(",", 1)
            IMPRESSORAS.append({
                "nome": nome.strip(),
                "ip": ip.strip()
            })

linhas = [IMPRESSORAS[i:i+3] for i in range(0, len(IMPRESSORAS), 3)]

for grupo in linhas:
    cols = st.columns(3)
    for col, impressora in zip(cols, grupo):
        with col:
            if impressora["nome"].lower()== "planejamento":
                card_planejamento(impressora,impressora["ip"])
            else:
                card(impressora)


with st.expander("Enviar relatório por e-mail"):
    st.text_input("E-mail de destino", key="input_email")
    
    if st.button("Enviar agora", on_click=disparar_envio(IMPRESSORAS)):
        pass

if st.session_state.get('sucesso_envio'):
    msg = st.success("Relatório enviado com sucesso!")
    time.sleep(3)
    msg.empty()
    st.session_state.sucesso_envio = False
    st.rerun()
