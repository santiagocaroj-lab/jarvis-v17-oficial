import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd
import io

# --- 1. CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="GARZÓN - Análisis Jurisprudencial", layout="wide")

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

# --- 3. MOTOR DE EXTRACCIÓN JURÍDICO (NLP AVANZADO MEJORADO) ---
def motor_juridico_final(pdf_file):
    texto_acumulado = ""
    try:
        pdf_file.seek(0) # Reinicia el cursor de lectura del PDF en memoria
        reader = PyPDF2.PdfReader(pdf_file)
        # Ampliamos a 8 páginas por si los antecedentes son largos
        for i in range(min(8, len(reader.pages))):
            texto_acumulado += reader.pages[i].extract_text() + " \n "
    except Exception as e:
        return {"accionante": "ERROR_LECTURA", "calidad": "ERROR", "accionado": "ERROR_LECTURA"}

    # Aplanar el texto para evitar que los saltos de línea rompan las expresiones regulares
    texto_limpio = re.sub(r'\s+', ' ', texto_acumulado)

    # --- A. EXTRACCIÓN DEL ACCIONANTE ---
    accionante = "NO IDENTIFICADO"
    patrones_acc = [
        r"(?:Accionante|Demandante|Actor)[s]?\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60})(?=\s*-\s*|\s+Accionado|\s+Demandado|C\.C\.|Cédula|Nit|Expediente)",
        # Agregamos "presentada", vital para la redacción reciente de la Corte Constitucional
        r"(?:instaurada|promovida|interpuesta|presentada)\s+por\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60})\s+(?:contra|en contra de|frente a)",
        # Captura directa del inicio de los antecedentes
        r"(?:El señor|La señora|El ciudadano|La ciudadana)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60})\s+(?:presentó|instauró|interpuso|promovió)"
    ]
    
    for p in patrones_acc:
        m = re.search(p, texto_limpio, re.IGNORECASE)
        if m:
            cand = m.group(1).strip().upper()
            # Lista negra para no capturar magistrados ni frases procesales
            if not any(b in cand for b in ["MAGISTRAD", "SALA", "CORTE", "JUEZ", "REVISION"]):
                accionante = cand
                break

    # --- B. EXTRACCIÓN DEL ACCIONADO (Con Resolución de Alias y Paréntesis) ---
    accionado = "NO IDENTIFICADO"
    patrones_ado = [
        r"(?:Accionado|Demandado|Entidad accionada)[s]?\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})(?=\s*-\s*|\s+Magistrado|\s+Tema|\s+Procedencia|Expediente)",
        # Añadimos soporte para leer paréntesis como "(UNP)" y cortes precisos
        r"(?:contra|en contra de)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)]{4,80}?)(?=\.|\,|\n| para | a fin de | por presunta | solicitando| mediante| \(en adelante)"
    ]
    
    for p in patrones_ado:
        m = re.search(p, texto_limpio, re.IGNORECASE)
        if m:
            cand = m.group(1).strip().upper()
            if not any(b in cand for b in ["PROVIDENCIA", "SENTENCIA", "FALLO", "DECISION", "RESOLUCION", "TUTELA"]):
                # Limpiamos paréntesis sueltos al final por si el regex cortó mal
                accionado = cand.replace(" (UNP)", "").replace("(UNP)", "").strip()
                break
    
    # Estandarización de Alias Críticos (UNP, Fiscalía)
    if "UNIDAD NACIONAL DE PROTECC" in accionado or re.search(r"\bUNP\b", accionado):
        accionado = "UNIDAD NACIONAL DE PROTECCION (UNP)"
    elif "FISCALIA" in accionado or "NACION" in accionado:
        if "FISCAL" in accionado: accionado = "FISCALIA GENERAL DE LA NACION"

    # --- C. EXTRACCIÓN DE LA CALIDAD (Búsqueda Relacional Estricta) ---
    calidad = "OTRA (CIVIL/ETC)"
    profesiones = r"(periodista|comunicador|reportero|líder social|defensor de derechos|abogado|firmante de paz|indígena)"
    
    # 1. Búsqueda por condición explícita ampliada
    patrones_condicion = [
        # Agregamos "es", "profesión de" y "profesión como" que usan las sentencias T-038 y T-040
        rf"(?:calidad de|condición de|desempeña como|ejerce como|profesión de|profesión como|es)\s+{profesiones}",
        rf"{profesiones}\s+(?:amenazado|amenazada|de profesión|independiente|de la emisora|del canal)"
    ]
    
    for p in patrones_condicion:
        m = re.search(p, texto_limpio, re.IGNORECASE)
        if m:
            calidad = m.group(1).strip().upper()
            break
            
    # 2. Búsqueda de proximidad (Si no funcionó la explícita)
    if calidad == "OTRA (CIVIL/ETC)" and accionante != "NO IDENTIFICADO":
        primer_nombre = accionante.split()[0]
        # Busca la profesión a un máximo de 150 caracteres del primer nombre del accionante
        patron_proximidad = rf"{re.escape(primer_nombre)}.{'{0,150}'}{profesiones}"
        m_prox = re.search(patron_proximidad, texto_limpio, re.IGNORECASE | re.DOTALL)
        if m_prox:
            calidad = m_prox.group(1).strip().upper()
            
    # Estandarizamos sinónimos
    if calidad in ["COMUNICADOR", "REPORTERO"]:
        calidad = "PERIODISTA"
    elif "LÍDER SOCIAL" in calidad or "LIDER SOCIAL" in calidad:
        calidad = "LÍDER SOCIAL"
                
    return {"accionante": accionante, "calidad": calidad, "accionado": accionado}

# --- 4. INTERFAZ GRÁFICA Y CONTROL DE ESTADO ---
st.markdown("<div class='main-title'>GARZÓN - INGENIERÍA EN REVERSA JURISPRUDENCIAL</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("⚙️ 1. Sentencia Arquimédica (Base)")
    file_arq = st.file_uploader("Sube el PDF de la sentencia más reciente", type="pdf", key="arq")
    st.info("Garzón extraerá la Entidad Accionada y la Calidad de este documento para establecer los criterios de inclusión absolutos.")

with col2:
    st.subheader("📂 2. Sentencias a Filtrar")
    files_comp = st.file_uploader("Sube las sentencias citadas (para incluir/excluir)", type="pdf", accept_multiple_files=True, key="masivo")

# Inicialización del estado de sesión para retener resultados
if 'analisis_terminado' not in st.session_state:
    st.session_state['analisis_terminado'] = False
    st.session_state['resultados_df'] = None
    st.session_state['pdf_binario'] = None
    st.session_state['html_parametros'] = ""

if st.button("🚀 EJECUTAR ANÁLISIS"):
    if not file_arq:
        st.error("Falta la Sentencia Arquimédica. Es obligatoria para establecer el patrón.")
    elif not files_comp:
        st.warning("Sube al menos un PDF en la sección de sentencias a filtrar.")
    else:
        with st.spinner("Garzón está analizando las estructuras procesales..."):
            
            # --- FASE 1: Extraer parámetros maestros de la Arquimédica ---
            ext_base = motor_juridico_final(file_arq)
            
            st.session_state['html_parametros'] = f"""
            <div class="param-box">
                <b>PARÁMETROS ESTRICTOS (SENTENCIA ARQUIMÉDICA):</b><br>
                <ul>
                    <li><b>Calidad Exigida:</b> {ext_base['calidad']}</li>
                    <li><b>Entidad Accionada Exigida:</b> {ext_base['accionado']}</li>
                    <li><i>Accionante Base Registrado: {ext_base['accionante']} (No usado para excluir)</i></li>
                </ul>
            </div>
            """

            # --- FASE 2: Analizar y comparar archivos masivos ---
            resultados = []
            
            for f in files_comp:
                info = motor_juridico_final(f)
                fallos = []
                
                # Criterio 1: La calidad debe ser exactamente la misma
                if info["calidad"] != ext_base["calidad"]:
                    fallos.append(f"Calidad difiere (Es {info['calidad']})")
                
                # Criterio 2: El accionado debe coincidir (Búsqueda cruzada para perdonar recortes de texto)
                # Si ninguno de los dos strings contiene al otro, entonces son diferentes.
                if ext_base["accionado"] not in info["accionado"] and info["accionado"] not in ext_base["accionado"]:
                    fallos.append(f"Accionado difiere ({info['accionado'][:20]}...)")
                
                estado = "✅ INCLUIDA" if not fallos else "❌ EXCLUIDA"
                resultados.append({
                    "Archivo": f.name,
                    "Accionante Encontrado": info['accionante'],
                    "Calidad Detectada": info['calidad'],
                    "Accionado Detectado": info["accionado"],
                    "Veredicto": estado,
                    "Motivo": ", ".join(fallos) if fallos else "Cumple ambos criterios"
                })
            
            st.session_state['resultados_df'] = pd.DataFrame(resultados)

            # --- FASE 3: Generación del Reporte PDF ---
            def safe_pdf(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 10, "REPORTE DE INGENIERIA EN REVERSA - GARZON", 0, 1, 'C')
            pdf.set_font("Arial", '', 10)
            pdf.ln(5)
            pdf.multi_cell(0, 7, safe_pdf(f"PARAMETROS DE EXCLUSION:\nCalidad Exigida: {ext_base['calidad']}\nAccionado Exigido: {ext_base['accionado']}\n" + "="*50))
            
            for r in resultados:
                if "INCLUIDA" in r["Veredicto"]:
                    pdf.set_fill_color(220, 255, 220) # Verde
                else:
                    pdf.set_fill_color(255, 220, 220) # Rojo
                pdf.cell(0, 8, safe_pdf(f"Documento: {r['Archivo']}"), 1, 1, 'L', True)
                pdf.multi_cell(0, 6, safe_pdf(f"Accionante: {r['Accionante Encontrado']}\nCalidad: {r['Calidad Detectada']}\nAccionado: {r['Accionado Detectado']}\nVEREDICTO: {r['Veredicto']}\nRazon: {r['Motivo']}\n" + "-"*80))
                pdf.ln(2)

            try:
                st.session_state['pdf_binario'] = pdf.output(dest='S').encode('latin-1')
            except AttributeError:
                st.session_state['pdf_binario'] = bytes(pdf.output())

            # Guardamos el estado exitoso
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
