import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="JARVIS v17.5 - SEMILLERO", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; background-color: white; color: #1a1a1a; }
    .main-title { font-size: 35px; font-weight: 700; border-left: 8px solid #ffc106; padding-left: 15px; margin-bottom: 25px; }
    .stButton>button { background-color: #ffc106; color: black; border: 2px solid black; font-weight: bold; width: 100%; height: 50px; }
    .param-box { background-color: #f0f2f6; border: 2px solid #ffc106; padding: 20px; border-radius: 10px; color: #1f1f1f; }
    </style>
    """, unsafe_allow_html=True)

# --- SEGURIDAD ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.markdown("<div class='main-title'>🔒 ACCESO JARVIS</div>", unsafe_allow_html=True)
    if st.text_input("Clave:", type="password") == "Juan007" or st.button("INGRESAR"):
        st.session_state['auth'] = True
        st.rerun()
    else: st.error("¿Espía ruso? Clave incorrecta.")
    st.stop()

# --- LÓGICA DE EXTRACCIÓN AVANZADA ---
def limpiar_texto(t):
    if not t: return ""
    return t.encode('ascii', 'ignore').decode('ascii')

def motor_extraccion(pdf_file):
    texto_completo = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        # Leemos las primeras 3 páginas para asegurar captura
        for i in range(min(3, len(reader.pages))):
            texto_completo += reader.pages[i].extract_text().upper() + " "
    except: return {"accionante": "ERROR", "calidad": "error", "accionado": "ERROR"}

    # 1. BUSCAR CALIDAD (Prioridad Periodista)
    calidad = "civil"
    if any(k in texto_completo for k in ["PERIODISTA", "LIBERTAD DE PRENSA", "COMUNICADOR", "REPORTERO", "NOTICIERO"]):
        calidad = "periodista"
    
    # 2. BUSCAR ACCIONANTE (Nombre propio)
    accionante = "NO IDENTIFICADO"
    p_accionante = [
        r"(?:SEÑOR|CIUDADANO|ACTOR|ACCIONANTE)\s*([A-ZÁÉÍÓÚÑ\s]{3,40})(?=\s|INSTAURÓ|PRESENTÓ|INTERPUSO)",
        r"(?:NOMBRE DE\s+)([A-ZÁÉÍÓÚÑ\s]{3,40})",
        r"(?:SENTENCIA\s+T-\d+\s+DE\s+\d+\s+.*?)([A-ZÁÉÍÓÚÑ\s]{3,40})"
    ]
    for p in p_accionante:
        m = re.search(p, texto_completo)
        if m: 
            accionante = m.group(1).strip()
            break

    # 3. BUSCAR ACCIONADO (Entidades)
    accionado = "NO IDENTIFICADO"
    # Diccionario de entidades comunes en estas sentencias
    entidades = ["UNIDAD NACIONAL DE PROTECCION", "UNP", "MINISTERIO DEL INTERIOR", "FISCALIA", "POLICIA NACIONAL", "JUZGADO", "TRIBUNAL"]
    for ent in entidades:
        if ent in texto_completo:
            accionado = ent
            break
    
    # Si no está en el diccionario, buscar por patrón "CONTRA"
    if accionado == "NO IDENTIFICADO":
        m_acc = re.search(r"(?:CONTRA|DEMANDADA)\s+([A-ZÁÉÍÓÚÑ\s\.]{3,50})", texto_completo)
        if m_acc: accionado = m_acc.group(1).strip()

    return {"accionante": accionante, "calidad": calidad, "accionado": accionado}

# --- INTERFAZ ---
st.markdown("<div class='main-title'>JARVIS v17.5: PROCESADOR JURÍDICO</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="large")
with c1:
    st.subheader("⚙️ Configuración Base")
    file_arq = st.file_uploader("Sentencia Arquimédica (PDF)", type="pdf")
    m_calidad = st.selectbox("Calidad Manual", ["No aplica", "Periodista", "Civil"])
    m_accionado = st.text_input("Accionado Manual (Ej: UNP)")

with c2:
    st.subheader("📂 Análisis Masivo")
    files_comp = st.file_uploader("Subir sentencias a comparar", type="pdf", accept_multiple_files=True)

if st.button("🚀 INICIAR COMPARACIÓN"):
    if not (file_arq or m_accionado):
        st.error("Falta información base (Archivo o Manual).")
    else:
        # Extraer parámetros de la Arquimédica
        base = {"calidad": m_calidad.lower(), "accionado": m_accionado.upper(), "accionante": "Manual"}
        if file_arq:
            ext_base = motor_extraccion(file_arq)
            if m_calidad == "No aplica": base["calidad"] = ext_base["calidad"]
            if not m_accionado: base["accionado"] = ext_base["accionado"]
            base["accionante"] = ext_base["accionante"]

        # Mostrar resumen de parámetros
        st.markdown(f"""
        <div class="param-box">
            <b>PARÁMETROS DETECTADOS (ARQUIMÉDICA):</b><br>
            • <b>Accionante:</b> {base['accionante']}<br>
            • <b>Calidad Requerida:</b> {base['calidad'].capitalize()}<br>
            • <b>Accionado Objetivo:</b> {base['accionado']}
        </div>
        """, unsafe_allow_html=True)

        # Comparar
        rows = []
        for f in files_comp:
            info = motor_extraccion(f)
            motivos = []
            
            # Validación de Calidad
            if base["calidad"] != "no aplica" and info["calidad"] != base["calidad"]:
                motivos.append(f"Calidad es {info['calidad']}")
            
            # Validación de Accionado (Cruce de nombres)
            if base["accionado"][:5] not in info["accionado"]:
                motivos.append("Entidad no coincide")
            
            estado = "✅ INCLUIDA" if not motivos else "❌ EXCLUIDA"
            rows.append({
                "Archivo": f.name,
                "Accionante (Detección)": f"{info['accionante']} ({info['calidad']})",
                "Accionado Detectado": info["accionado"],
                "Resultado": estado,
                "Motivo": ", ".join(motivos) if motivos else "Coincidencia plena"
            })

        st.markdown("### 📊 Resultado de la Investigación")
        st.table(pd.DataFrame(rows))
