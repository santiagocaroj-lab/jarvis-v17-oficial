import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="JARVIS v17.3 - PRO", layout="wide")

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

# --- FUNCIONES TÉCNICAS REFORZADAS ---
def limpiar_para_pdf(texto):
    if not texto: return ""
    reemplazos = {'á':'a','é':'e','í':'i','ó':'o','ú':'u','Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U','ñ':'n','Ñ':'N'}
    for orig, new in reemplazos.items():
        texto = texto.replace(orig, new)
    return texto.encode('ascii', 'ignore').decode('ascii')

def analizar_texto_avanzado(texto):
    t = texto.upper()
    # Identificación de Calidad
    calidad = "civil"
    if any(k in t for k in ["PERIODISTA", "PRENSA", "RADIO", "COMUNICADOR", "REPORTERO", "NOTICIERO"]):
        calidad = "periodista"
    
    # Identificación de Accionado (Multi-Patrón)
    accionado = "NO IDENTIFICADO"
    patrones = [
        r"(?:ACCIONADO|CONTRA|DEMANDADO|DIRIGIDA CONTRA|EN CONTRA DE)\s*[:\-]?\s*([A-ZÁÉÍÓÚÑ\s\.]{3,70})(?=\s|INSTAURÓ|ANTE|POR|DERECHOS)",
        r"(?:SENTENCIA\s+DE\s+TUTELA\s+DE\s+.*?\s+CONTRA\s+)([A-ZÁÉÍÓÚÑ\s\.]{3,70})",
        r"(?:NOTIFÍQUESE\s+A\s+)([A-ZÁÉÍÓÚÑ\s\.]{3,70})",
        r"(?:DEMANDADA\s*:\s*)([A-ZÁÉÍÓÚÑ\s\.]{3,70})"
    ]
    
    for p in patrones:
        match = re.search(p, t)
        if match:
            posible = match.group(1).strip()
            # Limpieza de conectores finales
            posible = re.split(r'\s(Y|PARA|QUE|EL|LA|EN)\s', posible)[0]
            if len(posible) > 3:
                accionado = posible
                break
                
    return {"calidad": calidad, "accionado": accionado}

# --- INTERFAZ ---
st.markdown("<div class='main-title'>JARVIS JURÍDICO v17.3</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📁 Parámetros de Inclusión")
    file_arq = st.file_uploader("1. Cargar Sentencia Arquimédica", type="pdf")
    st.write("---")
    st.write("✍️ **Entrada Manual (Facultativo)**")
    m_calidad = st.selectbox("Calidad del accionante", ["Periodista", "Civil"])
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
        # 1. Procesar la Arquimédica
        base = {"calidad": m_calidad.lower(), "accionado": m_accionado.upper()}
        nombre_arq = "Manual"
        
        if file_arq:
            nombre_arq = file_arq.name
            t_base = PyPDF2.PdfReader(file_arq).pages[0].extract_text()
            extraido_base = analizar_texto_avanzado(t_base)
            if not m_accionado: base["accionado"] = extraido_base["accionado"]
            # Si el usuario no tocó el selector, usamos lo que diga el PDF
            if m_calidad == "Civil": base["calidad"] = extraido_base["calidad"]

        # 2. Iniciar lista de resultados con la Arquimédica como referencia
        resultados_tabla = [{
            "Sentencia": f"⭐ {nombre_arq}",
            "Accionado": base["accionado"],
            "Calidad": base["calidad"],
            "Resultado": "PARÁMETROS",
            "Motivo": "Sentencia Base"
        }]

        # 3. Procesar Comparativas
        for f in files_comp:
            try:
                t_f = PyPDF2.PdfReader(f).pages[0].extract_text()
                info_f = analizar_texto_avanzado(t_f)
                
                razones = []
                if info_f["calidad"] != base["calidad"]: 
                    razones.append(f"Calidad: {info_f['calidad']}")
                
                # Comparación de accionado (Sustancial: primeras 6 letras)
                if base["accionado"][:6] not in info_f["accionado"]: 
                    razones.append("Accionado diferente")
                
                es_ok = len(razones) == 0
                resultados_tabla.append({
                    "Sentencia": f.name,
                    "Accionado": info_f["accionado"],
                    "Calidad": info_f["calidad"],
                    "Resultado": "✅ INCLUIDA" if es_ok else "❌ EXCLUIDA",
                    "Motivo": ", ".join(razones) if razones else "Coincidencia"
                })
            except:
                resultados_tabla.append({"Sentencia": f.name, "Resultado": "ERROR", "Motivo": "Archivo ilegible"})

        # --- MOSTRAR TABLA ---
        st.markdown("---")
        st.markdown("### 📊 TABLA DE ANÁLISIS COMPARATIVO")
        st.table(pd.DataFrame(resultados_tabla))

        # --- GENERACIÓN DE PDF SEGURO ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "REPORTE DE INVESTIGACION - JARVIS", 0, 1, 'C')
        pdf.ln(5)
        
        for r in resultados_tabla:
            pdf.set_fill_color(255, 193, 6) if "INCLUIDA" in r["Resultado"] else pdf.set_fill_color(240, 240, 240)
            if r["Resultado"] == "PARÁMETROS": pdf.set_fill_color(200, 200, 255)
            
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(0, 8, limpiar_para_pdf(f"Documento: {r['Sentencia']}"), 1, 1, 'L', True)
            pdf.set_font("Arial", '', 9)
            pdf.multi_cell(0, 6, limpiar_para_pdf(f"Estado: {r['Resultado']}\nAccionado: {r['Accionado']}\nCalidad: {r['Calidad']}\nMotivo: {r['Motivo']}\n" + "-"*80))
            pdf.ln(2)

        pdf_output = pdf.output(dest='S').encode('latin-1')
        st.download_button(label="📥 DESCARGAR REPORTE FORMAL (PDF)", data=pdf_output, file_name="analisis_jarvis.pdf", mime="application/pdf")
