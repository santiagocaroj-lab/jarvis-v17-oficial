import streamlit as st
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd
import io
import base64
import os
import unicodedata
import time

# --- 1. CONFIGURACIÓN Y ESTILOS VISUALES ---
st.set_page_config(page_title="ECOMODA - Servidor Jurídico", layout="wide")

# Función clásica de carga de imagen (sin caché, como pediste)
def cargar_imagen_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

img_logo_b64 = cargar_imagen_base64("Gemini_Generated_Image_ycjj93ycjj93ycjj (1).png")
img_login_b64 = cargar_imagen_base64("IMAGEN 4.png")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif; background-color: white; color: #1a1a1a; }
    .main-title { font-size: 38px; font-weight: 800; border-left: 10px solid #ffc106; padding-left: 20px; margin-bottom: 30px; text-transform: uppercase; }
    
    /* --- ANIMACIONES CSS --- */
    @keyframes fadeInUp {
        0% { opacity: 0; transform: translateY(40px); }
        100% { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeIn {
        0% { opacity: 0; }
        100% { opacity: 1; }
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
    .ecomoda-header { font-size: 16px; color: #94a3b8; letter-spacing: 5px; font-weight: 600; margin-top: 15px; margin-bottom: 25px; text-transform: uppercase; }
    .welcome-title { font-size: 46px; font-weight: 800; color: #ffc106 !important; margin-bottom: 20px; line-height: 1.2; text-transform: uppercase; }
    .welcome-subtitle { font-size: 18px; color: #f8fafc !important; font-weight: 400; margin-bottom: 40px; max-width: 700px; margin-left: auto; margin-right: auto; line-height: 1.6; }
    
    /* --- BOTONES Y FORMULARIOS --- */
    .stButton>button, div[data-testid="stFormSubmitButton"]>button { 
        background-color: #ffc106; color: black; border: 2px solid black; font-weight: bold; width: 100%; height: 50px; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s ease; border-radius: 8px;
    }
    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover { 
        background-color: black; color: #ffc106; transform: scale(1.02); 
    }
    
    .btn-guiado>button { background-color: #0f172a; color: #ffc106; border: 2px solid #ffc106; }
    .btn-guiado>button:hover { background-color: #ffc106; color: #0f172a; }

    .guide-button {
        display: flex; align-items: center; justify-content: center; background-color: transparent; color: #ffc106; border: 2px solid #ffc106; font-weight: bold; width: 100%; height: auto; padding: 12px 10px; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s ease; border-radius: 8px; text-decoration: none; margin-top: 15px; font-size: 13px;
    }
    .guide-button:hover { background-color: #ffc106; color: black; transform: scale(1.02); text-decoration: none; }

    .param-box { background-color: #f8f9fa; border: 2px solid #ffc106; padding: 20px; border-radius: 10px; margin-bottom: 25px; color: #000000 !important; }
    .param-box b, .param-box li, .param-box ul { color: #000000 !important; }
    
    /* --- ESTILOS PARA IMAGEN DE LOGIN ANCLADA Y FORMULARIO --- */
    div[data-testid="stTextInput"], .stButton, div[data-testid="stFormSubmitButton"] { position: relative; z-index: 10; }
    
    div[data-testid="stForm"] { border: none; padding: 0; max-width: 350px; margin: 0; margin-left: 0; background-color: transparent; }
    
    .login-img-container { position: fixed; bottom: 0px; right: -12%; height: 80vh; width: auto; object-fit: contain; opacity: 0; animation: fadeIn 1.2s ease 0.1s forwards; z-index: 999; pointer-events: none; }
    
    /* Estilos para centrar la barra de carga */
    .loading-container { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LISTAS Y CONFIGURACIONES ---
LISTA_DERECHOS = [
    "No aplica", "Acceso a la administración de justicia", "Acceso progresivo a la tierra", "Agua potable", 
    "Ambiente sano", "Asociación sindical", "Ayuda humanitaria", "Consulta previa", "Debido proceso", 
    "Derecho a la capacidad jurídica", "Derecho a la honra", "Derecho a la nacionalidad", "Derecho a la paz", 
    "Derecho a la reparación a población víctima de desplazamiento", "Derecho a la vida libre de violencia de género", 
    "Derecho a morir dignamente", "Derecho al acceso a cargos públicos", "Derecho al buen nombre", 
    "Derecho de los niños", "Derecho de petición", "Dignidad humana", "Educación", "Elegir y ser elegido", 
    "Libre desarrollo de la personalidad", "Libre expresión", "Libertad de prensa", 
    "Reconocimiento de persona en condición de desplazamiento mediante el ruv", "Recreación y deporte", 
    "Salud", "Seguridad personal", "Seguridad social", "Sexuales y reproductivos", 
    "Suministro de energía eléctrica", "Trabajo", "Tranquilidad personal", "Vida", "Visita íntima", 
    "Vivienda digna", "Otro"
]

if 'pagina_actual' not in st.session_state: st.session_state['pagina_actual'] = 'bienvenida'
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'uploader_key' not in st.session_state: st.session_state['uploader_key'] = 0 

# (Aquí va la función motor_juridico_final, la he omitido en esta visualización para no saturarte, 
#  pero tú debes mantener la misma que ya tienes en tu código original)
# ... [MANTÉN TU motor_juridico_final Y FUNCIONES AUXILIARES AQUÍ] ...

def limpiar_texto_usuario(texto):
    if not texto: return ""
    texto = str(texto).upper().strip()
    texto = ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')
    return texto

def generar_siglas(nombre):
    palabras_ignoradas = ['DE', 'LA', 'EL', 'LOS', 'LAS', 'Y', 'PARA', 'EN']
    palabras = [p for p in str(nombre).upper().replace("(", "").replace(")", "").split() if p not in palabras_ignoradas]
    return "".join([p[0] for p in palabras if p])

def highlight_veredicto(val):
    if "✅" in val: return 'background-color: #dcfce7; color: black; font-weight: bold;'
    elif "⚠️" in val: return 'background-color: #fef08a; color: black; font-weight: bold;'
    elif "❌" in val: return 'background-color: #fee2e2; color: black;'
    return ''

# =====================================================================
# PANTALLA 1: BIENVENIDA (ECOMODA)
# =====================================================================
if st.session_state['pagina_actual'] == 'bienvenida':
    img_html = ""
    if img_logo_b64:
        img_html = f"<img src='data:image/png;base64,{img_logo_b64}' width='140' style='border-radius: 10px;'>"

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
            # En lugar de ir directo al login, vamos a la pantalla de carga
            st.session_state['pagina_actual'] = 'cargando'
            st.rerun()
        
        st.markdown("""
            <a href='https://www.researchgate.net/publication/359064966_Linea_Jurisprudencial_en_8_simples_pasos' target='_blank' class='guide-button'>
                📖 ¿Dudas sobre la línea jurisprudencial? Aquí encontrarás una guía
            </a>
        """, unsafe_allow_html=True)
    st.stop()

# =====================================================================
# PANTALLA INTERMEDIA: LÍNEA DE CARGA (NUEVA)
# =====================================================================
if st.session_state['pagina_actual'] == 'cargando':
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h4 style='text-align: center;'>Estableciendo conexión segura...</h4>", unsafe_allow_html=True)
        barra_carga = st.progress(0)
        
        # Simulamos la carga visual para darle tiempo a limpiar la pantalla anterior
        for porcentaje in range(100):
            time.sleep(0.01) # Velocidad de la línea (1 segundo en total)
            barra_carga.progress(porcentaje + 1)
            
        # Una vez termina, cambiamos al login real
        st.session_state['pagina_actual'] = 'login'
        st.rerun()

# =====================================================================
# PANTALLA 2: FIREWALL DE SEGURIDAD (LOGIN)
# =====================================================================
if st.session_state['pagina_actual'] == 'login':
    st.markdown("<div class='main-title'>🔒 ACCESO RESTRINGIDO GARZÓN</div>", unsafe_allow_html=True)
    
    if img_login_b64:
        st.markdown(f"""
            <img src="data:image/png;base64,{img_login_b64}" class="login-img-container">
            """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("Por favor, identifícate para acceder al motor de análisis.")
        
        with st.form(key='login_form', clear_on_submit=False):
            clave = st.text_input("Ingrese la clave de seguridad:", type="password")
            submit_button = st.form_submit_button("INGRESAR")
            
            if submit_button:
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

# ... [MANTÉN EL RESTO DEL CÓDIGO DE LAS PANTALLAS 3 Y 4 AQUÍ] ...
