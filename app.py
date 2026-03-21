import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd
import io
import base64
import os

# --- 1. CONFIGURACIÓN Y ESTILOS VISUALES ---
st.set_page_config(page_title="ECOMODA - Servidor Jurídico", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; background-color: white; color: #1a1a1a; }
    .main-title { font-size: 38px; font-weight: 800; border-left: 10px solid #ffc106; padding-left: 20px; margin-bottom: 30px; text-transform: uppercase; }
    
    /* --- ANIMACIONES CSS (FADE IN) --- */
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(40px); }
        100% { opacity: 1; transform: translateY(0); }
    }

    /* --- ESTILOS DE PÁGINA DE BIENVENIDA --- */
    .welcome-wrapper {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); 
        padding: 60px 40px;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0px 15px 35px rgba(0,0,0,0.4);
        margin-top: 4vh;
        margin-bottom: 40px;
        border: 1px solid #334155;
        animation: fadeInUp 1.2s cubic-bezier(0.25, 1, 0.5, 1) forwards;
    }
    .ecomoda-header { 
        font-size: 16px; 
        color: #94a3b8; 
        letter-spacing: 5px; 
        font-weight: 600; 
        margin-top: 15px;
        margin-bottom: 25px; 
        text-transform: uppercase;
    }
    .welcome-title { 
        font-size: 46px; 
        font-weight: 800; 
        color: #ffc106 !important; 
        margin-bottom: 20px; 
        line-height: 1.2;
        text-transform: uppercase;
    }
    .welcome-subtitle { 
        font-size: 18px; 
        color: #f8fafc !important; 
        font-weight: 400;
        margin-bottom: 40px; 
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }
    
    /* --- BOTONES --- */
    .stButton>button { 
        background-color: #ffc106; 
        color: black; 
        border: 2px solid black; 
        font-weight: bold; 
        width: 100%; 
        height: 50px; 
        text-transform: uppercase; 
        letter-spacing: 1px; 
        transition: all 0.3s ease; 
        border-radius: 8px;
    }
    .stButton>button:hover { background-color: black; color: #ffc106; transform: scale(1.02); }
    
    .guide-button {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: transparent;
        color: #ffc106;
        border: 2px solid #ffc106;
        font-weight: bold;
        width: 100%;
        height: auto;
        padding: 12px 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        border-radius: 8px;
        text-decoration: none;
        margin-top: 15px;
        font-size: 13px;
    }
    .guide-button:hover {
        background-color: #ffc106;
        color: black;
        transform: scale(1.02);
        text-decoration: none;
    }

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

# --- 2. CONTROL DE RUTAS E INICIALIZACIÓN ---
if 'pagina_actual' not in st.session_state:
    st.session_state['pagina_actual'] = 'bienvenida'
if 'auth' not in st.session_state:
    st.session_state['auth'] = False
if 'uploader_key' not in st.session_state:
    st.session_state['uploader_key'] = 0 

# =====================================================================
# PANTALLA 1: BIENVENIDA (ECOMODA)
# =====================================================================
if st.session_state['pagina_actual'] == 'bienvenida':
    
    nombre_imagen = "Gemini_Generated_Image_ycjj93ycjj93ycjj (1).png"
    img_html = ""
    
    if os.path.exists(nombre_imagen):
        with open(nombre_imagen, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        img_html = f"<img src='data:image/png;base64,{encoded_string}' width='140' style='border-radius: 10px;'>"
    else:
        img_html = f"<p style='color: #ef4444; font-size: 12px;'>[Falta logo: {nombre_imagen}]</p>"

    st.markdown(f"""
        <div class='welcome-wrapper'>
            {img_html}
            <div class='ecomoda-header'>Ecomoda - Servidor Jurídico</div>
            <div class='welcome-title'>Análisis Jurisprudencial para Periodistas</div>
            <div class='welcome-subtitle'>
                Descubre las líneas jurisprudenciales clave de la Corte Constitucional mediante nuestro motor de inteligencia artificial <b>'Garzón'</b>.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 INGRESAR AL SISTEMA"):
            st.session_state['pagina_actual'] = 'login'
            st.rerun()
        
        st.markdown("""
            <a href='https://www.researchgate.net/publication/359064966_Linea_Jurisprudencial_en_8_simples_pasos' target='_blank' class='guide-button'>
                📖 ¿Dudas sobre la línea jurisprudencial? Aquí encontrarás una guía
            </a>
        """, unsafe_allow_html=True)
            
    st.stop()

# =====================================================================
# PANTALLA 2: FIREWALL DE SEGURIDAD
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
# PANTALLA 3: APLICACIÓN PRINCIPAL GARZÓN CON TRIPLE REDUNDANCIA AGNÓSTICA
# =====================================================================
if st.session_state['pagina_actual'] == 'app_garzon' and st.session_state['auth']:
    
    # --- MOTOR DE EXTRACCIÓN JURÍDICO (TRIPLE REDUNDANCIA) ---
    def motor_juridico_final(pdf_file):
        texto_acumulado = ""
        try:
            pdf_file.seek(0)
            reader = PyPDF2.PdfReader(pdf_file)
            for i in range(min(12, len(reader.pages))):
                texto_acumulado += reader.pages[i].extract_text() + " \n "
        except Exception as e:
            return {"accionante": "ERROR_LECTURA", "calidad": "ERROR", "accionado": "ERROR_LECTURA"}

        texto_limpio = re.sub(r'\s+', ' ', texto_acumulado)

        # ---------------------------------------------------------
        # A. EXTRACCIÓN ACCIONANTE
        # ---------------------------------------------------------
        accionante = "NO IDENTIFICADO"
        patrones_acc = [
            # Capa 1: Estricta
            r"(?:Accionante|Demandante|Actor)[s]?\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60})(?=\s*-\s*|\s+Accionado|\s+Demandado|C\.C\.|Cédula|Nit|Expediente)",
            r"(?:instaurada|promovida|interpuesta|presentada|formulada)\s+por\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60}?)\s+(?:contra|en contra de|frente a)",
            r"(?:El señor|La señora|El ciudadano|La ciudadana)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60}?)\s+(?:presentó|instauró|interpuso|promovió|formuló)",
            # Capa 2: Relajada (Redundancia)
            r"(?:Acción de tutela de|amparo propuesto por)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60}?)\s+(?:contra|en contra de)"
        ]
        for p in patrones_acc:
            m = re.search(p, texto_limpio, re.IGNORECASE)
            if m:
                cand = m.group(1).strip().upper()
                if not any(b in cand for b in ["MAGISTRAD", "SALA", "CORTE", "JUEZ", "REVISION", "TUTELA"]):
                    accionante = cand
                    break

        # ---------------------------------------------------------
        # B. EXTRACCIÓN ACCIONADO
        # ---------------------------------------------------------
        accionado = "NO IDENTIFICADO"
        patrones_ado = [
            # Capa 1: Estricta
            r"(?:Accionado|Demandado|Entidad accionada)[s]?\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,80})(?=\s*-\s*|\s+Magistrado|\s+Tema|\s+Procedencia|Expediente)",
            r"(?:instaurada|promovida|interpuesta|presentada|formulada)\s+por\s+(?:[A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60}?)\s+(?:contra|en contra de|frente a)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_-]{4,90}?)(?=\.|\,|\n| para | a fin de | por presunta | solicitando| mediante| \(en adelante)",
            r"(?:tutela|amparo|demanda)(?:[^\.]{0,50}?)(?:contra|en contra de|frente a)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_-]{4,90}?)(?=\.|\,|\n| para | a fin de | por presunta | solicitando| mediante| \(en adelante)",
            # Capa 2: Proximidad suelta (Redundancia)
            r"(?:contra|en contra de)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_-]{4,60}?)(?=\.|\,|\n|y otro|y otros)"
        ]
        
        for p in patrones_ado:
            m = re.search(p, texto_limpio, re.IGNORECASE)
            if m:
                cand = m.group(1).strip().upper()
                if not any(b in cand for b in ["PROVIDENCIA", "SENTENCIA", "FALLO", "DECISION", "RESOLUCION", "TUTELA", "DERECHO", "VIDA", "INTEGRIDAD", "SALUD", "RIESGO", "LIBERTAD", "IGUALDAD"]):
                    cand = re.sub(r'\s*\([A-Z0-9]+\)$', '', cand).strip()
                    accionado = cand
                    break
        
        # Capa 3: Salvavidas Agnóstico (Extracción de Entidad Directa sin lista predefinida)
        if accionado == "NO IDENTIFICADO":
            m_salvavidas = re.search(r"contra\s+(?:la\s+|el\s+|los\s+|las\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]{4,60}?)(?=\.|\,| a | para | y |/| en |\()", texto_limpio)
            if m_salvavidas:
                cand = m_salvavidas.group(1).strip().upper()
                if not any(b in cand for b in ["PROVIDENCIA", "SENTENCIA", "FALLO", "DECISION", "RESOLUCION", "TUTELA", "DERECHO", "VIDA", "INTEGRIDAD", "SALUD", "PETICION"]):
                    accionado = cand

        # ---------------------------------------------------------
        # C. EXTRACCIÓN CALIDAD (Totalmente Agnóstica y Estadística)
        # ---------------------------------------------------------
        calidad = "NO IDENTIFICADA (CIVIL)"
        
        poblaciones_lista = ["periodista", "comunicador", "reportero", "líder social", "lideresa social", "defensor de derechos", "defensora de derechos", "abogado", "abogada", "firmante de paz", "indígena", "campesino", "desplazado", "docente"]
        poblaciones_clave = r"(" + "|".join(poblaciones_lista) + r")"
        
        # Capa 1: Gramática Estricta
        patrones_condicion = [
            rf"(?:calidad de|condición de|desempeña como|ejerce como|profesión de|profesión como|es|su labor como)\s+{poblaciones_clave}",
            rf"{poblaciones_clave}\s+(?:amenazado|amenazada|de profesión|independiente|de la emisora|del canal|de la región)"
        ]
        for p in patrones_condicion:
            m = re.search(p, texto_limpio, re.IGNORECASE)
            if m:
                calidad = m.group(1).strip().upper()
                break
                
        # Capa 2: Proximidad al nombre
        if calidad == "NO IDENTIFICADA (CIVIL)" and accionante != "NO IDENTIFICADO":
            primer_nombre = accionante.split()[0]
            patron_proximidad = rf"{re.escape(primer_nombre)}.{'{0,150}'}{poblaciones_clave}"
            m_prox = re.search(patron_proximidad, texto_limpio, re.IGNORECASE | re.DOTALL)
            if m_prox:
                calidad = m_prox.group(1).strip().upper()
                
        # Capa 3: Salvavidas Estadístico Agnóstico (El Sonar)
        if calidad == "NO IDENTIFICADA (CIVIL)":
            conteo = {}
            for pob in poblaciones_lista:
                # Cuenta cuántas veces aparece cada profesión en las primeras 12 páginas
                conteo[pob] = len(re.findall(rf"\b{pob}\b", texto_limpio, re.IGNORECASE))
            
            # Obtiene la profesión que más se repite
            if conteo:
                max_pob = max(conteo, key=conteo.get)
                # Si se menciona 3 o más veces, la IA asume por estadística que esa es la calidad
                if conteo[max_pob] >= 3:
                    calidad = max_pob.upper()
                
        # Normalización Semántica Final (Para no fallar si dice "reportero" vs "periodista")
        if calidad in ["COMUNICADOR", "REPORTERO"]: calidad = "PERIODISTA"
        if calidad in ["LIDERESA SOCIAL", "DEFENSORA DE DERECHOS", "DEFENSOR DE DERECHOS"]: calidad = "LÍDER SOCIAL"
                    
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

    col_btn1, col_btn2 = st.columns(2)
    
    with col_btn2:
        if st.button("🧹 LIMPIAR DATOS (Empezar de nuevo)"):
            st.session_state['analisis_terminado'] = False
            st.session_state['resultados_df'] = None
            st.session_state['pdf_binario'] = None
            st.session_state['html_parametros'] = ""
            st.session_state['uploader_key'] += 1 
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
                
                # Función para extraer siglas dinámicamente de CUALQUIER entidad (Ej: Ministerio de Salud -> MS)
                def generar_siglas(nombre):
                    palabras_ignoradas = ['DE', 'LA', 'EL', 'LOS', 'LAS', 'Y', 'PARA', 'EN']
                    palabras = [p for p in str(nombre).upper().replace("(", "").replace(")", "").split() if p not in palabras_ignoradas]
                    return "".join([p[0] for p in palabras if p])

                for f in files_comp:
                    info = motor_juridico_final(f)
                    fallos = []
                    
                    if info["calidad"] != ext_base["calidad"]:
                        fallos.append(f"Calidad difiere (Encontró '{info['calidad']}')")
                    
                    acc_base = ext_base["accionado"].strip()
                    acc_comp = info["accionado"].strip()
                    
                    siglas_base = generar_siglas(acc_base)
                    siglas_comp = generar_siglas(acc_comp)
                    
                    coincidencia_accionado = False
                    
                    # 1. Validación directa por substring
                    if len(acc_base) > 4 and len(acc_comp) > 4:
                        if acc_base in acc_comp or acc_comp in acc_base:
                            coincidencia_accionado = True
                            
                    # 2. Validación cruzada por siglas dinámicas (El salvavidas de alias agnóstico)
                    if not coincidencia_accionado:
                        if len(siglas_base) >= 2 and siglas_base in acc_comp:
                            coincidencia_accionado = True
                        elif len(siglas_comp) >= 2 and siglas_comp in acc_base:
                            coincidencia_accionado = True
                        elif len(siglas_base) >= 2 and siglas_base == siglas_comp:
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
