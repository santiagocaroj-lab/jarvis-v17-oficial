import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd
import io
import base64
import os
import unicodedata

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
    
    .btn-guiado>button { background-color: #0f172a; color: #ffc106; border: 2px solid #ffc106; }
    .btn-guiado>button:hover { background-color: #ffc106; color: #0f172a; }

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

# --- 3. MOTOR DE EXTRACCIÓN JURÍDICO (TRIPLE REDUNDANCIA AGNÓSTICA) ---
# Se ubica a nivel global para ser usado tanto en el modo automático como en el guiado.
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

    # A. EXTRACCIÓN ACCIONANTE
    accionante = "NO IDENTIFICADO"
    patrones_acc = [
        r"(?:Accionante|Demandante|Actor)[s]?\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60})(?=\s*-\s*|\s+Accionado|\s+Demandado|C\.C\.|Cédula|Nit|Expediente)",
        r"(?:instaurada|promovida|interpuesta|presentada|formulada)\s+por\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60}?)\s+(?:contra|en contra de|frente a)",
        r"(?:El señor|La señora|El ciudadano|La ciudadana)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60}?)\s+(?:presentó|instauró|interpuso|promovió|formuló)",
        r"(?:Acción de tutela de|amparo propuesto por)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s]{3,60}?)\s+(?:contra|en contra de)"
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
        r"(?:tutela|amparo|demanda)(?:[^\.]{0,50}?)(?:contra|en contra de|frente a)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_-]{4,90}?)(?=\.|\,|\n| para | a fin de | por presunta | solicitando| mediante| \(en adelante)",
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
                
    if accionado == "NO IDENTIFICADO":
        m_salvavidas = re.search(r"contra\s+(?:la\s+|el\s+|los\s+|las\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s]{4,60}?)(?=\.|\,| a | para | y |/| en |\()", texto_limpio)
        if m_salvavidas:
            cand = m_salvavidas.group(1).strip().upper()
            if not any(b in cand for b in ["PROVIDENCIA", "SENTENCIA", "FALLO", "DECISION", "RESOLUCION", "TUTELA", "DERECHO", "VIDA", "INTEGRIDAD", "SALUD", "PETICION"]):
                accionado = cand

    # C. EXTRACCIÓN CALIDAD
    calidad = "NO IDENTIFICADA (CIVIL)"
    poblaciones_lista = ["periodista", "comunicador", "reportero", "líder social", "lideresa social", "defensor de derechos", "defensora de derechos", "abogado", "abogada", "firmante de paz", "indígena", "campesino", "desplazado", "docente"]
    poblaciones_clave = r"(" + "|".join(poblaciones_lista) + r")"
    
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
            
    if calidad == "NO IDENTIFICADA (CIVIL)":
        conteo = {}
        for pob in poblaciones_lista:
            conteo[pob] = len(re.findall(rf"\b{pob}\b", texto_limpio, re.IGNORECASE))
        if conteo:
            max_pob = max(conteo, key=conteo.get)
            if conteo[max_pob] >= 3:
                calidad = max_pob.upper()
            
    if calidad in ["COMUNICADOR", "REPORTERO"]: calidad = "PERIODISTA"
    if calidad in ["LIDERESA SOCIAL", "DEFENSORA DE DERECHOS", "DEFENSOR DE DERECHOS"]: calidad = "LÍDER SOCIAL"
                
    return {"accionante": accionante, "calidad": calidad, "accionado": accionado}

# --- 4. FUNCIONES AUXILIARES DE LIMPIEZA ---
def limpiar_texto_usuario(texto):
    """Elimina tildes, espacios extra y convierte a mayúsculas para igualar parámetros"""
    if not texto: return ""
    texto = str(texto).upper().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto


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
# PANTALLA 3: APLICACIÓN PRINCIPAL (MODO AUTOMÁTICO INTACTO)
# =====================================================================
if st.session_state['pagina_actual'] == 'app_garzon' and st.session_state['auth']:
    
    st.markdown("<div class='main-title'>GARZÓN - INGENIERÍA EN REVERSA JURISPRUDENCIAL</div>", unsafe_allow_html=True)
    
    # --- INTERVENCIÓN DEL USUARIO (NUEVO BANNER) ---
    st.markdown("""
    <div style="background-color: #f8f9fa; border-left: 5px solid #0f172a; padding: 15px; margin-bottom: 20px; border-radius: 5px; color: black;">
        <b>🕵️‍♂️ ¿Ya tienes definido tu escenario jurídico? (Modo Facultativo)</b><br>
        Si ya sabes exactamente qué sujetos vas a analizar (Ej: Periodistas contra la UNP), 
        puedes ayudar a Garzón ingresando los parámetros manualmente para una mayor precisión.
    </div>
    """, unsafe_allow_html=True)
    
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("🚪 Cerrar Sesión / Volver a ECOMODA"):
            st.session_state['auth'] = False
            st.session_state['pagina_actual'] = 'bienvenida'
            st.rerun()
    with col_nav2:
        st.markdown("<div class='btn-guiado'>", unsafe_allow_html=True)
        if st.button("🛠️ IR AL MODO GUIADO (INGRESAR PARÁMETROS)"):
            st.session_state['pagina_actual'] = 'app_garzon_guiado'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("---")

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
        ejecutar = st.button("🚀 EJECUTAR ANÁLISIS AUTOMÁTICO")

    if ejecutar:
        if not file_arq:
            st.error("Falta la Sentencia Arquimédica.")
        elif not files_comp:
            st.warning("Sube al menos un PDF a filtrar.")
        else:
            with st.spinner("Garzón está analizando (Modo Automático)..."):
                ext_base = motor_juridico_final(file_arq)
                
                st.session_state['html_parametros'] = f"""
                <div class="param-box">
                    <b style="font-size: 18px;">📋 PARÁMETROS BASE EXTRAÍDOS DE LA SENTENCIA ARQUIMÉDICA:</b><br><br>
                    <ul>
                        <li><b>Calidad Encontrada (Regla de oro):</b> {ext_base['calidad']}</li>
                        <li><b>Entidad Accionada Encontrada (Regla de oro):</b> {ext_base['accionado']}</li>
                        <li><i>Accionante Base Registrado: {ext_base['accionante']}</i></li>
                    </ul>
                </div>
                """

                resultados = []
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
                    if len(acc_base) > 4 and len(acc_comp) > 4:
                        if acc_base in acc_comp or acc_comp in acc_base:
                            coincidencia_accionado = True
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
                st.session_state['analisis_terminado'] = True

    if st.session_state['analisis_terminado']:
        st.markdown(st.session_state['html_parametros'], unsafe_allow_html=True)
        st.table(st.session_state['resultados_df'])


# =====================================================================
# PANTALLA 4: MODO GUIADO (EL HUMANO EN EL BUCLE - 4TO FILTRO)
# =====================================================================
if st.session_state['pagina_actual'] == 'app_garzon_guiado' and st.session_state['auth']:
    
    st.markdown("<div class='main-title'>GARZÓN - MODO GUIADO (INTERVENCIÓN)</div>", unsafe_allow_html=True)
    
    if st.button("🔙 Volver al Modo Automático"):
        st.session_state['pagina_actual'] = 'app_garzon'
        st.rerun()
        
    st.write("---")
    
    # 1. PARÁMETROS DEL USUARIO
    st.subheader("📝 1. Ingresa tu Escenario (Opcional)")
    st.info("Solo llena los campos que ya tengas definidos. Garzón los usará como 'Idea Base' para interpretar la sentencia Arquimédica.")
    
    col_u1, col_u2, col_u3 = st.columns(3)
    with col_u1:
        u_accionante = st.text_input("Accionante (Ej: Juan Pérez)")
    with col_u2:
        u_accionado = st.text_input("Entidad Accionada (Ej: UNP)")
    with col_u3:
        opts_calidad = ["No aplica", "Periodista/Comunicador social", "Docente", "Funcionario público", "Civil", "Otro"]
        u_calidad_sel = st.selectbox("Calidad del Accionante", opts_calidad)
        u_calidad = ""
        if u_calidad_sel == "Otro":
            u_calidad = st.text_input("Especifique la calidad:")
        elif u_calidad_sel != "No aplica":
            u_calidad = u_calidad_sel
            if u_calidad == "Periodista/Comunicador social":
                u_calidad = "PERIODISTA"
            
    st.write("---")

    # 2. SUBIDA DE ARCHIVOS
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader("⚙️ 2. Sentencia Arquimédica")
        file_arq_g = st.file_uploader("Sube el PDF base", type="pdf", key=f"arq_g_{st.session_state['uploader_key']}")
    with col2:
        st.subheader("📂 3. Sentencias a Filtrar")
        files_comp_g = st.file_uploader("Sube los PDFs citados", type="pdf", accept_multiple_files=True, key=f"masivo_g_{st.session_state['uploader_key']}")

    if 'analisis_terminado_g' not in st.session_state:
        st.session_state['analisis_terminado_g'] = False

    col_btn1, col_btn2 = st.columns(2)
    with col_btn2:
        if st.button("🧹 LIMPIAR DATOS"):
            st.session_state['analisis_terminado_g'] = False
            st.session_state['uploader_key'] += 1 
            st.rerun()
            
    with col_btn1:
        ejecutar_g = st.button("🚀 EJECUTAR ANÁLISIS GUIADO")

    if ejecutar_g:
        if not file_arq_g:
            st.error("Falta la Sentencia Arquimédica.")
        elif not files_comp_g:
            st.warning("Sube al menos un PDF a filtrar.")
        else:
            with st.spinner("Garzón está interpretando tus parámetros y leyendo los expedientes..."):
                
                # Paso 1: Extracción pura de la IA
                ext_base = motor_juridico_final(file_arq_g)
                
                # Paso 2: Limpieza de inputs del usuario
                param_u_acc = limpiar_texto_usuario(u_accionante)
                param_u_ado = limpiar_texto_usuario(u_accionado)
                param_u_cal = limpiar_texto_usuario(u_calidad)
                
                # Paso 3: EL 4TO FILTRO (FUSIÓN IA + HUMANO)
                # El parámetro final será el del usuario si lo escribió, sino, el de la IA.
                final_calidad = param_u_cal if param_u_cal else ext_base['calidad']
                final_accionado = param_u_ado if param_u_ado else ext_base['accionado']
                final_accionante = param_u_acc if param_u_acc else ext_base['accionante']
                
                # Mostrar en pantalla la comparación para transparencia
                st.session_state['html_parametros_g'] = f"""
                <div class="param-box">
                    <b style="font-size: 18px;">🧠 4TO FILTRO APLICADO (FUSIÓN DE PARÁMETROS):</b><br><br>
                    <table style="width:100%; text-align:left; border-collapse: collapse;">
                      <tr>
                        <th style="border-bottom: 1px solid black; padding: 5px;">Criterio</th>
                        <th style="border-bottom: 1px solid black; padding: 5px;">Sugerencia IA (Arquimédica)</th>
                        <th style="border-bottom: 1px solid black; padding: 5px;">Tu Idea Base</th>
                        <th style="border-bottom: 1px solid black; padding: 5px; color: green;">REGLA ÚNICA DEFINIDA</th>
                      </tr>
                      <tr>
                        <td style="padding: 5px;"><b>Calidad</b></td>
                        <td style="padding: 5px;">{ext_base['calidad']}</td>
                        <td style="padding: 5px;">{param_u_cal if param_u_cal else '<i>(Vacío)</i>'}</td>
                        <td style="padding: 5px; color: green;"><b>{final_calidad}</b></td>
                      </tr>
                      <tr>
                        <td style="padding: 5px;"><b>Accionado</b></td>
                        <td style="padding: 5px;">{ext_base['accionado']}</td>
                        <td style="padding: 5px;">{param_u_ado if param_u_ado else '<i>(Vacío)</i>'}</td>
                        <td style="padding: 5px; color: green;"><b>{final_accionado}</b></td>
                      </tr>
                    </table>
                    <br>
                    <p><i>Nota: Garzón exigirá estrictamente la 'Regla Única Definida' para evaluar el resto de sentencias.</i></p>
                </div>
                """

                resultados = []
                def generar_siglas(nombre):
                    palabras_ignoradas = ['DE', 'LA', 'EL', 'LOS', 'LAS', 'Y', 'PARA', 'EN']
                    palabras = [p for p in str(nombre).upper().replace("(", "").replace(")", "").split() if p not in palabras_ignoradas]
                    return "".join([p[0] for p in palabras if p])

                for f in files_comp_g:
                    info = motor_juridico_final(f)
                    fallos = []
                    
                    # 1. Comparación de Calidad contra la Regla Única
                    calidad_limpia_info = limpiar_texto_usuario(info['calidad'])
                    calidad_limpia_final = limpiar_texto_usuario(final_calidad)
                    
                    # Flexibilidad: si la regla única está contenida en la extraída o viceversa
                    if calidad_limpia_final not in calidad_limpia_info and calidad_limpia_info not in calidad_limpia_final:
                        fallos.append(f"Calidad difiere (Encontró '{info['calidad']}')")
                    
                    # 2. Comparación de Accionado contra la Regla Única
                    acc_base = limpiar_texto_usuario(final_accionado)
                    acc_comp = limpiar_texto_usuario(info["accionado"])
                    siglas_base = generar_siglas(acc_base)
                    siglas_comp = generar_siglas(acc_comp)
                    
                    coincidencia_accionado = False
                    
                    if len(acc_base) > 2 and len(acc_comp) > 2:
                        if acc_base in acc_comp or acc_comp in acc_base:
                            coincidencia_accionado = True
                            
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
                        "Motivo": ", ".join(fallos) if fallos else "Cumple exacto con tu Regla Única"
                    })
                
                st.session_state['resultados_df_g'] = pd.DataFrame(resultados)
                st.session_state['analisis_terminado_g'] = True

    if st.session_state['analisis_terminado_g']:
        st.markdown(st.session_state['html_parametros_g'], unsafe_allow_html=True)
        st.table(st.session_state['resultados_df_g'])
