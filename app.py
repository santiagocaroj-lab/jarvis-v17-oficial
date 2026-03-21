import streamlit as st
import PyPDF2
import re
import pandas as pd

# --- ESTILOS ---
st.set_page_config(page_title="JARVIS v17.8 - SEMILLERO", layout="wide")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; }
    .main-title { font-size: 35px; font-weight: 700; border-left: 8px solid #ffc106; padding-left: 15px; margin-bottom: 25px; }
    .param-box { background-color: #f0f2f6; border: 2px solid #ffc106; padding: 20px; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- SEGURIDAD ---
if 'auth' not in st.session_state: st.session_state['auth'] = False
if not st.session_state['auth']:
    st.markdown("<div class='main-title'>🔒 ACCESO JARVIS</div>")
    if st.text_input("Clave:", type="password") == "Juan007":
        st.session_state['auth'] = True
        st.rerun()
    st.stop()

# --- MOTOR DE EXTRACCIÓN JURÍDICO v4 (ANTI-ANONIMIZACIÓN) ---
def motor_juridico_v4(pdf_file):
    texto = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        # Leemos más páginas porque el nombre suele estar en los antecedentes (pág 2-4)
        for i in range(min(6, len(reader.pages))):
            texto += reader.pages[i].extract_text().upper() + " \n "
    except: return {"accionante": "ERROR", "calidad": "error", "accionado": "ERROR"}

    # 1. FILTRO DE FRASES PROHIBIDAS (Lo que te causó el error)
    frases_ruido = [
        r"SUPRESIÓN DE LOS DATOS QUE PERMITAN",
        r"RESERVA DE LA IDENTIDAD",
        r"DATOS QUE PERMITAN IDENTIFICAR",
        r"MAGISTRADO PONENTE.*",
        r"SECRETARÍA GENERAL.*"
    ]
    for frase in frases_ruido:
        texto = re.sub(frase, "[FILTRADO]", texto)

    # 2. IDENTIFICAR ACCIONANTE (Buscando nombres ficticios o reales)
    # Priorizamos nombres que aparezcan después de "SEÑOR" o "CIUDADANO"
    accionante = "NOMBRE PROTEGIDO / NO DETECTADO"
    
    # Patrón mejorado para capturar nombres cortos (como Luis, Alejandro) o largos
    p_acc = [
        r"(?:SEÑOR|CIUDADANO|ACTOR)\s+([A-ZÁÉÍÓÚÑ]{3,20})(?=\s|[\.,])", # Captura nombres como LUIS
        r"(?:ACCIONANTE|DEMANDANTE)\s+([A-ZÁÉÍÓÚÑ\s]{4,30})(?=\s+INTERPUSO|\s+PRESENTÓ)"
    ]
    
    for p in p_acc:
        m = re.search(p, texto)
        if m:
            cand = m.group(1).strip()
            # Si el candidato es una palabra legal común, lo ignoramos
            if cand not in ["DERECHO", "CORTE", "TUTELA", "SENTENCIA", "ACCIONANTE"]:
                accionante = cand
                break

    # 3. IDENTIFICAR CALIDAD
    calidad = "civil"
    if any(k in texto for k in ["PERIODISTA", "LIBERTAD DE PRENSA", "COMUNICADOR", "REPORTERO"]):
        calidad = "periodista"
    
    # 4. IDENTIFICAR ACCIONADO
    accionado = "NO IDENTIFICADO"
    p_to = r"(?:CONTRA|DEMANDAD[OA])\s+(?:LA|EL|LOS|LAS)?\s*([A-ZÁÉÍÓÚÑ\s\.]{3,50})(?=\s+Y|\s+POR|\s+ANTE|\.|\n)"
    m_to = re.search(p_to, texto)
    if m_to:
        accionado = m_to.group(1).strip()
    
    # Refuerzo para la UNP
    if "UNIDAD NACIONAL DE PROTECCION" in texto or "UNP" in texto:
        if accionado == "NO IDENTIFICADO" or len(accionado) < 2:
            accionado = "UNIDAD NACIONAL DE PROTECCIÓN (UNP)"
                
    return {"accionante": accionante, "calidad": calidad, "accionado": accionado}

# --- INTERFAZ ---
st.markdown("<div class='main-title'>JARVIS v17.8: INVESTIGACIÓN JURÍDICA</div>", unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="large")
with c1:
    st.subheader("⚙️ Parámetros Base")
    file_arq = st.file_uploader("Sentencia Arquimédica", type="pdf")
    m_calidad = st.selectbox("Calidad Manual", ["No aplica", "Periodista", "Civil"])
    m_accionado = st.text_input("Accionado Manual")

with c2:
    st.subheader("📂 Análisis Masivo")
    files_comp = st.file_uploader("Subir archivos", type="pdf", accept_multiple_files=True)

if st.button("🚀 EJECUTAR"):
    if not (file_arq or m_accionado):
        st.error("Falta la sentencia base.")
    else:
        base = {"calidad": m_calidad.lower(), "accionado": m_accionado.upper(), "accionante": "Manual"}
        if file_arq:
            ext_base = motor_juridico_v4(file_arq)
            base["accionante"] = ext_base["accionante"]
            if m_calidad == "No aplica": base["calidad"] = ext_base["calidad"]
            if not m_accionado: base["accionado"] = ext_base["accionado"]

        st.markdown(f"""
        <div class="param-box">
            <b>PARÁMETROS DETECTADOS:</b><br>
            • Accionante: <b>{base['accionante']}</b><br>
            • Calidad: <b>{base['calidad'].upper()}</b><br>
            • Accionado: <b>{base['accionado']}</b>
        </div>
        """, unsafe_allow_html=True)

        rows = []
        for f in files_comp:
            info = motor_juridico_v4(f)
            motivos = []
            if base["calidad"] != "no aplica" and info["calidad"] != base["calidad"]:
                motivos.append("Calidad")
            if base["accionado"][:5] not in info["accionado"]:
                motivos.append("Accionado")
            
            estado = "✅ INCLUIDA" if not motivos else "❌ EXCLUIDA"
            rows.append({
                "Archivo": f.name,
                "Accionante / Calidad": f"{info['accionante']} ({info['calidad']})",
                "Accionado": info["accionado"],
                "Resultado": estado,
                "Motivo": ", ".join(motivos) if motivos else "Coincidencia"
            })
        st.table(pd.DataFrame(rows))
