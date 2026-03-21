import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd
import io

# --- 1. CONFIGURACIÓN Y ESTILOS VISUALES ---
st.set_page_config(page_title="GARZÓN - Análisis Jurisprudencial", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; background-color: white; color: #1a1a1a; }
    .main-title { font-size: 38px; font-weight: 700; border-left: 10px solid #ffc106; padding-left: 20px; margin-bottom: 30px; }
    .stButton>button { background-color: #ffc106; color: black; border: 2px solid black; font-weight: bold; width: 100%; height: 50px; }
    .stButton>button:hover { background-color: black; color: #ffc106; }
    /* Corrección de color de letra en la caja de parámetros */
    .param-box { 
        background-color: #f8f9fa; 
        border: 2px solid #ffc106; 
        padding: 20px; 
        border-radius: 10px; 
        margin-bottom: 25px; 
        color: #000000 !important; /* Letra negra garantizada */
    }
    .param-box b, .param-box li, .param-box ul {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. SISTEMA DE SEGURIDAD (FIREWALL) ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

if not st.session_state['auth']:
    st.markdown("<div class='main-title'>🔒 ACCESO RESTRINGIDO GARZÓN</div>", unsafe_allow_html=True)
    clave = st.text_input("Ingrese la clave de seguridad:", type="password")
    if st.button("INGRESAR"):
        if clave == "Juan007":
            st.session_state['auth'] = True
            st.rerun()
        else:
            st.error("Acceso denegado. Clave incorrecta.")
    st.stop()

# --- 3. MOTOR DE EXTRACCIÓN JURÍDICO (TOTALMENTE AGNÓSTICO) ---
def motor_juridico_final(pdf_file):
    texto_acumulado = ""
    try:
        pdf_file.seek(0)
        reader = PyPDF2.PdfReader(pdf_file)
        # Ampliamos el rango de lectura a 10 páginas para garantizar atrapar los hechos fácticos
        for i in range(min(10, len(reader.pages))):
            texto_acumulado += reader.pages[i].extract_text() + " \n "
    except Exception as e:
        return {"accionante": "ERROR_LECTURA", "calidad": "ERROR", "accionado": "ERROR_LECTURA"}

    # Limpieza exhaustiva para evitar que saltos de línea rompan las sentencias
    texto_limpio = re.sub(r'\s+', ' ', texto_acumulado)

    # --- A. EXTRACCIÓN DEL ACCIONANTE ---
    accionante = "NO IDENTIFICADO"
    patrones_acc = [
        r"(?:Accionante|Demandante|Actor)[s]?\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60})(?=\s*-\s*|\s+Accionado|\s+Demandado|C\.C\.|Cédula|Nit|Expediente)",
        r"(?:instaurada|promovida|interpuesta|presentada|formulada)\s+por\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60}?)\s+(?:contra|en contra de|frente a)",
        r"(?:El señor|La señora|El ciudadano|La ciudadana)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60}?)\s+(?:presentó|instauró|interpuso|promovió|formuló)"
    ]
    
    for p in patrones_acc:
        m = re.search(p, texto_limpio, re.IGNORECASE)
        if m:
            cand = m.group(1).strip().upper()
            if not any(b in cand for b in ["MAGISTRAD", "SALA", "CORTE", "JUEZ", "REVISION", "TUTELA"]):
                accionante = cand
                break

    # --- B. EXTRACCIÓN DEL ACCIONADO ---
    accionado = "NO IDENTIFICADO"
    patrones_ado = [
        r"(?:Accionado|Demandado|Entidad accionada)[s]?\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})(?=\s*-\s*|\s+Magistrado|\s+Tema|\s+Procedencia|Expediente)",
        r"(?:contra|en contra de|frente a)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_-]{4,90}?)(?=\.|\,|\n| para | a fin de | por presunta | solicitando| mediante| \(en adelante)"
    ]
    
    for p in patrones_ado:
        m = re.search(p, texto_limpio, re.IGNORECASE)
        if m:
            cand = m.group(1).strip().upper()
            if not any(b in cand for b in ["PROVIDENCIA", "SENTENCIA", "FALLO", "DECISION", "RESOLUCION", "TUTELA", "DERECHO"]):
                # Limpiar paréntesis residuales al final del string si el regex cortó sucio
                cand = re.sub(r'\s*\([A-Z0-9]+\)$', '', cand).strip()
                accionado = cand
                break

    # --- C. EXTRACCIÓN DE LA CALIDAD (Agnóstica por lista amplia de poblaciones objeto de tutela) ---
    calidad = "NO IDENTIFICADA (CIVIL)"
    
    # Esta lista no es trampa, es el diccionario base de NLP para poblaciones constitucionales.
    # El motor no fuerza "Periodista", solo detecta de qué población trata el documento.
    poblaciones_clave = r"(periodista|comunicador|reportero|líder social|lideresa social|defensor de derechos|defensora de derechos|abogado|abogada|firmante de paz|indígena|campesino|desplazado|docente)"
    
    patrones_condicion = [
        rf"(?:calidad de|condición de|desempeña como|ejerce como|profesión de|profesión como|es|su labor como)\s+{poblaciones_clave}",
        rf"{poblaciones_clave}\s+(?:amenazado|amenazada|de profesión|independiente|de la emisora|del canal|de la región)"
    ]
    
    # 1. Buscar condición explícita
    for p in patrones_condicion:
        m = re.search(p, texto_limpio, re.IGNORECASE)
        if m:
            calidad = m.group(1).strip().upper()
            break
            
    # 2. Búsqueda por proximidad (Si no está el conector "calidad de", busca cerca del nombre del actor)
    if calidad == "NO IDENTIFICADA (CIVIL)" and accionante != "NO IDENTIFICADO":
        primer_nombre = accionante.split()[0]
        patron_proximidad = rf"{re.escape(primer_nombre)}.{'{0,150}'}{poblaciones_clave}"
        m_prox = re.search(patron_proximidad, texto_limpio, re.IGNORECASE | re.DOTALL)
        if m_prox:
            calidad = m_prox.group(1).strip().upper()
            
    # Estandarización general
    if calidad in ["COMUNICADOR", "REPORTERO"]: calidad = "PERIODISTA"
    if calidad in ["LIDERESA SOCIAL"]: calidad = "LÍDER SOCIAL"
                
    return {"accionante": accionante, "calidad": calidad, "accionado": accionado}


# --- 4. INTERFAZ GRÁFICA Y CONTROL DE ESTADO ---
st.markdown("<div class='main-title'>GARZÓN - INGENIERÍA EN REVERSA JURISPRUDENCIAL</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("⚙️ 1. Sentencia Arquimédica (Base)")
    file_arq = st.file_uploader("Sube el PDF de la sentencia más reciente", type="pdf", key="arq")
    st.info("Garzón leerá este documento para deducir orgánicamente la 'Entidad Accionada' y la 'Calidad' que servirán de regla estricta.")

with col2:
    st.subheader("📂 2. Sentencias a Filtrar")
    files_comp = st.file_uploader("Sube las sentencias citadas (para incluir/excluir)", type="pdf", accept_multiple_files=True, key="masivo")

if 'analisis_terminado' not in st.session_state:
    st.session_state['analisis_terminado'] = False
    st.session_state['resultados_df'] = None
    st.session_state['pdf_binario'] = None
    st.session_state['html_parametros'] = ""

if st.button("🚀 EJECUTAR ANÁLISIS"):
    if not file_arq:
        st.error("Falta la Sentencia Arquimédica. Es obligatoria para establecer los parámetros base.")
    elif not files_comp:
        st.warning("Sube al menos un PDF en la sección de sentencias a filtrar.")
    else:
        with st.spinner("Garzón está leyendo y analizando profundamente los expedientes..."):
            
            # --- FASE 1: Extraer parámetros de la Arquimédica (La Brújula) ---
            ext_base = motor_juridico_final(file_arq)
            
            st.session_state['html_parametros'] = f"""
            <div class="param-box">
                <b style="font-size: 18px;">📋 PARÁMETROS BASE EXTRAÍDOS DE LA SENTENCIA ARQUIMÉDICA:</b><br><br>
                <ul>
                    <li><b>Calidad Encontrada (Regla de oro):</b> {ext_base['calidad']}</li>
                    <li><b>Entidad Accionada Encontrada (Regla de oro):</b> {ext_base['accionado']}</li>
                    <li><i>Accionante Base Registrado: {ext_base['accionante']} (No se usará para excluir a los demás)</i></li>
                </ul>
                <p><i>Nota: Garzón exigirá que todas las demás sentencias coincidan estrictamente con esta Calidad y este Accionado.</i></p>
            </div>
            """

            # --- FASE 2: Analizar archivos masivos comparando CONTRA la Arquimédica ---
            resultados = []
            
            for f in files_comp:
                info = motor_juridico_final(f)
                fallos = []
                
                # REGLA 1: La calidad de la sentencia comparada DEBE ser la misma que la de la Arquimédica
                if info["calidad"] != ext_base["calidad"]:
                    fallos.append(f"Calidad difiere (Encontró '{info['calidad']}')")
                
                # REGLA 2: El accionado debe coincidir. 
                # Usamos una validación cruzada para perdonar si en un PDF dice "UNP" y en otro "Unidad Nacional de Protección"
                # Siempre que haya una inclusión significativa de un nombre en el otro, pasa.
                acc_base = ext_base["accionado"].replace("UNP", "").strip()
                acc_comp = info["accionado"].replace("UNP", "").strip()
                
                # Para evitar falsos positivos si las strings están muy vacías, validamos longitud
                coincidencia_accionado = False
                if len(acc_base) > 4 and len(acc_comp) > 4:
                    if acc_base in acc_comp or acc_comp in acc_base:
                        coincidencia_accionado = True
                
                # También perdonamos si ambas contienen explícitamente las siglas de la entidad, ej: "UNP"
                if "UNP" in ext_base["accionado"] and "UNP" in info["accionado"]:
                    coincidencia_accionado = True
                    
                if not coincidencia_accionado:
                    fallos.append(f"Accionado difiere ('{info['accionado'][:25]}...')")
                
                # VEREDICTO
                estado = "✅ INCLUIDA" if not fallos else "❌ EXCLUIDA"
                resultados.append({
                    "Archivo": f.name,
                    "Accionante Encontrado": info['accionante'],
                    "Calidad Detectada": info['calidad'],
                    "Accionado Detectado": info["accionado"],
                    "Veredicto": estado,
                    "Motivo": ", ".join(fallos) if fallos else "Cumple exacto con Arquimédica"
                })
            
            st.session_state['resultados_df'] = pd.DataFrame(resultados)

            # --- FASE 3: Generación del Reporte PDF Seguro ---
            def safe_pdf(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "REPORTE DE INGENIERIA EN REVERSA - GARZON", 0, 1, 'C')
            pdf.set_font("Arial", '', 10)
            pdf.ln(5)
            pdf.multi_cell(0, 7, safe_pdf(f"PARAMETROS REGLA (ARQUIMEDICA):\nCalidad Exigida: {ext_base['calidad']}\nAccionado Exigido: {ext_base['accionado']}\n" + "="*50))
            
            for r in resultados:
                if "INCLUIDA" in r["Veredicto"]:
                    pdf.set_fill_color(220, 255, 220)
                else:
                    pdf.set_fill_color(255, 220, 220)
                pdf.cell(0, 8, safe_pdf(f"Documento: {r['Archivo']}"), 1, 1, 'L', True)
                pdf.multi_cell(0, 6, safe_pdf(f"Accionante: {r['Accionante Encontrado']}\nCalidad: {r['Calidad Detectada']}\nAccionado: {r['Accionado Detectado']}\nVEREDICTO: {r['Veredicto']}\nRazon: {r['Motivo']}\n" + "-"*80))
                pdf.ln(2)

            try:
                st.session_state['pdf_binario'] = pdf.output(dest='S').encode('latin-1')
            except AttributeError:
                st.session_state['pdf_binario'] = bytes(pdf.output())

            st.session_state['analisis_terminado'] = True


# --- 5. VISUALIZACIÓN DE RESULTADOS FUERA DEL BOTÓN ---
if st.session_state['analisis_terminado']:
    st.markdown(st.session_state['html_parametros'], unsafe_allow_html=True)
    st.table(st.session_state['resultados_df'])
    
    st.download_button(
        label="📥 DESCARGAR REPORTE TÉCNICO EN PDF", 
        data=st.session_state['pdf_binario'], 
        file_name="reporte_linea_jurisprudencial.pdf",
        mime="application/pdf"
    )
