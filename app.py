import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd

# --- 1. CONFIGURACIÓN Y ESTILOS (SE MANTIENEN) ---
st.set_page_config(page_title="JARVIS v17.9 - SEMILLERO", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; background-color: white; color: #1a1a1a; }
    .main-title { font-size: 38px; font-weight: 700; border-left: 10px solid #ffc106; padding-left: 20px; margin-bottom: 30px; }
    .stButton>button { background-color: #ffc106; color: black; border: 2px solid black; font-weight: bold; width: 100%; height: 50px; }
    .stButton>button:hover { background-color: black; color: #ffc106; }
    .param-box { background-color: #f8f9fa; border: 2px solid #ffc106; padding: 20px; border-radius: 10px; margin-bottom: 25px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SISTEMA DE SEGURIDAD (SIEMPRE ACTIVO) ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("<div class='main-title'>🔒 ACCESO RESTRINGIDO JARVIS</div>", unsafe_allow_html=True)
    clave = st.text_input("Ingrese la clave de seguridad:", type="password")
    if st.button("INGRESAR"):
        if clave == "Juan007":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Acceso denegado.")
    st.stop()

# --- 3. MOTOR DE EXTRACCIÓN REFINADO ---
def motor_juridico_pro(pdf_file):
    texto = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        # Analizamos hasta 5 páginas para encontrar los hechos y el resuelve
        for i in range(min(5, len(reader.pages))):
            texto += reader.pages[i].extract_text().upper() + " \n "
    except: return {"accionante": "ERROR", "calidad": "error", "accionado": "ERROR"}

    # --- LIMPIEZA DE RUIDO JURÍDICO ---
    # Eliminamos frases de magistrados y órdenes administrativas que confunden al extractor
    ruido = [
        r"MAGISTRADO PONENTE.*", r"SECRETARÍA GENERAL.*", r"SALA DE SELECCIÓN.*",
        r"SUPRESIÓN DE LOS DATOS.*", r"RESERVA DE LA IDENTIDAD.*", r"ACTO ADMINISTRATIVO",
        r"EXPEDIENTE T-.*", r"SENTENCIA T-.*"
    ]
    texto_limpio = texto
    for r in ruido:
        texto_limpio = re.sub(r, " ", texto_limpio)

    # --- CRITERIOS PARA ACCIONANTE ---
    # Buscamos nombres propios después de palabras de interposición
    accionante = "NO DETECTADO"
    patrones_ante = [
        r"(?:SEÑOR|CIUDADANO|ACTOR|ACCIONANTE)\s+([A-ZÁÉÍÓÚÑ]{3,20})(?=\s|[\.,])",
        r"(?:INSTAURADA|PROMOVIDA|PRESENTADA)\s+POR\s+(?:EL\s+SEÑOR\s+)?([A-ZÁÉÍÓÚÑ\s]{4,30})(?=\s+CONTRA|\s+EN|[\.,])"
    ]
    for p in
