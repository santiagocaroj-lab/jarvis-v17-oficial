import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd
import io

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="JARVIS v17.1 - PRO", layout="wide")

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
    /* Estilo para la tabla */
    .stDataFrame {
        border: 1px solid #ffc106;
        border-radius: 10px;
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

# --- FUNCIONES TÉCNICAS ---
def analizar_texto(texto):
    texto_up = texto.upper()
    calidad = "periodista" if any(k in texto_up for k in ["PERIODISTA", "PRENSA", "RADIO", "COMUNICADOR", "REPORTERO"]) else "civil"
    
    match = re.search(r"(ACCIONADO|CONTRA|EN CONTRA DE)\s*:\s*([A-ZÁÉÍÓÚÑ\s]{3,60})", texto_up)
    accionado = match.group(2).strip() if match else "NO IDENTIFICADO"
    return {"calidad": calidad, "accionado": accionado}

# --- INTERFAZ ---
st.markdown("<div class='main-title'>JARVIS JURÍDICO v17.1</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("📁 Parámetros de Inclusión")
    file_arq = st.file_uploader("1. Cargar Sentencia Arquimédica", type="pdf")
    
    st.write("---")
    st.write("✍️ **Entrada Manual (Facultativo)**")
    # Corregido: Solo Periodista o Civil
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
        # Definir Base de comparación
        base = {"calidad": m_calidad.lower(), "accionado": m_accionado.upper()}
        
        if file_arq:
            try:
                lector_arq = PyPDF2.PdfReader(file_arq)
                t_base = lector_arq.pages[0].extract_text()
                extraido = analizar_texto(t_base)
                if not m_accionado: base["accionado"] = extraido["accionado"]
                # Si el usuario no cambió el selectbox (asumimos Periodista por defecto), 
                # pero el PDF dice Civil, podríamos dejar que el PDF mande si no hubo interacción manual clara.
            except:
                st.error("Error al leer la sentencia arquimédica.")

        # Procesar comparativas para la tabla
        resultados_tabla = []
        relevantes_lista = []

        for f in files_comp:
            try:
                lector_f = PyPDF2.PdfReader(f)
                t_f = lector_f.pages[0].extract_text()
                info_f = analizar_texto(t_f)
                
                # Lógica de comparación
                razones = []
                if info_f["calidad"] != base["calidad"]: 
                    razones.append(f"Calidad distinta ({info_f['calidad']})")
                
                # Comparación flexible del accionado (primeras 5 letras)
                if base["accionado"][:5] not in info_f["accionado"]: 
                    razones.append("Accionado diferente")
                
                es_relevante = len(razones) == 0
                estado = "✅ INCLUIDA" if es_relevante else "❌ EXCLUIDA"
                
                resultados_tabla.append({
                    "Sentencia": f.name,
                    "Accionado Detectado": info_f["accionado"],
                    "Calidad": info_f["calidad"],
                    "Resultado": estado,
                    "Motivo": ", ".join(razones) if razones else "Cumple criterios"
                })
                
                if es_relevante: relevantes_lista.append(f.name)
            except:
                resultados_tabla.append({"Sentencia": f.name, "Resultado": "ERROR", "Motivo": "Archivo ilegible"})

        # --- MOSTRAR RESULTADOS EN PANTALLA ---
        st.markdown("---")
        st.markdown("### 📊 TABLA DE ANÁLISIS RESULTANTE")
        
        # Crear DataFrame para la tabla
        df = pd.DataFrame(resultados_tabla)
        st.table(df) # Muestra la tabla con el diseño de la página

        st.success(f"Se analizaron {len(files_comp)} documentos. Sentencias relevantes: {', '.join(relevantes_lista) if relevantes_lista else 'Ninguna'}")

        # --- OPCIÓN DE DESCARGA PDF (CON FORMATO TABLA) ---
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "REPORTE DE INVESTIGACION - JARVIS JURIDICO", 0, 1, 'C')
        pdf.set_font("Arial", '', 10)
        pdf.ln(5)
        
        for r in resultados_tabla:
            pdf.set_fill_color(255, 193, 6) if "INCLUIDA" in r["Resultado"] else pdf.set_fill_color(240, 240, 240)
            pdf.cell(0, 8, f"Documento: {r['Sentencia']}", 1, 1, 'L', True)
            pdf.multi_cell(0, 6, f"Estado: {r['Resultado']}\nDetalle: {r['Motivo']}\nAccionado: {r['Accionado Detectado']}\n" + "."*80)
            pdf.ln(2)

        pdf_output = pdf.output(dest='S').encode('latin-1', 'ignore')
        st.download_button(
            label="📥 DESCARGAR REPORTE FORMAL (PDF)",
            data=pdf_output,
            file_name="analisis_semillero.pdf",
            mime="application/pdf"
        )
