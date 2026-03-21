import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import io

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="JARVIS v17 - PRO", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; background-color: white; color: #1a1a1a; }
    .main-title { font-size: 40px; font-weight: 700; border-left: 10px solid #ffc106; padding-left: 20px; margin-bottom: 30px; }
    .stButton>button { background-color: #ffc106; color: black; border: none; font-weight: bold; width: 100%; height: 50px; }
    .stButton>button:hover { background-color: black; color: #ffc106; }
    </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE SEGURIDAD ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

if not st.session_state['autenticado']:
    st.markdown("<div class='main-title'>🔒 ACCESO RESTRINGIDO</div>", unsafe_allow_html=True)
    clave = st.text_input("Ingrese la clave de seguridad:", type="password")
    if st.button("INGRESAR"):
        if clave == "Juan007":
            st.session_state['autenticado'] = True
            st.rerun()
        else:
            st.error("¿Eres un espía ruso intentando robar el código? Pues te salió mal: la clave es incorrecta.")
    st.stop()

# --- FUNCIONES TÉCNICAS ---
def analizar_texto(texto):
    calidad = "periodista" if any(k in texto.upper() for k in ["PERIODISTA", "PRENSA", "RADIO", "COMUNICADOR"]) else "ciudadano(a)"
    match = re.search(r"(ACCIONADO|CONTRA|EN CONTRA DE)\s*:\s*([A-ZÁÉÍÓÚÑ\s]{3,60})", texto.upper())
    accionado = match.group(2).strip() if match else "NO IDENTIFICADO"
    return {"calidad": calidad, "accionado": accionado}

# --- INTERFAZ ---
st.markdown("<div class='main-title'>JARVIS JURÍDICO v17</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📁 Parámetros de Inclusión")
    file_arq = st.file_uploader("Cargar Sentencia Arquimédica", type="pdf")
    st.write("**Opcional: Entrada Manual**")
    m_calidad = st.selectbox("Calidad requerida", ["Automático", "Periodista", "Ciudadano(a)"])
    m_accionado = st.text_input("Entidad accionada (Ej: UNP, Fiscalía)")

with col2:
    st.subheader("📄 Sentencias a Procesar")
    files_comp = st.file_uploader("Subir archivos para análisis", type="pdf", accept_multiple_files=True)

if st.button("EJECUTAR ANÁLISIS"):
    if not file_arq and not m_accionado:
        st.warning("Por favor, cargue un PDF base o ingrese la información manual.")
    else:
        # Extraer base
        base = {"calidad": "periodista", "accionado": m_accionado.upper()}
        if file_arq:
            t_base = PyPDF2.PdfReader(file_arq).pages[0].extract_text()
            extraido = analizar_texto(t_base)
            if not m_accionado: base["accionado"] = extraido["accionado"]
            if m_calidad == "Automático": base["calidad"] = extraido["calidad"]
        
        # Procesar comparativas
        relevantes = []
        for f in files_comp:
            t_f = PyPDF2.PdfReader(f).pages[0].extract_text()
            info_f = analizar_texto(t_f)
            # Lógica de comparación
            if info_f["calidad"] == base["calidad"] and base["accionado"][:5] in info_f["accionado"]:
                relevantes.append(f.name)
        
        st.markdown("---")
        st.success(f"Análisis finalizado. Se encontraron **{len(relevantes)}** sentencias relevantes.")
        if relevantes:
            st.write(f"Las sentencias que cumplen los criterios son: {', '.join(relevantes)}")
        
        # Botón de descarga (Simulado para esta versión rápida)
        st.download_button("📥 DESCARGAR RESULTADOS", "Resultados del análisis...", "analisis.txt")