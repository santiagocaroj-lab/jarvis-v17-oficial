import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd
import io

# --- 1. CONFIGURACIÓN Y ESTILOS VISUALES ---
st.set_page_config(page_title="ECOMODA - Servidor Jurídico", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; background-color: white; color: #1a1a1a; }
    .main-title { font-size: 38px; font-weight: 700; border-left: 10px solid #ffc106; padding-left: 20px; margin-bottom: 30px; }
    
    /* --- ESTILOS DE LA PÁGINA DE BIENVENIDA --- */
    .welcome-wrapper {
        background: linear-gradient(135deg, #1a1a1a 0%, #3a3a3a 100%);
        padding: 100px 20px;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0px 10px 30px rgba(0,0,0,0.2);
        margin-top: 5vh;
        margin-bottom: 40px;
    }
    .welcome-title { font-size: 60px; font-weight: 700; color: #ffffff !important; margin-bottom: 10px; }
    .welcome-subtitle { font-size: 24px; color: #f0f0f0 !important; font-style: italic; margin-bottom: 40px; }
    .question-title { font-size: 30px; font-weight: bold; color: #ffffff !important; margin-bottom: 30px; }
    
    /* --- ESTILOS GENERALES Y BOTONES --- */
    .stButton>button { background-color: #ffc106; color: black; border: 2px solid black; font-weight: bold; width: 100%; height: 50px; }
    .stButton>button:hover { background-color: black; color: #ffc106; }
    .param-box { 
        background-color: #f8f9fa; 
        border: 2px solid #ffc106; 
        padding: 20px; 
        border-radius: 10px; 
        margin-bottom: 25px; 
        color: #000000 !important; 
    }
    .param-box b, .param-box li, .param-box ul {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CONTROL DE RUTAS (NAVEGACIÓN) E INICIALIZACIÓN DE VARIABLES ---
if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 'bienvenida'
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 0 # Clave dinámica para borrar archivos subidos

# =====================================================================
# PANTALLA 1: BIENVENIDA (ECOMODA)
# =====================================================================
if st.session_state['pagina_actual'] == 'bienvenida':
    # Agrupamos los textos en el contenedor oscuro centrado
    st.markdown("""
        <div class='welcome-wrapper'>
            <div class='welcome-title'>Bienvenido a ECOMODA</div>
            <div class='welcome-subtitle'>Tu servidor jurídico predilecto</div>
            <div class='question-title'>¿Qué haremos hoy?</div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Ir a 'Garzón'"):
            st.session_state['pagina_actual'] = 'login'
            st.rerun()
    st.stop()

# =====================================================================
# PANTALLA 2: SISTEMA DE SEGURIDAD (FIREWALL)
# =====================================================================
if st.session_state['pagina_actual'] == 'login':
    st.markdown("<div class='main-title'>🔒 ACCESO RESTRINGIDO GARZÓN</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("Por favor, identifícate para acceder al motor de análisis.")
        clave = st.text_input("Ingrese la clave de seguridad:", type="password")
        
        if st.button("INGRESAR"):
            if clave == "Juan007":
                st.session_state['auth'] = True
                st.session_state['pagina_actual'] = 'app_garzon'
                st.rerun()
            else:
                st.error("Acceso denegado. Clave incorrecta.")
        
        st.write("") 
        if st.button("🔙 Volver al inicio"):
            st.session_state['pagina_actual'] = 'bienvenida'
            st.rerun()
            
    st.stop()


# =====================================================================
# PANTALLA 3: APLICACIÓN PRINCIPAL GARZÓN
# =====================================================================
if st.session_state['pagina_actual'] == 'app_garzon' and st.session_state['auth']:
    
    # --- MOTOR DE EXTRACCIÓN JURÍDICO ---
    def motor_juridico_final(pdf_file):
        texto_acumulado = ""
        try:
            pdf_file.seek(0)
            reader = PyPDF2.PdfReader(pdf_file)
            for i in range(min(10, len(reader.pages))):
                texto_acumulado += reader.pages[i].extract_text() + " \n "
        except Exception as e:
            return {"accionante": "ERROR_LECTURA", "calidad": "ERROR", "accionado": "ERROR_LECTURA"}

        texto_limpio = re.sub(r'\s+', ' ', texto_acumulado)

        # A. EXTRACCIÓN ACCIONANTE
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

        # B. EXTRACCIÓN ACCIONADO
        accionado = "NO IDENTIFICADO"
        patrones_ado = [
            r"(?:Accionado|Demandado|Entidad accionada)[s]?\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})(?=\s*-\s*|\s+Magistrado|\s+Tema|\s+Procedencia|Expediente)",
            r"(?:instaurada|promovida|interpuesta|presentada|formulada)\s+por\s+(?:[A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60}?)\s+(?:contra|en contra de|frente a)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_-]{4,90}?)(?=\.|\,|\n| para | a fin de | por presunta | solicitando| mediante| \(en adelante)",
            r"(?:tutela|amparo|demanda)(?:[^\.]{0,50}?)(?:contra|en contra de|frente a)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_-]{4,90}?)(?=\.|\,|\n| para | a fin de | por presunta | solicitando| mediante| \(en adelante)"
        ]
        for p in patrones_ado:
            m = re.search(p, texto_limpio, re.IGNORECASE)
            if m:
                cand = m.group(1).strip().upper()
                if not any(b in cand for b in ["PROVIDENCIA", "SENTENCIA", "FALLO", "DECISION", "RESOLUCION", "TUTELA", "DERECHO", "VIDA", "INTEGRIDAD", "SALUD", "RIESGO", "LIBERTAD", "IGUALDAD"]):
                    cand = re.sub(r'\s*\([A-Z0-9]+\)$', '', cand).strip()
                    accionado = cand
                    break
                    
        if "UNIDAD NACIONAL DE PROTECC" in accionado or re.search(r"\bUNP\b", accionado):
            accionado = "UNIDAD NACIONAL DE PROTECCION (UNP)"
        elif "FISCALIA" in accionado or "NACION" in accionado:
            if "FISCAL" in accionado: accionado = "FISCALIA GENERAL DE LA NACION"

        # C. EXTRACCIÓN CALIDAD
        calidad = "NO IDENTIFICADA (CIVIL)"
        poblaciones_clave = r"(periodista|comunicador|reportero|líder social|lideresa social|defensor de derechos|defensora de derechos|abogado|abogada|firmante de paz|indígena|campesino|desplazado|docente)"
        
        patrones_condicion = [
            rf"(?:calidad de|condición de|desempeña como|ejerce como|profesión de|profesión como|es|su labor como)\s+{poblaciones_clave}",
            rf"{poblaciones_clave}\s+(?:amenazado|amenazada|de profesión|independiente|de la emisora|del canal|de la región)"
        ]
        for p in patrones_condicion:
            m = re.search(p, texto_limpio, re.IGNORECASE)
            if m:
                calidad = m.group(1).strip().upper()
                break
                
        if calidad == "NO IDENTIFICADA (CIVIL)" and accionante != "NO IDENTIFICADO":
            primer_nombre = accionante.split()[0]
            patron_proximidad = rf"{re.escape(primer_nombre)}.{'{0,150}'}{poblaciones_clave}"
            m_prox = re.search(patron_proximidad, texto_limpio, re.IGNORECASE | re.DOTALL)
            if m_prox:
                calidad = m_prox.group(1).strip().upper()
                
        if calidad in ["COMUNICADOR", "REPORTERO"]: calidad = "PERIODISTA"
        if calidad in ["LIDERESA SOCIAL"]: calidad = "LÍDER SOCIAL"
                    
        return {"accionante": accionante, "calidad": calidad, "accionado": accionado}

    # --- INTERFAZ DE GARZÓN ---
    st.markdown("<div class='main-title'>GARZÓN - INGENIERÍA EN REVERSA JURISPRUDENCIAL</div>", unsafe_allow_html=True)
    
    if st.button("🚪 Cerrar Sesión / Volver a ECOMODA"):
        st.session_state['auth'] = False
        st.session_state['pagina_actual'] = 'bienvenida'
        st.rerun()

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.subheader("⚙️ 1. Sentencia Arquimédica (Base)")
        file_arq = st.file_uploader("Sube el PDF de la sentencia más reciente", type="pdf", key=f"arq_{st.session_state['uploader_key']}")
        st.info("Garzón leerá este documento para deducir orgánicamente la 'Entidad Accionada' y la 'Calidad' que servirán de regla estricta.")

    with col2:
        st.subheader("📂 2. Sentencias a Filtrar")
        files_comp = st.file_uploader("Sube las sentencias citadas (para incluir/excluir)", type="pdf", accept_multiple_files=True, key=f"masivo_{st.session_state['uploader_key']}")

    if 'analisis_terminado' not in st.session_state:
        st.session_state['analisis_terminado'] = False
        st.session_state['resultados_df'] = None
        st.session_state['pdf_binario'] = None
        st.session_state['html_parametros'] = ""

    # Botones de Acción (Ejecutar y Limpiar)
    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn2:
        if st.button("🧹 LIMPIAR DATOS (Empezar de nuevo)"):
            st.session_state['analisis_terminado'] = False
            st.session_state['resultados_df'] = None
            st.session_state['pdf_binario'] = None
            st.session_state['html_parametros'] = ""
            st.session_state['uploader_key'] += 1 # Cambiar la key borra los archivos subidos
            st.rerun()

    with col_btn1:
        ejecutar = st.button("🚀 EJECUTAR ANÁLISIS")

    if ejecutar:
        if not file_arq:
            st.error("Falta la Sentencia Arquimédica. Es obligatoria para establecer los parámetros base.")
        elif not files_comp:
            st.warning("Sube al menos un PDF en la sección de sentencias a filtrar.")
        else:
            with st.spinner("Garzón está leyendo y analizando profundamente los expedientes..."):
                
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

                resultados = []
                
                for f in files_comp:
                    info = motor_juridico_final(f)
                    fallos = []
                    
                    if info["calidad"] != ext_base["calidad"]:
                        fallos.append(f"Calidad difiere (Encontró '{info['calidad']}')")
                    
                    acc_base = ext_base["accionado"].replace("UNP", "").strip()
                    acc_comp = info["accionado"].replace("UNP", "").strip()
                    
                    coincidencia_accionado = False
                    if len(acc_base) > 4 and len(acc_comp) > 4:
                        if acc_base in acc_comp or acc_comp in acc_base:
                            coincidencia_accionado = True
                    
                    if "UNP" in ext_base["accionado"] and "UNP" in info["accionado"]:
                        coincidencia_accionado = True
                        
                    if not coincidencia_accionado:
                        fallos.append(f"Accionado difiere ('{info['accionado'][:25]}...')")
                    
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

    if st.session_state['analisis_terminado']:
        st.markdown(st.session_state['html_parametros'], unsafe_allow_html=True)
        st.table(st.session_state['resultados_df'])
        
        st.download_button(
            label="📥 DESCARGAR REPORTE TÉCNICO EN PDF", 
            data=st.session_state['pdf_binario'], 
            file_name="reporte_linea_jurisprudencial.pdf",
            mime="application/pdf"
        )
