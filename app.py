import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="JARVIS v17.4 - PRO", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Montserrat', sans-serif; 
        background-color: white; 
        color: #1a1a1a; 
    }
    .main-title { 
        font-size: 40px; 
        font-weight: 700; 
        border-left: 10px solid #ffc106; 
        padding-left: 20px; 
        margin-bottom: 30px; 
    }
    .stButton>button { 
        background-color: #ffc106; 
        color: black; 
        border: 2px solid black;
        font-weight: bold; 
        width: 100%; 
        height: 50px; 
    }
    .stButton>button:hover { 
        background-color: black; 
        color: #ffc106; 
    }
    .param-box {
        background-color: #f9f9f9;
        border: 1px solid #ffc106;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
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

# --- FUNCIONES DE EXTRACCIÓN MEJORADAS ---
def limpiar_para_pdf(texto):
    if not texto: return ""
    reemplazos = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U','ñ':'n','Ñ':'N'}
    for orig, new in reemplazos.items():
        texto = texto.replace(orig, new)
    return texto.encode('ascii', 'ignore').decode('ascii')

def analizar_entidades(texto):
    t = texto.upper()
    
    # 1. Identificar Accionante (Nombre)
    accionante = "NO IDENTIFICADO"
    patrones_te = [
        r"(?:ACCIONANTE|DEMANDANTE|PROMOVIDA POR|INTERPUESTA POR|CIUDADANO|SEÑOR\(A\))\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s\.]{3,50})(?=\s|CONTRA|INSTAURÓ|PRESENTÓ)",
        r"(?:AUTOR\s*:\s*)([A-ZÁÉÍÓÚÑ\s\.]{3,50})"
    ]
    for p in patrones_te:
        m = re.search(p, t)
        if m: 
            accionante = m.group(1).strip()
            break

    # 2. Identificar Calidad
    calidad = "no aplica"
    palabras_periodista = ["PERIODISTA", "PRENSA", "RADIO", "COMUNICADOR", "REPORTERO", "NOTICIERO", "MEDIO DE COMUNICACION"]
    if any(k in t for k in palabras_periodista):
        calidad = "periodista"
    elif "CIUDADANO" in t or "CIVIL" in t:
        calidad = "civil"
    
    # 3. Identificar Accionado (Entidad)
    accionado = "NO IDENTIFICADO"
    patrones_to = [
        r"(?:ACCIONADO|CONTRA|DEMANDADO|DIRIGIDA CONTRA|EN CONTRA DE)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s\.]{3,60})(?=\s|INSTAURÓ|ANTE|POR|DERECHOS|RESUELVE)",
        r"(?:CONTRA LA|CONTRA EL)\s+([A-ZÁÉÍÓÚÑ\s\.]{3,60})",
        r"(?:NOTIFÍQUESE A)\s+([A-ZÁÉÍÓÚÑ\s\.]{3,60})"
    ]
    for p in patrones_to:
        m = re.search(p, t)
        if m:
            posible = m.group(1).strip()
            posible = re.split(r'\s(Y|PARA|QUE|EL|LA|EN|CON)\s', posible)[0]
            if len(posible) > 3:
                accionado = posible
                break
                
    return {"accionante": accionante, "calidad": calidad, "accionado": accionado}

# --- INTERFAZ ---
st.markdown("<div class='main-title'>JARVIS JURÍDICO v17.4</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📁 Parámetros de Inclusión")
    file_arq = st.file_uploader("1. Cargar Sentencia Arquimédica", type="pdf")
    st.write("---")
    st.write("✍️ **Entrada Manual (Facultativo)**")
    m_calidad = st.selectbox("Calidad del accionante", ["No aplica", "Periodista", "Civil"])
    m_accionado = st.text_input("Entidad accionada (Ej: UNP, Fiscalía, etc.)")

with col2:
    st.subheader("📄 Sentencias a Procesar")
    files_comp = st.file_uploader("2. Subir sentencias para análisis masivo", type="pdf", accept_multiple_files=True)

if st.button("🚀 EJECUTAR ANÁLISIS COMPARATIVO"):
    if not file_arq and not m_accionado:
        st.warning("Debe cargar un PDF base o completar la información manual.")
    elif not files_comp:
        st.warning("Por favor, suba al menos una sentencia para analizar.")
    else:
        # Procesar Arquimédica para definir Base
        base = {"calidad": m_calidad.lower(), "accionado": m_accionado.upper(), "accionante": "No definido"}
        
        if file_arq:
            t_base = PyPDF2.PdfReader(file_arq).pages[0].extract_text()
            ext_base = analizar_entidades(t_base)
            base["accionante"] = ext_base["accionante"]
            if not m_accionado: base["accionado"] = ext_base["accionado"]
            if m_calidad == "No aplica": base["calidad"] = ext_base["calidad"]

        # Mensaje de Parámetros
        st.markdown(f"""
        <div class="param-box">
            <b>RESULTADO DE PARÁMETROS:</b><br>
            La sentencia arquimédica dio como parámetros un accionante <b>{base['accionante']}</b> (Calidad: {base['calidad']}), 
            siendo el accionado <b>{base['accionado']}</b>.
        </div>
        """, unsafe_allow_html=True)

        # Procesar Comparativas
        resultados_tabla = []
        for f in files_comp:
            try:
                t_f = PyPDF2.PdfReader(f).pages[0].extract_text()
                info_f = analizar_entidades(t_f)
                
                razones = []
                # Solo comparamos calidad si no es "no aplica"
                if base["calidad"] != "no aplica" and info_f["calidad"] != base["calidad"]: 
                    razones.append(f"Calidad distinta ({info_f['calidad']})")
                
                # Comparación de accionado (Sustancial)
                if base["accionado"][:6] not in info_f["accionado"]: 
                    razones.append("Entidad no coincide")
                
                es_ok = len(razones) == 0
                resultados_tabla.append({
                    "Sentencia": f.name,
                    "Accionante (Nombre/Calidad)": f"{info_f['accionante']} / {info_f['calidad']}",
                    "Accionado": info_f["accionado"],
                    "Resultado": "✅ INCLUIDA" if es_ok else "❌ EXCLUIDA",
                    "Motivo": ", ".join(razones) if razones else "Cumple criterios"
                })
            except:
                resultados_tabla.append({"Sentencia": f.name, "Accionante (Nombre/Calidad)": "N/A", "Accionado": "ERROR", "Resultado": "ERROR", "Motivo": "Ilegible"})

        # Mostrar Tabla
        st.markdown("### 📊 TABLA DE ANÁLISIS")
        st.table(pd.DataFrame(resultados_tabla))

        # PDF Reporte
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "REPORTE DE ANALISIS JURIDICO - JARVIS", 0, 1, 'C')
        pdf.set_font("Arial", '', 10)
        pdf.ln(5)
        pdf.multi_cell(0, 7, limpiar_para_pdf(f"PARAMETROS BASE:\nAccionante: {base['accionante']}\nAccionado: {base['accionado']}\nCalidad: {base['calidad']}\n" + "="*50))
        
        for r in resultados_tabla:
            pdf.set_fill_color(255, 193, 6) if "INCLUIDA" in r["Resultado"] else pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, limpiar_para_pdf(f"Doc: {r['Sentencia']}"), 1, 1, 'L', True)
            pdf.multi_cell(0, 6, limpiar_para_pdf(f"Accionante: {r['Accionante (Nombre/Calidad)']}\nAccionado: {r['Accionado']}\nResultado: {r['Resultado']}\nMotivo: {r['Motivo']}\n" + "."*80))
            pdf.ln(2)

        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="📥 DESCARGAR REPORTE PDF", data=pdf_output, file_name="analisis_jarvis.pdf", mime="application/pdf")
