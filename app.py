import streamlit as st
import streamlit.components.v1 as components
import fitz  # Esta es la librería PyMuPDF (asegúrate de hacer: pip install PyMuPDF)
import re
from fpdf import FPDF
import pandas as pd
import io
import base64
import os
import unicodedata
import time
import random

# ==========================================
# 1. CONFIGURACIÓN Y ESTILOS VISUALES
# ==========================================
st.set_page_config(page_title="ECOMODA - Servidor Jurídico", layout="wide", initial_sidebar_state="collapsed")

with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚙️ Configuración</h2>", unsafe_allow_html=True)
    st.toggle("🔇 Silenciar Música y Efectos", key="silenciar_sonido", value=False)

def cargar_archivo_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as archivo:
            return base64.b64encode(archivo.read()).decode()
    return ""

img_logo_b64 = cargar_archivo_base64("Gemini_Generated_Image_ycjj93ycjj93ycjj (1).png")
img_login_b64 = cargar_archivo_base64("IMAGEN 4.png")

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
        background-color: #ffc106; color: black; border: 2px solid black; font-weight: bold; width: 100%; height: 50px; text-transform: uppercase; letter-spacing: 1px;
        transition: all 0.3s ease; border-radius: 8px;
    }
    .stButton>button:hover, div[data-testid="stFormSubmitButton"]>button:hover {
        background-color: black; color: #ffc106; transform: scale(1.02);
    }

    .btn-guiado>button { background-color: #0f172a; color: #ffc106; border: 2px solid #ffc106; }
    .btn-guiado>button:hover { background-color: #ffc106; color: #0f172a; }

    .guide-button {
        display: flex; align-items: center; justify-content: center; background-color: transparent; color: #ffc106; border: 2px solid #ffc106; font-weight: bold; width: 100%; height: auto;
        padding: 12px 10px; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s ease; border-radius: 8px; text-decoration: none; margin-top: 15px; font-size: 13px;
    }
    .guide-button:hover { background-color: #ffc106; color: black; transform: scale(1.02); text-decoration: none; }
    
    .param-box { background-color: #f8f9fa; border: 2px solid #ffc106; padding: 20px; border-radius: 10px; margin-bottom: 25px; color: #000000 !important; }
    .param-box b, .param-box li, .param-box ul { color: #000000 !important; }

    /* --- ESTILOS PARA IMAGEN DE LOGIN ANCLADA Y FORMULARIO --- */
    div[data-testid="stTextInput"], .stButton, div[data-testid="stFormSubmitButton"] { position: relative; z-index: 10; }
    
    div[data-testid="stForm"] { border: none; padding: 0; max-width: 350px; margin: 0; margin-left: 0; background-color: transparent; }
    
    .login-img-container { 
        position: fixed; 
        bottom: 0px; 
        right: -12%; 
        height: 80vh; 
        width: auto; 
        object-fit: contain; 
        opacity: 0; 
        animation: fadeIn 1.2s ease 0.1s forwards; 
        z-index: 999; 
        pointer-events: none; 
        transition: right 0.3s ease-out; 
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LISTAS Y CONFIGURACIONES INICIALES
# ==========================================
LISTA_DERECHOS = [
    "No aplica", "Acceso a la administración de justicia", "Acceso progresivo a la tierra", "Agua potable",
    "Ambiente sano", "Asociación sindical", "Ayuda humanitaria", "Consulta previa", "Debido proceso",
    "Derecho a la capacidad jurídica", "Derecho a la honra", "Derecho a la nacionalidad", "Derecho a la paz",
    "Derecho a la reparación a población víctima de desplazamiento", "Derecho a la vida libre de violencia de género",
    "Derecho a morir dignamente", "Derecho al acceso a cargos públicos", "Derecho al buen nombre",
    "Derecho de los niños", "Derecho de petición", "Dignidad humana", "Educación", "Elegir y ser elegido",
    "Estabilidad laboral reforzada", "Familia", "Habeas data", "Identidad cultural", "Identidad sexual y de genero",
    "Igualdad", "Integridad personal, fisica y psicologica", "Interrupción voluntaria del embarazo", "Intimidad",
    "Intimidad familiar", "Libertad", "Libertad de culto", "Libertad de enseñanza", "Libertad de expresión",
    "Libertad de información", "Libertad de locomoción y domicilio", "Libertad de opinión", "Libertad de prensa",
    "Libertad de profesión u oficio", "Libre desarrollo de la personalidad", "Mínimo vital", "Objeción de conciencia",
    "Participación en materia ambiental", "Participación política", "Personalidad jurídica", "Propiedad privada",
    "Reconocimiento de persona en condición de desplazamiento mediante el ruv", "Recreación y deporte",
    "Salud", "Seguridad personal", "Seguridad social", "Sexuales y reproductivos",
    "Suministro de energía eléctrica", "Trabajo", "Tranquilidad personal", "Vida", "Visita íntima",
    "Vivienda digna", "Otro"
]

if 'pagina_actual' not in st.session_state: st.session_state['pagina_actual'] = 'bienvenida'
if 'auth' not in st.session_state: st.session_state['auth'] = False
if 'uploader_key' not in st.session_state: st.session_state['uploader_key'] = 0
if 'sfx_pendiente' not in st.session_state: st.session_state['sfx_pendiente'] = None
if 'musica_activa' not in st.session_state: st.session_state['musica_activa'] = False
if 'musica_pista' not in st.session_state: st.session_state['musica_pista'] = None

# --- SISTEMA DE BARAJEADO PERFECTO DE FRASES (No repetición) ---
if 'frases_disponibles' not in st.session_state or not st.session_state['frases_disponibles']:
    todas_las_frases = [
        "Buscando en la relatoría de la corte...", "Leyendo sobre el realismo jurídico...", 
        "Analizando estadísticas...", "Yendo por café para trabajar...", "¿Análisis jurisprudencial? Vamos a ello...",
        "Buscando sentencias relevantes...", "Conectando con el servidor jurisprudencial...", 
        "Explorando la relatoría constitucional...", "Indexando precedentes relevantes...",
        "Analizando línea jurisprudencial en construcción...", "Preparando café jurídico ☕...", 
        "Ordenando el caos jurisprudencial...", "Ejecutando análisis de consistencia jurisprudencial...",
        "Traduciendo 'lenguaje jurídico' a 'lenguaje humano'...", "Consultando a la Corte... (modo intenso activado)",
        "¿Seguro que esto no podía ser más simple?", "Cuando creías que ya habías terminado... aparece otra sentencia",
        "Cruzando criterios de las altas cortes...", "Intentando que todo esto tenga sentido...",
        "Negociando con precedentes rebeldes..."
    ]
    random.shuffle(todas_las_frases)
    st.session_state['frases_disponibles'] = todas_las_frases

# ==========================================
# 3. GESTOR DE AUDIO Y SCRIPTS DINÁMICOS
# ==========================================
def renderizar_gestor_y_efectos():
    silenciado = st.session_state.get('silenciar_sonido', False)
    bg_b64 = ""
    sfx_b64 = ""
    
    if not silenciado:
        if st.session_state['musica_activa'] and st.session_state['musica_pista']:
            bg_b64 = cargar_archivo_base64(st.session_state['musica_pista'])
        if st.session_state['sfx_pendiente']:
            sfx_b64 = cargar_archivo_base64(st.session_state['sfx_pendiente'])
            
    js_code = f"""
    <script>
    try {{
        const doc = window.parent.document;
        
        // 1. REPRODUCTOR DE AUDIO INVISIBLE
        const silenciado = {str(silenciado).lower()};
        let bgAudio = doc.getElementById('ecomoda-bg-music');
        if (!bgAudio) {{
            bgAudio = doc.createElement('audio');
            bgAudio.id = 'ecomoda-bg-music';
            bgAudio.loop = true;
            bgAudio.volume = 0.3;
            doc.body.appendChild(bgAudio);
        }}
        
        if (silenciado) {{
            bgAudio.pause();
        }} else {{
            const bgStr = "{bg_b64}";
            if (bgStr) {{
                const targetSrc = "data:audio/mp3;base64," + bgStr;
                if (bgAudio.src !== targetSrc) {{
                    bgAudio.src = targetSrc;
                    bgAudio.play().catch(e => console.log("Autoplay bloqueado"));
                }} else if (bgAudio.paused) {{
                    bgAudio.play().catch(e => console.log("Autoplay bloqueado"));
                }}
            }} else {{
                bgAudio.pause();
                bgAudio.src = "";
            }}
        }}
        
        const sfxStr = "{sfx_b64}";
        if (sfxStr && !silenciado) {{
            let sfxAudio = new Audio("data:audio/mp3;base64," + sfxStr);
            sfxAudio.volume = 0.8;
            sfxAudio.play().catch(e => console.log("Autoplay SFX bloqueado"));
        }}

        // 2. DESPLAZAMIENTO DINÁMICO DE LA IMAGEN
        const checkImg = setInterval(() => {{
            const img = doc.querySelector('.login-img-container');
            const mainContainer = doc.querySelector('[data-testid="stAppViewBlockContainer"]') || doc.querySelector('.block-container');
            
            if (img && mainContainer) {{
                clearInterval(checkImg);
                
                const updatePos = () => {{
                    const rect = mainContainer.getBoundingClientRect();
                    const windowWidth = window.innerWidth;
                    const spaceOnRight = windowWidth - rect.right;
                    img.style.right = (spaceOnRight - 80) + 'px'; 
                }};
                
                const observer = new ResizeObserver(updatePos);
                observer.observe(mainContainer);
                updatePos(); 
            }}
        }}, 200);
        
        setTimeout(() => clearInterval(checkImg), 4000);

    }} catch (error) {{
        console.log("Error de JS:", error);
    }}
    </script>
    """
    components.html(js_code, width=0, height=0)
    st.session_state['sfx_pendiente'] = None

renderizar_gestor_y_efectos()

# ==========================================
# 4. FUNCIONES AUXILIARES Y MOTOR JURÍDICO (ACTUALIZADO A PYMUPDF/FITZ)
# ==========================================
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
    if isinstance(val, str):
        if "✅" in val: return 'background-color: #dcfce7; color: black; font-weight: bold;'
        elif "⚠️" in val: return 'background-color: #fef08a; color: black; font-weight: bold;'
        elif "❌" in val: return 'background-color: #fee2e2; color: black;'
    return ''

def limpiar_y_separar_sujetos(texto):
    texto_limpio = limpiar_texto_usuario(texto)
    sujetos = re.split(r'\s+Y\s+|\s+E\s+|,', texto_limpio)
    return [s.strip() for s in sujetos if len(s.strip()) > 3]

def motor_juridico_final(pdf_file):
    texto_acumulado = ""
    try:
        pdf_file.seek(0)
        # ---------------------------------------------------------
        # AQUÍ ESTÁ EL CAMBIO A LA NUEVA LIBRERÍA (PyMuPDF / fitz)
        # ---------------------------------------------------------
        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
        
        # Leemos hasta 20 páginas
        limite_paginas = min(20, doc.page_count)
        
        for i in range(limite_paginas):
            pagina_texto = doc[i].get_text("text")
            texto_acumulado += pagina_texto + " \n "
            
            # Condición de parada inteligente para ahorrar recursos
            if re.search(r"Magistrad[oa]\s+Ponente", pagina_texto, re.IGNORECASE):
                break
                
        doc.close()
    except Exception as e:
        return {"accionante": "ERROR_LECTURA", "calidad": "ERROR", "accionado": "ERROR_LECTURA", "derechos": ["ERROR"]}
    
    texto_limpio = re.sub(r'\s+', ' ', texto_acumulado)

    # A. EXTRACCIÓN ACCIONANTE
    accionante = "NO IDENTIFICADO"
    patrones_acc = [
        r"(?:Accionantes?|Demandantes?|Actores?)\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,150}?)(?=\s*-\s*|\s+Accionado|\s+Demandado|C\.C\.|Cédula|Nit|Expediente|\n)",
        r"(?:instaurada|promovida|interpuesta|presentada|formulada)[s]?\s+por\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,150}?)\s+(?:contra|en contra de|frente a)",
        r"(?:El señor|La señora|Los señores|Las señoras|El ciudadano|La ciudadana)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,150}?)\s+(?:presentó|instauraron|instauró|interpuso|promovió|formuló)",
        r"(?:Acción de tutela de|amparo propuesto por)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,150}?)\s+(?:contra|en contra de)"
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
        r"(?:Accionados?|Demandados?|Entidad accionada|Entidades accionadas)\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_\-\,\.]{3,150}?)(?=\s*-\s*|\s+Magistrado|\s+Tema|\s+Procedencia|Expediente|\n)",
        r"(?:instaurada|promovida|interpuesta|presentada|formulada)[s]?\s+por\s+(?:[A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,150}?)\s+(?:contra|en contra de|frente a)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_\-\,\.]{4,150}?)(?=\.|\n| para | a fin de | por presunta | solicitando| mediante| \(en adelante)",
        r"(?:tutela|amparo|demanda)(?:[^\.]{0,50}?)(?:contra|en contra de|frente a)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_\-\,\.]{4,150}?)(?=\.|\n| para | a fin de | por presunta | solicitando| mediante| \(en adelante)",
        r"(?:contra|en contra de)(?: la| el| los| las)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_\-\,\.]{4,150}?)(?=\.|\n| para | a fin de | cuyo | quienes)"
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
        m_salvavidas = re.search(r"contra\s+(?:la\s+|el\s+|los\s+|las\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s\,]{4,150}?)(?=\.|\n| a | para |/| en |\()", texto_limpio)
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
        primer_nombre = limpiar_texto_usuario(accionante).split()[0].replace("[", "").replace("]", "")
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
    
    # D. EXTRACCIÓN DERECHOS VULNERADOS
    derechos_encontrados = set()
    patrones_derecho = [
        r"(?:Derechos?\s+vulnerados?|Derechos?\s+invocados?)\s*:\s*([A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,200}?)(?:\.|\n|\||T-|Expediente)",
        r"(?:vulnerar|vulneró|amenazó|violó|transgredió|vulneración|amenaza)(?:[^\.]{0,40}?)(?:derechos?\s+fundamentales?|derecho)(?:\s+a\s+la|\s+al|\s+a|\s+de)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,200}?)(?:\.|\n| para | a fin de | contra | solicitando | mediante | por parte)",
        r"(?:amparo|protección|garantía)(?:[^\.]{0,40}?)(?:derechos?\s+fundamentales?|derecho)(?:\s+a\s+la|\s+al|\s+a|\s+de)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,200}?)(?:\.|\n| para | a fin de | contra | solicitando | mediante | por parte)",
        r"(?:tutela|amparo)(?:[^\.]{0,40}?)(?:derechos?\s+fundamentales?|derecho)(?:\s+a\s+la|\s+al|\s+a|\s+de)?\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,200}?)(?:\.|\n| para | a fin de | contra | solicitando | mediante | por parte)"
    ]

    fragmentos_brutos = []
    for p in patrones_derecho:
        for m in re.finditer(p, texto_limpio, re.IGNORECASE):
            fragmentos_brutos.append(m.group(1).upper())
            
    cortes_basura = [
        " CON FIN", " CON EL FIN", " PARA QUE", " SOLICITANDO", " MEDIANTE", " POR PARTE",
        " HASTA", " A FIN DE", " CONTRA", " CON EL PROPOSITO", " Y EN CONSECUENCIA",
        " SE LE ORDENE", " EN SEDE", " QUE SE", " PIDIENDO", " CON EL OBJETO", " AL DEBIDO",
        " AL QUE", " ORDENAR", " CUMPLA"
    ]

    basura_palabras = ["LA", "EL", "LOS", "LAS", "QUE", "SU", "SUS", "DE", "DEL", "AL", "A", "EN", "POR", "CON", "PARA", "RESPETO", "RESPETÓ", "GARANTICE", "PROTEJA", "ORDENE", "TUTELA", "AMPARO"]

    DERECHOS_MAESTROS = [
        "ADMINISTRACION DE JUSTICIA", "TIERRA", "AGUA POTABLE", "AMBIENTE SANO",
        "ASOCIACION SINDICAL", "AYUDA HUMANITARIA", "CONSULTA PREVIA", "DEBIDO PROCESO",
        "CAPACIDAD JURIDICA", "HONRA", "NACIONALIDAD", "PAZ", "REPARACION",
        "VIDA LIBRE DE VIOLENCIA", "MORIR DIGNAMENTE", "ACCESO A CARGOS PUBLICOS",
        "BUEN NOMBRE", "NIÑOS", "PETICION", "DIGNIDAD HUMANA", "EDUCACION", "ELEGIR Y SER ELEGIDO",
        "ESTABILIDAD LABORAL", "FAMILIA", "HABEAS DATA", "IDENTIDAD CULTURAL", "IDENTIDAD SEXUAL",
        "IGUALDAD", "INTEGRIDAD", "INTERRUPCION VOLUNTARIA", "INTIMIDAD", "LIBERTAD DE CULTO",
        "LIBERTAD DE ENSEÑANZA", "LIBERTAD DE EXPRESION", "LIBRE EXPRESION", "LIBERTAD DE INFORMACION",
        "LIBERTAD DE LOCOMOCION", "LIBERTAD DE OPINION", "LIBERTAD DE PRENSA", "PROFESION U OFICIO",
        "LIBRE DESARROLLO", "MINIMO VITAL", "OBJECION DE CONCIENCIA", "PARTICIPACION EN MATERIA AMBIENTAL",
        "PARTICIPACION POLITICA", "PERSONALIDAD JURIDICA", "PROPIEDAD PRIVADA", "RECONOCIMIENTO DE PERSONA",
        "RECREACION", "SALUD", "SEGURIDAD PERSONAL", "SEGURIDAD SOCIAL", "SEXUALES Y REPRODUCTIVOS",
        "ENERGIA ELECTRICA", "TRABAJO", "TRANQUILIDAD", "VIDA", "VISITA INTIMA", "VIVIENDA DIGNA"
    ]
    
    for frag in fragmentos_brutos:
        for corte in cortes_basura:
            if corte in frag:
                frag = frag.split(corte)[0]

        frag = re.sub(r'\s+Y\s+', ',', frag)
        frag = re.sub(r'\s+E\s+', ',', frag)
        frag = re.sub(r'\s+O\s+', ',', frag)
        partes = [d.strip() for d in frag.split(',')]

        for d in partes:
            d_clean = d.replace("FUNDAMENTALES", "").replace("FUNDAMENTAL", "").replace("DERECHOS", "").replace("DERECHO", "").strip()
            palabras = d_clean.split()
            d_clean = " ".join([w for w in palabras if w not in basura_palabras])

            if len(d_clean) >= 3 and not any(bad in d_clean for bad in ["DEMANDAD", "ACCION", "RESPUESTA", "JUZGADO", "SENTENCIA", "ACTOR"]):
                encontrado = False
                for dm in DERECHOS_MAESTROS:
                    if dm in d_clean or d_clean in dm:
                        derechos_encontrados.add(dm)
                        encontrado = True
                        break

                if not encontrado and len(d_clean) < 30:
                    derechos_encontrados.add(d_clean)
                    
    if not derechos_encontrados:
        texto_inicio = texto_limpio[:5000].upper()
        for dm in DERECHOS_MAESTROS:
            if re.search(rf"\b{dm}\b", texto_inicio):
                derechos_encontrados.add(dm)

    derechos_finales = list(derechos_encontrados)
    if not derechos_finales:
        derechos_finales = ["NO IDENTIFICADO"]

    return {"accionante": accionante, "calidad": calidad, "accionado": accionado, "derechos": derechos_finales}

# =====================================================================
# RUTEO DE PANTALLAS
# =====================================================================

# PANTALLA 1: BIENVENIDA (ECOMODA)
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
        if st.button(" 🚀  INGRESAR AL SISTEMA"):
            st.session_state['musica_activa'] = True
            st.session_state['musica_pista'] = "INCIDENTAL1_mezcla.mp3"
            st.session_state['sfx_pendiente'] = "Boton1.mp3"
            st.session_state['pagina_actual'] = 'cargando'
            st.rerun()

        st.markdown("""
            <a href='https://www.researchgate.net/publication/359064966_Linea_Jurisprudencial_en_8_simples_pasos' target='_blank' class='guide-button'>
                📖  ¿Dudas sobre la línea jurisprudencial? Aquí encontrarás una guía
            </a>
        """, unsafe_allow_html=True)
    
    st.stop()

# PANTALLA INTERMEDIA: LÍNEA DE CARGA
elif st.session_state['pagina_actual'] == 'cargando':
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        mensaje_actual = st.session_state['frases_disponibles'].pop()
        
        st.markdown(f"<h4 style='text-align: center; color: #1a1a1a;'>{mensaje_actual}</h4>", unsafe_allow_html=True)
        barra_carga = st.progress(0)
        
        for porcentaje in range(100):
            time.sleep(0.015) 
            barra_carga.progress(porcentaje + 1)
            
        st.session_state['pagina_actual'] = 'login'
        st.rerun()
        
    st.stop()

# PANTALLA 2: FIREWALL DE SEGURIDAD (LOGIN)
elif st.session_state['pagina_actual'] == 'login':
    st.markdown("<div class='main-title'> 🔒 ACCESO RESTRINGIDO GARZÓN</div>", unsafe_allow_html=True)
    
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
                    st.session_state['sfx_pendiente'] = "Boton2.mp3"
                    st.session_state['musica_pista'] = "INCIDENTAL 2_mezcla.mp3"
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

# PANTALLA 3: GARZÓN (MODO AUTOMÁTICO)
elif st.session_state['pagina_actual'] == 'app_garzon' and st.session_state['auth']:
    st.markdown("<div class='main-title'>GARZÓN - INGENIERÍA EN REVERSA JURISPRUDENCIAL</div>", unsafe_allow_html=True)
    st.markdown("""
        <div style="background-color: #f8f9fa; border-left: 5px solid #0f172a; padding: 15px; margin-bottom: 20px; border-radius: 5px; color: black;">
            <b> 🕵️‍♂️ ¿Ya tienes definido tu escenario y tu tema jurídico? (Modo Facultativo)</b><br>
            Si ya sabes exactamente qué sujetos vas a analizar y qué derechos están en juego, puedes ayudar a Garzón ingresando los parámetros manualmente para una mayor precisión.
        </div>
    """, unsafe_allow_html=True)

    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button(" 🚪 Cerrar Sesión / Volver a ECOMODA"):
            st.session_state['musica_activa'] = False
            st.session_state['auth'] = False
            st.session_state['pagina_actual'] = 'bienvenida'
            st.rerun()
    with col_nav2:
        st.markdown("<div class='btn-guiado'>", unsafe_allow_html=True)
        if st.button(" 🛠️ IR AL MODO GUIADO (INGRESAR PARÁMETROS)"):
            st.session_state['pagina_actual'] = 'app_garzon_guiado'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.write("---")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader(" ⚙️ 1. Sentencia Arquimédica (Base)")
        file_arq = st.file_uploader("Sube el PDF de la sentencia más reciente", type="pdf", key=f"arq_{st.session_state['uploader_key']}")
        if file_arq is not None and not st.session_state.get(f"arq_subido_{st.session_state['uploader_key']}"):
            st.session_state[f"arq_subido_{st.session_state['uploader_key']}"] = True
            st.session_state['sfx_pendiente'] = "subido1.mp3"
            st.rerun()
    with col2:
        st.subheader(" 📂 2. Sentencias a Filtrar")
        files_comp = st.file_uploader("Sube las sentencias citadas (para incluir/excluir)", type="pdf", accept_multiple_files=True, key=f"masivo_{st.session_state['uploader_key']}")
        if files_comp and not st.session_state.get(f"comp_subido_{st.session_state['uploader_key']}"):
            st.session_state[f"comp_subido_{st.session_state['uploader_key']}"] = True
            st.session_state['sfx_pendiente'] = "subido2.mp3"
            st.rerun()

    if 'analisis_terminado' not in st.session_state:
        st.session_state['analisis_terminado'] = False
        st.session_state['resultados_df'] = None
        st.session_state['pdf_binario'] = None
        st.session_state['html_parametros'] = ""

    col_btn1, col_btn2 = st.columns(2)
    with col_btn2:
        if st.button(" 🧹 LIMPIAR DATOS (Empezar de nuevo)"):
            st.session_state['analisis_terminado'] = False
            st.session_state['uploader_key'] += 1 
            st.rerun()
    with col_btn1:
        ejecutar = st.button(" 🚀 EJECUTAR ANÁLISIS AUTOMÁTICO")

    if ejecutar:
        if not file_arq or not files_comp:
            st.error("Faltan archivos para procesar.")
        else:
            with st.spinner("Garzón está analizando (Modo Automático)..."):
                ext_base = motor_juridico_final(file_arq)
                derechos_base_limpios = [limpiar_texto_usuario(d) for d in ext_base['derechos']]
                
                st.session_state['html_parametros'] = f"""
                <div class="param-box">
                    <b style="font-size: 18px;"> 📋 REGLAS BASE EXTRAÍDAS (Sujeto, Objeto y Tema):</b><br><br>
                    <ul>
                        <li><b>Accionante (Sujeto Activo):</b> {ext_base['accionante']}</li>
                        <li><b>Calidad Encontrada (Sujeto):</b> {ext_base['calidad']}</li>
                        <li><b>Entidad Accionada Encontrada (Objeto):</b> {ext_base['accionado']}</li>
                        <li><b>Derechos Detectados (Tema):</b> {", ".join(ext_base['derechos'])}</li>
                    </ul>
                </div>
                """

                resultados = []

                for f in files_comp:
                    info = motor_juridico_final(f)
                    estado = ""
                    fallos = []
                    
                    match_calidad = False
                    calidad_limpia_info = limpiar_texto_usuario(info['calidad'])
                    calidad_limpia_final = limpiar_texto_usuario(ext_base['calidad'])
                    if calidad_limpia_final in calidad_limpia_info or calidad_limpia_info in calidad_limpia_final:
                        match_calidad = True
                    else:
                        fallos.append(f"Calidad difiere ({info['calidad']})")
                    
                    match_accionado = False
                    acc_base = limpiar_texto_usuario(ext_base["accionado"])
                    acc_comp = limpiar_texto_usuario(info["accionado"])
                    siglas_base = generar_siglas(acc_base)
                    siglas_comp = generar_siglas(acc_comp)
                    if (len(acc_base) > 2 and len(acc_comp) > 2 and (acc_base in acc_comp or acc_comp in acc_base)) or \
                       (len(siglas_base) >= 2 and siglas_base in acc_comp) or \
                       (len(siglas_comp) >= 2 and siglas_comp in acc_base) or \
                       (len(siglas_base) >= 2 and siglas_base == siglas_comp) or acc_base == "NO IDENTIFICADO":
                        match_accionado = True
                    else:
                        fallos.append(f"Accionado difiere")
                        
                    match_derecho = False
                    derechos_info_limpios = [limpiar_texto_usuario(d) for d in info['derechos']]
                    
                    if ext_base['derechos'] == ["NO IDENTIFICADO"]:
                        match_derecho = True
                    else:
                        for d_base in derechos_base_limpios:
                            if d_base == "NO IDENTIFICADO": continue
                            for d_info in derechos_info_limpios:
                                if d_base in d_info or d_info in d_base:
                                    match_derecho = True
                                    break
                            if match_derecho: break
                            
                        if not match_derecho:
                            fallos.append("Derecho difiere")

                    if not match_calidad or not match_accionado: estado = " ❌ EXCLUIDA"
                    elif match_calidad and match_accionado and match_derecho: estado = " ✅ INCLUIDA"
                    elif match_calidad and match_accionado and not match_derecho: estado = " ⚠️ INCLUIDA (El derecho no coincide, pero el escenario es muy similar)"
                        
                    resultados.append({
                        "Archivo": f.name,
                        "Accionante": info['accionante'],
                        "Calidad Evaluada": info['calidad'],
                        "Accionado Evaluado": info["accionado"],
                        "Derechos Evaluados": ", ".join(info['derechos']),
                        "Veredicto": estado,
                        "Motivo (Fallas)": ", ".join(fallos) if fallos else "Cumple todos los criterios"
                    })
                
                st.session_state['resultados_df'] = pd.DataFrame(resultados)
                
                def safe_pdf(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "REPORTE DE INGENIERIA EN REVERSA (AUTOMATICO) - GARZON", 0, 1, 'C')
                pdf.set_font("Arial", '', 10)
                pdf.ln(5)
                pdf.multi_cell(0, 7, safe_pdf(f"REGLA UNICA APLICADA (ARQUIMÉDICA):\nSujeto (Calidad): {ext_base['calidad']}\nObjeto (Accionado): {ext_base['accionado']}\nTema (Derecho): {', '.join(ext_base['derechos'])}\n" + "="*50))
                
                for r in resultados:
                    if " ✅ " in r["Veredicto"]: pdf.set_fill_color(220, 255, 220)
                    elif " ⚠️ " in r["Veredicto"]: pdf.set_fill_color(255, 255, 153)
                    else: pdf.set_fill_color(255, 220, 220)
                        
                    pdf.cell(0, 8, safe_pdf(f"Documento: {r['Archivo']}"), 1, 1, 'L', True)
                    pdf.multi_cell(0, 6, safe_pdf(f"Derechos: {r['Derechos Evaluados']}\nCalidad: {r['Calidad Evaluada']}\nAccionado: {r['Accionado Evaluado']}\nVEREDICTO: {r['Veredicto']}\nFallas: {r['Motivo (Fallas)']}\n" + "-"*80))
                    pdf.ln(2)

                try: st.session_state['pdf_binario'] = pdf.output(dest='S').encode('latin-1')
                except AttributeError: st.session_state['pdf_binario'] = bytes(pdf.output())
                    
                st.session_state['analisis_terminado'] = True

    if st.session_state['analisis_terminado']:
        st.markdown(st.session_state['html_parametros'], unsafe_allow_html=True)
        st.dataframe(st.session_state['resultados_df'].style.map(highlight_veredicto, subset=['Veredicto']))
        st.download_button(
            label=" 📥 DESCARGAR REPORTE TÉCNICO EN PDF", 
            data=st.session_state['pdf_binario'], 
            file_name="Reporte_Ingenieria_Inversa.pdf",
            mime="application/pdf"
        )
    st.stop()

# PANTALLA 4: GARZÓN (MODO GUIADO)
elif st.session_state['pagina_actual'] == 'app_garzon_guiado' and st.session_state['auth']:
    st.markdown("<div class='main-title'>GARZÓN - MODO GUIADO (INGRESO MANUAL DE PARÁMETROS)</div>", unsafe_allow_html=True)
    if st.button(" 🔙 Volver al Modo Automático"):
        st.session_state['pagina_actual'] = 'app_garzon'
        st.rerun()
        
    st.write("---")
    st.subheader(" 📝 1. Ingresa tu Escenario y Tema Jurídico")
    st.info("Llena los campos definidos. Garzón los usará como 'Regla Única' y evaluará el cumplimiento de los 3 Criterios (Sujeto, Objeto, Derecho).")
    
    st.markdown("<b> 👤 Datos del Accionante (Quien demanda):</b>", unsafe_allow_html=True)
    col_u1, col_u2, col_u3 = st.columns(3)
    with col_u1: u_accionante = st.text_input("Nombre (Ej: Juan Pérez)")
    with col_u2:
        opts_calidad = ["No aplica", "Periodista/Comunicador social", "Docente", "Funcionario público", "Civil", "Otro"]
        u_calidad_sel = st.selectbox("Calidad del Accionante", opts_calidad)
    with col_u3:
        u_calidad = ""
        if u_calidad_sel == "Otro": u_calidad = st.text_input("Especifique la calidad:")
        elif u_calidad_sel != "No aplica": 
            u_calidad = u_calidad_sel
            if u_calidad == "Periodista/Comunicador social": u_calidad = "PERIODISTA"
                
    st.markdown("<br><b> 🏢 Datos del Accionado (Quien vulnera el derecho):</b>", unsafe_allow_html=True)
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1: u_accionado_nombre = st.text_input("Nombre / Particular (Ej: Carlos Gómez)")
    with col_a2: u_accionado_calidad = st.text_input("Cargo / Calidad (Ej: Alcalde, Gerente)")
    with col_a3: u_accionado_entidad = st.text_input("Entidad vinculada (Ej: Ministerio, UNP)")

    st.markdown("<br><b> ⚖️ Datos del Derecho Vulnerado (Tema):</b>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)
    with col_d1: u_derecho_sel = st.selectbox("Seleccione el Derecho Fundamental principal:", LISTA_DERECHOS)
    with col_d2:
        u_derecho = ""
        if u_derecho_sel == "Otro": u_derecho = st.text_input("Especifique el derecho:")
        elif u_derecho_sel != "No aplica": u_derecho = u_derecho_sel

    st.write("---")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.subheader(" ⚙️ 2. Sentencia Arquimédica")
        file_arq_g = st.file_uploader("Sube el PDF base", type="pdf", key=f"arq_g_{st.session_state['uploader_key']}")
        if file_arq_g is not None and not st.session_state.get(f"arq_g_subido_{st.session_state['uploader_key']}"):
            st.session_state[f"arq_g_subido_{st.session_state['uploader_key']}"] = True
            st.session_state['sfx_pendiente'] = "subido1.mp3"
            st.rerun()
    with col2:
        st.subheader(" 📂 3. Sentencias a Filtrar")
        files_comp_g = st.file_uploader("Sube los PDFs citados", type="pdf", accept_multiple_files=True, key=f"masivo_g_{st.session_state['uploader_key']}")
        if files_comp_g and not st.session_state.get(f"comp_g_subido_{st.session_state['uploader_key']}"):
            st.session_state[f"comp_g_subido_{st.session_state['uploader_key']}"] = True
            st.session_state['sfx_pendiente'] = "subido2.mp3"
            st.rerun()

    if 'analisis_terminado_g' not in st.session_state:
        st.session_state['analisis_terminado_g'] = False
        st.session_state['resultados_df_g'] = None
        st.session_state['html_parametros_g'] = ""
        st.session_state['pdf_binario_g'] = None

    col_btn1, col_btn2 = st.columns(2)
    with col_btn2:
        if st.button(" 🧹 LIMPIAR DATOS"):
            st.session_state['analisis_terminado_g'] = False
            st.session_state['uploader_key'] += 1 
            st.rerun()
            
    with col_btn1:
        ejecutar_g = st.button(" 🚀 EJECUTAR ANÁLISIS GUIADO (Sujeto + Objeto + Derecho)")

    if ejecutar_g:
        if not file_arq_g or not files_comp_g:
            st.error("Faltan archivos para procesar.")
        else:
            with st.spinner("Garzón está interpretando tus parámetros y buscando en los expedientes..."):
                ext_base = motor_juridico_final(file_arq_g)
                
                param_u_cal = limpiar_texto_usuario(u_calidad)
                param_u_acc = limpiar_texto_usuario(u_accionante)
                param_u_der = limpiar_texto_usuario(u_derecho)
                partes_accionado_u = [limpiar_texto_usuario(x) for x in [u_accionado_nombre, u_accionado_calidad, u_accionado_entidad] if limpiar_texto_usuario(x)]
                
                # --- SISTEMA INTELIGENTE DE ALERTAS Y PRIORIDAD (CORRECCIÓN ESTRICTA) ---
                alertas = []
                
                # 1. ACCIONANTE
                final_accionante = ext_base['accionante']
                if param_u_acc:
                    if param_u_acc in ext_base['accionante'] or ext_base['accionante'] in param_u_acc:
                        final_accionante = param_u_acc
                    else:
                        alertas.append(f"El accionante que indicaste (<b>{u_accionante}</b>) no coincide. Daré prioridad a lo hallado en el documento: <b>{ext_base['accionante']}</b>")
                
                # 2. CALIDAD
                final_calidad = ext_base['calidad']
                if param_u_cal and param_u_cal not in ["NO APLICA", "OTRO"]:
                    if param_u_cal in ext_base['calidad'] or ext_base['calidad'] in param_u_cal:
                        final_calidad = param_u_cal
                    else:
                        alertas.append(f"La calidad que indicaste (<b>{u_calidad}</b>) no coincide. Daré prioridad a lo hallado en el documento: <b>{ext_base['calidad']}</b>")

                # 3. ACCIONADO
                final_accionado_display = ext_base['accionado']
                usar_accionado_usuario = False
                if partes_accionado_u:
                    encontrado_acc = False
                    for parte in partes_accionado_u:
                        if parte in ext_base['accionado'] or ext_base['accionado'] in parte:
                            encontrado_acc = True
                            break
                        sigla_parte = generar_siglas(parte)
                        if len(sigla_parte) >= 2 and sigla_parte in ext_base['accionado']:
                            encontrado_acc = True
                            break
                    if encontrado_acc:
                        usar_accionado_usuario = True
                        final_accionado_display = " | ".join(partes_accionado_u)
                    else:
                        alertas.append(f"El accionado que indicaste (<b>{' | '.join(partes_accionado_u)}</b>) no coincide. Daré prioridad a lo hallado en el documento: <b>{ext_base['accionado']}</b>")

                # 4. DERECHOS
                final_derecho_display = ", ".join(ext_base['derechos'])
                usar_derecho_usuario = False
                derechos_base_limpios = [limpiar_texto_usuario(d) for d in ext_base['derechos']]
                
                if param_u_der and param_u_der != "NO APLICA":
                    encontrado_der = False
                    for d_base in derechos_base_limpios:
                        if param_u_der in d_base or d_base in param_u_der:
                            encontrado_der = True
                            break
                    if encontrado_der:
                        usar_derecho_usuario = True
                        final_derecho_display += f" <br><small>(Guía del usuario: {u_derecho})</small>"
                    else:
                        alertas.append(f"El derecho que indicaste (<b>{u_derecho}</b>) no se encontró. Daré prioridad a lo hallado en el documento: <b>{', '.join(ext_base['derechos'])}</b>")

                html_alertas = ""
                if alertas:
                    html_alertas = "<div style='margin-top: 15px; padding: 10px; background-color: #ffeeba; border-left: 5px solid #ffc107; color: #856404; font-size: 14px;'><b>⚠️ ¡Atención! Algunas de tus guías entraron en conflicto con la Sentencia Arquimédica. El sistema de precisión ha dado prioridad al documento original:</b><ul style='margin-top: 5px;'>"
                    for alerta in alertas:
                        html_alertas += f"<li>{alerta}</li>"
                    html_alertas += "</ul></div>"
                
                st.session_state['html_parametros_g'] = f"""
                <div class="param-box">
                    <b style="font-size: 18px;"> 🧠 4TO FILTRO (FUSIÓN SUJETO - OBJETO - TEMA):</b><br><br>
                    <table style="width:100%; text-align:left; border-collapse: collapse;">
                      <tr>
                        <th style="border-bottom: 1px solid black; padding: 5px;">Criterio Evaluado</th>
                        <th style="border-bottom: 1px solid black; padding: 5px;">Sugerencia IA (Arquimédica)</th>
                        <th style="border-bottom: 1px solid black; padding: 5px; color: green;">REGLA ÚNICA A BUSCAR</th>
                      </tr>
                      <tr>
                        <td style="padding: 5px;"><b>0. Accionante (Sujeto)</b></td>
                        <td style="padding: 5px;">{ext_base['accionante']}</td>
                        <td style="padding: 5px; color: green;"><b>{final_accionante}</b></td>
                      </tr>
                      <tr>
                        <td style="padding: 5px;"><b>1. Calidad (Sujeto)</b></td>
                        <td style="padding: 5px;">{ext_base['calidad']}</td>
                        <td style="padding: 5px; color: green;"><b>{final_calidad}</b></td>
                      </tr>
                      <tr>
                        <td style="padding: 5px;"><b>2. Accionado (Objeto)</b></td>
                        <td style="padding: 5px;">{ext_base['accionado']}</td>
                        <td style="padding: 5px; color: green;"><b>{final_accionado_display}</b></td>
                      </tr>
                      <tr>
                        <td style="padding: 5px;"><b>3. Derecho (Tema)</b></td>
                        <td style="padding: 5px;">{", ".join(ext_base['derechos'])}</td>
                        <td style="padding: 5px; color: green;"><b>{final_derecho_display}</b></td>
                      </tr>
                    </table>
                    {html_alertas}
                </div>
                """

                resultados = []

                for f in files_comp_g:
                    info = motor_juridico_final(f)
                    fallos = []
                    
                    # 1. MATCH CALIDAD
                    match_calidad = False
                    calidad_limpia_info = limpiar_texto_usuario(info['calidad'])
                    calidad_limpia_final = limpiar_texto_usuario(final_calidad)
                    if calidad_limpia_final in calidad_limpia_info or calidad_limpia_info in calidad_limpia_final or final_calidad == "NO IDENTIFICADA (CIVIL)":
                        match_calidad = True
                    else:
                        fallos.append(f"Calidad difiere ({info['calidad']})")
                    
                    # 2. MATCH ACCIONADO
                    match_accionado = False
                    acc_comp = limpiar_texto_usuario(info["accionado"])
                    siglas_comp = generar_siglas(acc_comp)
                    
                    if usar_accionado_usuario:
                        for parte in partes_accionado_u:
                            parte_limpia = limpiar_texto_usuario(parte)
                            if len(parte_limpia) > 2:
                                sigla_parte = generar_siglas(parte_limpia)
                                if parte_limpia in acc_comp or acc_comp in parte_limpia or \
                                   (len(sigla_parte) >= 2 and sigla_parte in acc_comp) or \
                                   (len(siglas_comp) >= 2 and siglas_comp in parte_limpia):
                                    match_accionado = True
                                    break
                    else:
                        acc_base = limpiar_texto_usuario(ext_base['accionado'])
                        if acc_base == "NO IDENTIFICADO":
                            match_accionado = True
                        else:
                            siglas_base = generar_siglas(acc_base)
                            if (len(acc_base) > 2 and len(acc_comp) > 2 and (acc_base in acc_comp or acc_comp in acc_base)) or \
                               (len(siglas_base) >= 2 and siglas_base in acc_comp) or \
                               (len(siglas_comp) >= 2 and siglas_comp in acc_base) or \
                               (len(siglas_base) >= 2 and siglas_base == siglas_comp):
                                match_accionado = True
                                
                    if not match_accionado:
                        fallos.append(f"Accionado difiere ({info['accionado'][:20]}...)")
                        
                    # 3. MATCH DERECHO
                    match_derecho = False
                    derechos_info_limpios = [limpiar_texto_usuario(d) for d in info['derechos']]
                    
                    if usar_derecho_usuario:
                        for d_info in derechos_info_limpios:
                            if param_u_der in d_info or d_info in param_u_der:
                                match_derecho = True
                                break
                    else:
                        # Fallback a la Sentencia Base
                        if ext_base['derechos'] == ["NO IDENTIFICADO"]:
                            match_derecho = True
                        else:
                            for d_base in derechos_base_limpios:
                                if d_base == "NO IDENTIFICADO": continue
                                for d_info in derechos_info_limpios:
                                    if d_base in d_info or d_info in d_base:
                                        match_derecho = True
                                        break
                                if match_derecho: break
                        
                    if not match_derecho:
                        fallos.append("Derecho difiere")

                    # VEREDICTO FINAL
                    if not match_calidad or not match_accionado:
                        estado = " ❌ EXCLUIDA"
                    elif match_calidad and match_accionado and match_derecho:
                        estado = " ✅ INCLUIDA"
                    elif match_calidad and match_accionado and not match_derecho:
                        estado = " ⚠️ INCLUIDA (El derecho no coincide, pero el escenario es muy similar)"
                        
                    resultados.append({
                        "Archivo": f.name,
                        "Accionante": info['accionante'],
                        "Calidad Evaluada": info['calidad'],
                        "Accionado Evaluado": info["accionado"],
                        "Derechos Evaluados": ", ".join(info['derechos']),
                        "Veredicto": estado,
                        "Motivo (Fallas)": ", ".join(fallos) if fallos else "Cumple todos los criterios"
                    })
                
                st.session_state['resultados_df_g'] = pd.DataFrame(resultados)
                
                def safe_pdf(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(0, 10, "REPORTE DE INGENIERIA EN REVERSA (GUIADO) - GARZON", 0, 1, 'C')
                pdf.set_font("Arial", '', 10)
                pdf.ln(5)
                pdf.multi_cell(0, 7, safe_pdf(f"REGLA UNICA APLICADA:\nAccionante (Sujeto): {final_accionante}\nCalidad (Sujeto): {final_calidad}\nObjeto (Accionado): {final_accionado_display}\nTema (Derecho): {final_derecho_display.replace('<br><small>','').replace('</small>','')}\n" + "="*50))
                
                for r in resultados:
                    if " ✅ " in r["Veredicto"]: pdf.set_fill_color(220, 255, 220) 
                    elif " ⚠️ " in r["Veredicto"]: pdf.set_fill_color(255, 255, 153) 
                    else: pdf.set_fill_color(255, 220, 220) 
                        
                    pdf.cell(0, 8, safe_pdf(f"Documento: {r['Archivo']}"), 1, 1, 'L', True)
                    pdf.multi_cell(0, 6, safe_pdf(f"Derechos: {r['Derechos Evaluados']}\nCalidad: {r['Calidad Evaluada']}\nAccionado: {r['Accionado Evaluado']}\nVEREDICTO: {r['Veredicto']}\nFallas: {r['Motivo (Fallas)']}\n" + "-"*80))
                    pdf.ln(2)
                    
                try:
                    st.session_state['pdf_binario_g'] = pdf.output(dest='S').encode('latin-1')
                except AttributeError:
                    st.session_state['pdf_binario_g'] = bytes(pdf.output())
                    
                st.session_state['analisis_terminado_g'] = True

    if st.session_state['analisis_terminado_g']:
        st.markdown(st.session_state['html_parametros_g'], unsafe_allow_html=True)
        st.dataframe(st.session_state['resultados_df_g'].style.map(highlight_veredicto, subset=['Veredicto']))
        
        st.download_button(
            label=" 📥 DESCARGAR REPORTE TÉCNICO EN PDF", 
            data=st.session_state['pdf_binario_g'], 
            file_name="reporte_guiado_linea_jurisprudencial.pdf",
            mime="application/pdf"
        )
