import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd

# --- 1. CONFIGURACIÓN Y ESTILOS (SE MANTIENEN) ---
st.set_page_config(page_title="JARVIS v18.0 - SEMILLERO", layout="wide")

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

# --- 3. MOTOR DE EXTRACCIÓN MEJORADO (v18.0) ---
def motor_juridico_final(pdf_file):
    texto_acumulado = ""
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        # Analizamos las primeras 5 páginas para capturar encabezado y antecedentes
        for i in range(min(5, len(reader.pages))):
            texto_acumulado += reader.pages[i].extract_text().upper() + " \n "
    except:
        return {"accionante": "ERROR", "calidad": "error", "accionado": "ERROR"}

    # --- CRITERIO ACCIONANTE (Búsqueda de nombres reales/ficticios) ---
    accionante = "NO IDENTIFICADO"
    # Lista de frases que NO son nombres y debemos ignorar
    bloqueo_nombres = ["MAGISTRADO", "PONENTE", "SECRETARIA", "CORTE", "SUPRESION", "DATOS", "RESERVA", "IDENTIDAD"]
    
    patrones_acc = [
        r"(?:SEÑOR|CIUDADANO|ACTOR|ACCIONANTE)\s+([A-ZÁÉÍÓÚÑ]{3,25})(?=\s|[\.,])",
        r"(?:INSTAURADA|PROMOVIDA)\s+POR\s+([A-ZÁÉÍÓÚÑ\s]{4,30})(?=\s+CONTRA|\s+EN|[\.,])"
    ]
    
    for p in patrones_acc:
        m = re.search(p, texto_acumulado)
        if m:
            cand = m.group(1).strip()
            # Validamos que el nombre no contenga palabras prohibidas
            if not any(b in cand for b in bloqueo_nombres) and len(cand) > 2:
                accionante = cand
                break

    # --- CRITERIO ACCIONADO (Búsqueda de Entidad) ---
    accionado = "NO IDENTIFICADO"
    # Patrones específicos de la Corte: "CONTRA...", "ACCIONADO:...", "DEMANDADA:..."
    patrones_ado = [
        r"(?:CONTRA|DEMANDAD[OA]|ACCIONAD[OA])\s*[:\-]?\s*(?:LA|EL|LOS|LAS)?\s*([A-ZÁÉÍÓÚÑ\s\.]{3,55})(?=\s+Y|\s+POR|\s+ANTE|\.|\n|QUIEN|INTERPUSO)",
        r"(?:DIRIGIDA\s+CONTRA)\s+([A-ZÁÉÍÓÚÑ\s\.]{3,55})"
    ]
    
    for p in patrones_ado:
        m = re.search(p, texto_acumulado)
        if m:
            cand = m.group(1).strip()
            # Si el extractor atrapó "ACTO ADMINISTRATIVO" o "SENTENCIA", seguimos buscando
            if not any(b in cand for b in ["ACTO", "SENTENCIA", "PROVIDENCIA", "RECURSO"]) and len(cand) > 3:
                accionado = cand
                break

    # Refuerzo para entidades del Semillero
    entidades_fijas = ["UNIDAD NACIONAL DE PROTECCION", "UNP", "MINISTERIO DEL INTERIOR", "FISCALIA", "POLICIA"]
    for e in entidades_fijas:
        if e in texto_acumulado and (accionado == "NO IDENTIFICADO" or len(accionado) < 5):
            accionado = e
            break

    # --- CRITERIO CALIDAD ---
    calidad = "civil"
    if any(k in texto_acumulado for k in ["PERIODISTA", "LIBERTAD DE PRENSA", "COMUNICADOR", "REPORTERO"]):
        calidad = "periodista"
                
    return {"accionante": accionante, "calidad": calidad, "accionado": accionado}

# --- 4. INTERFAZ Y PROCESAMIENTO ---
st.markdown("<div class='main-title'>JARVIS JURÍDICO v18.0</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("⚙️ Configuración Base")
    file_arq = st.file_uploader("Sentencia Arquimédica", type="pdf", key="arq")
    m_calidad = st.selectbox("Calidad Manual", ["No aplica", "Periodista", "Civil"])
    m_accionado = st.text_input("Accionado Manual")

with col2:
    st.subheader("📂 Análisis Masivo")
    files_comp = st.file_uploader("Subir archivos comparativos", type="pdf", accept_multiple_files=True, key="masivo")

if st.button("🚀 EJECUTAR ANÁLISIS"):
    if not file_arq and not m_accionado:
        st.error("Debe proporcionar una base (PDF o texto manual).")
    elif not files_comp:
        st.warning("Suba sentencias para analizar.")
    else:
        # Extraer parámetros de la Arquimédica
        base = {"calidad": m_calidad.lower(), "accionado": m_accionado.upper(), "accionante": "No identificado"}
        if file_arq:
            ext_base = motor_juridico_final(file_arq)
            base["accionante"] = ext_base["accionante"]
            if m_calidad == "No aplica": base["calidad"] = ext_base["calidad"]
            if not m_accionado: base["accionado"] = ext_base["accionado"]

        st.markdown(f"""
        <div class="param-box">
            <b>PARÁMETROS DE LA SENTENCIA ARQUIMÉDICA:</b><br>
            La sentencia arquimédica dio como parámetros un accionante <b>{base['accionante']}</b> (Calidad: {base['calidad']}), 
            siendo el accionado <b>{base['accionado']}</b>.
        </div>
        """, unsafe_allow_html=True)

        # Generar Tabla
        resultados = []
        for f in files_comp:
            info = motor_juridico_final(f)
            fallos = []
            if base["calidad"] != "no aplica" and info["calidad"] != base["calidad"]:
                fallos.append(f"Calidad ({info['calidad']})")
            if base["accionado"][:5] not in info["accionado"]:
                fallos.append("Accionado diferente")
            
            estado = "✅ INCLUIDA" if not fallos else "❌ EXCLUIDA"
            resultados.append({
                "Archivo": f.name,
                "Accionante / Calidad": f"{info['accionante']} / {info['calidad']}",
                "Accionado Detectado": info["accionado"],
                "Resultado": estado,
                "Motivo": ", ".join(fallos) if fallos else "Coincidencia plena"
            })
        
        st.table(pd.DataFrame(resultados))

        # --- REPORTE PDF SEGURO ---
        def safe_pdf(txt): return txt.encode('ascii', 'ignore').decode('ascii')
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "REPORTE DE INVESTIGACION - JARVIS", 0, 1, 'C')
        pdf.set_font("Arial", '', 10)
        pdf.ln(5)
        pdf.multi_cell(0, 7, safe_pdf(f"PARAMETROS BASE:\nAccionante: {base['accionante']}\nAccionado: {base['accionado']}\nCalidad: {base['calidad']}\n" + "="*50))
        
        for r in resultados:
            pdf.set_fill_color(255, 193, 6) if "INCLUIDA" in r["Resultado"] else pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, safe_pdf(f"Doc: {r['Archivo']}"), 1, 1, 'L', True)
            pdf.multi_cell(0, 6, safe_pdf(f"Accionante: {r['Accionante / Calidad']}\nAccionado: {r['Accionado Detectado']}\nResultado: {r['Resultado']}\nMotivo: {r['Motivo']}\n" + "."*80))
            pdf.ln(2)

        pdf_bin = pdf.output(dest='S').encode('latin-1')
        st.download_button("📥 DESCARGAR REPORTE FINAL", data=pdf_bin, file_name="analisis_jarvis.pdf")
