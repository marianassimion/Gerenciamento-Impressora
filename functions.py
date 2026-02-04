import streamlit as st
import requests
from bs4 import BeautifulSoup
import smtplib
from email.message import EmailMessage

# ==========================
# LEITURA DO TONER
# ==========================
def ler_toner(ip):
    html = requests.get(f"http://{ip}", timeout=5).text
    soup = BeautifulSoup(html, "html.parser")

    toners = {}

    for img in soup.find_all("img", class_="tonerremain"):
        height = img.get("height")
        cor = img.get("alt", "").lower()

        if height and cor:
            toners[cor] = int(height)

    if not toners:
        return None

    max_level = max(toners.values())

    return {
        cor: round((nivel / max_level) * 100, 1)
        for cor, nivel in toners.items()
    }

def ler_toner_planejamento(ip):
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html"
    }

    base = f"http://{ip}/web/guest/pt/websys/webArch/"

    # cria sessão
    session.get(base + "getStatus.cgi", headers=headers)

    # pega página real com toner
    r = session.get(base + "getStatus.cgi", headers=headers)

    soup = BeautifulSoup(r.text, "html.parser")
    toners_px = {}

    for img in soup.select("div.tonerArea img"):
        largura = int(img["width"])
        cor = img.find_previous("dt", class_="listboxdtm").text.strip().lower()
        toners_px[cor] = largura

    if not toners_px:
        return None

    MAX_WIDTH = 160  # barra cheia = 100%

    # converte de pixel → porcentagem
    toners_percentual = {
        cor: round((px / MAX_WIDTH) * 100)
        for cor, px in toners_px.items()
    }

    return toners_percentual

# ==========================
# TONER EM FORMATO DE BATERIA
# ==========================

def bateria_toner(cor, pct):
    cores = {
        "black": "#2b2b2b",
        "cyan": "#00a8e8",
        "magenta": "#ec008c",
        "yellow": "#fff200",
    }

    cor_css = cores.get(cor, "#999")
    texto_cor = "black" if cor == "yellow" else "white"

    st.markdown(
        f"""
        <div style="
            width:60px;
            height:130px;
            border:3px solid #333;
            border-radius:10px;
            padding:4px;
            position:relative;
            background:#f2f2f2;
            margin:auto;
        ">
            <div style="
                position:absolute;
                bottom:4px;
                left:4px;
                right:4px;
                height:{pct}%;
                background:{cor_css};
                border-radius:6px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-weight:800;
                color:{texto_cor};
                font-size:14px;
            ">
                {pct}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def bateria_toner_planejamento(cor, pct):
    cores = {
        "preto": "#2b2b2b",
        "ciano": "#00a8e8",
        "magenta": "#ec008c",
        "amarelo": "#fff200",
    }

    cor_css = cores.get(cor, "#999")
    texto_cor = "black" if cor == "yellow" else "white"

    st.markdown(
        f"""
        <div style="
            width:60px;
            height:130px;
            border:3px solid #333;
            border-radius:10px;
            padding:4px;
            position:relative;
            background:#f2f2f2;
            margin:auto;
        ">
            <div style="
                position:absolute;
                bottom:4px;
                left:4px;
                right:4px;
                height:{pct}%;
                background:{cor_css};
                border-radius:6px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-weight:800;
                color:{texto_cor};
                font-size:14px;
            ">
                {pct}%
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# ==========================
# CARD COM DIVISÓRIA
# ==========================

def card(impressora):

    st.markdown(
    f"""
    <div style="
        display:flex; 
        justify-content:space-between; 
        align-items:center;
        border: 1px solid;
        border-radius: 15px;">
        <h4 style="margin:8px;">{impressora['nome']}</h4>
        <small style="color:#fffff; margin-right:8px">{impressora['ip']}</small>
    </div>

    <hr style="margin:6px 0; opacity:.3">
    """,
    unsafe_allow_html=True
)
    dados = ler_toner(impressora["ip"])

    if dados is None:
        st.error("Offline")
        return
    st.markdown(
        "<div style='display:flex; justify-content:flex-start;'>",
        unsafe_allow_html=True
    )
    
    cols = st.columns(len(dados), gap="small")

    for col, (_, pct) in zip(cols, dados.items()):
        with col:
            bateria_toner(_, pct)
            
    st.markdown("</div>", unsafe_allow_html=True)
    
    if min(dados.values()) < 20:
        st.warning("⚠ Toner baixo")

    cor_minima, nivel_minimo = min(dados.items(), key=lambda x: x[1])

    if min(dados.values()) < 20 and not impressora.get("alerta_enviado", False):
        enviar_alerta(impressora["nome"], nivel_minimo, cor_minima) 
        impressora["alerta_enviado"] = True

    st.markdown("</div>", unsafe_allow_html=True)

def card_planejamento(impressora, ip):

    st.markdown(
        f"""
        <div style="
            display:flex; 
            justify-content:space-between; 
            align-items:center;
            border: 1px solid;
            border-radius: 15px;
            padding:6px;">
            <h4 style="margin:8px;">{impressora['nome']}</h4>
            <small style="margin-right:8px">{impressora['ip']}</small>
        </div>

        <hr style="margin:6px 0; opacity:.3">
        """,
        unsafe_allow_html=True
    )

    dados = ler_toner_planejamento(ip)

    if not dados:
        st.error("Offline")
        return

    cols = st.columns(len(dados), gap="small")

    for col, (cor, pct) in zip(cols, dados.items()):
        with col:
            bateria_toner_planejamento(cor, pct)

    # alerta visual
    if min(dados.values()) < 20:
        st.warning("⚠ Toner baixo")

    cor_minima, nivel_minimo = min(dados.items(), key=lambda x: x[1])

    # alerta por email (só uma vez)
    if nivel_minimo < 20 and not impressora.get("alerta_enviado", False):
        enviar_alerta(
            impressora["nome"],
            nivel_minimo,
            cor_minima
        )
        impressora["alerta_enviado"] = True

# ==========================
# ENVIO DE E-MAIL
# ==========================

def enviar_alerta(impressora, nivel, cor):
    msg = EmailMessage()
    msg["Subject"] = "Toner baixo"
    msg["From"] = "gerenciamento.teste.ctin@gmail.com"
    msg["To"] = "mariana.santos@cnsesi.com.br, samara.lima@cnsesi.com.br"

    msg.set_content(
        f"A impressora {impressora} está com toner da cor {cor} em {nivel}%."
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("gerenciamento.teste.ctin@gmail.com", "cbxl hwpg ujaa mdte")
        smtp.send_message(msg)

# ==========================
# ENVIO DE RELATÓRIO DE E-MAIL
# ==========================
def enviar_relatorio(email_destino, IMPRESSORAS):
    msg = EmailMessage()
    msg["Subject"] = "Relatório de Toner das Impressoras"
    msg["From"] = "gerenciamento.teste.ctin@gmail.com"
    msg["To"] = f"{email_destino}, mariana.santos@cnsesi.com.br"

    texto = "RELATÓRIO DE TONER\n\n"

    for impressora in IMPRESSORAS:

        if impressora["nome"].lower() == "planejamento":
            dados = ler_toner_planejamento(impressora["ip"])
                        
        else:
            dados = ler_toner(impressora["ip"])

        if dados is None:
            texto += f"{impressora['nome']} — Offline\n"

        else:
            for cor, nivel in dados.items():
                texto += f"{impressora['nome']} | {cor}: {nivel}%\n"

        texto += "\n"

    texto += f"Relatório gerado para {email_destino}"

    msg.set_content(texto)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("gerenciamento.teste.ctin@gmail.com", "cbxl hwpg ujaa mdte")
        smtp.send_message(msg)

def disparar_envio(IMPRESSORAS):
    email = st.session_state.input_email

    if not email:
        st.error("Por favor, preencha o e-mail.")
        return

    enviar_relatorio(email, IMPRESSORAS)
    st.session_state.sucesso_envio = True
    st.session_state.input_email = ""
