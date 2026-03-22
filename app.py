import streamlit as st
import streamlit.components.v1 as components
import PyPDF2
import re
from fpdf import FPDF
import pandas as pd
import io
import base64
import os
import unicodedata
import time
import random

# --- 1. CONFIGURACIÓN Y ESTILOS VISUALES ---
# La barra lateral se inicializa colapsada por defecto
st.set_page_config(page_title="ECOMODA - Servidor Jurídico", layout="wide", initial_sidebar_state="collapsed")

# Pestaña de configuración lateral
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>⚙️ Configuración</h2>", unsafe_allow_html=True)
    st.toggle("🔇 Silenciar Música y Efectos", key="silenciar_sonido", value=False)

# Función para cargar imagen o audio en Base64
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
    @keyframes fadeOut {
        0% { opacity: 1; }
        100% { opacity: 0; }
    }
    .fade-out-anim { animation: fadeOut 1s forwards !important; }
    
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
    .btn-back>button { background-color: white; color: black; border: 2px solid #ccc; height: 40px; font-size: 12px; margin-bottom: 15px; }
    .btn-back>button:hover { background-color: #f0f0f0; color: black; transform: scale(1.02); }

    .guide-button {
        display: flex; align-items: center; justify-content: center; background-color: transparent; color: #ffc106; border: 2px solid #ffc106; font-weight: bold; width: 100%; height: auto;
        padding: 12px 10px; text-transform: uppercase; letter-spacing: 1px; transition: all 0.3s ease; border-radius: 8px; text-decoration: none; margin-top: 15px; font-size: 13px;
    }
    .guide-button:hover { background-color: #ffc106; color: black; transform: scale(1.02); text-decoration: none; }
    .param-box { background-color: #f8f9fa; border: 2px solid #ffc106; padding: 20px; border-radius: 10px; margin-bottom: 25px; color: #000000 !important; }
    .param-box b, .param-box li, .param-box ul { color: #000000 !important; }

    /* --- ESTILOS PARA IMAGEN DE LOGIN (Corregido para no solaparse con sidebar) --- */
    div[data-testid="stTextInput"], div[data-testid="stFormSubmitButton"] { position: relative; z-index: 10; }
    div[data-testid="stForm"] { border: none; padding: 0; max-width: 350px; margin: 0; margin-left: 0; background-color: transparent; }
    
    .login-wrapper { position: relative; min-height: 80vh; width: 100%; }
    .login-img-container { 
        position: absolute; bottom: 0; right: 0; 
        height: 80vh; width: auto; object-fit: contain; 
        opacity: 0; animation: fadeIn 1.2s ease 0.1s forwards; 
        z-index: 0; pointer-events: none; 
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. LISTAS Y CONFIGURACIONES INICIALES ---
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
if 'fade_out' not in st.session_state: st.session_state['fade_out'] = False

# Variables para controlar que la música inicie solo al interactuar
if 'musica_activa' not in st.session_state: st.session_state['musica_activa'] = False
if 'musica_pista' not in st.session_state: st.session_state['musica_pista'] = None

# --- 3. GESTOR DE AUDIO GLOBAL AVANZADO ---
def renderizar_gestor_audio():
    silenciado = st.session_state.get('silenciar_sonido', False)
    bg_b64 = ""
    sfx_b64 = ""
    
    # Preparamos las pistas en Base64
    if not silenciado:
        if st.session_state['musica_activa'] and st.session_state['musica_pista']:
            bg_b64 = cargar_archivo_base64(st.session_state['musica_pista'])
        if st.session_state['sfx_pendiente']:
            sfx_b64 = cargar_archivo_base64(st.session_state['sfx_pendiente'])
            
    js_code = f"""
    <script>
    try {{
        const doc = window.parent.document;
        const silenciado = {str(silenciado).lower()};
        
        // --- MÚSICA DE FONDO ---
        let bgAudio = doc.getElementById('ecomoda-bg-music');
        if (!bgAudio) {{
            bgAudio = doc.createElement('audio');
            bgAudio.id = 'ecomoda-bg-music';
            bgAudio.loop = true;
            bgAudio.volume = 0.3; // Volumen suave
            doc.body.appendChild(bgAudio);
        }}
        
        if (silenciado) {{
            bgAudio.pause();
        }} else {{
            const bgStr = "{bg_b64}";
            if (bgStr) {{
                const targetSrc = "data:audio/mp3;base64," + bgStr;
                // Previene reinicios / solapamientos si la pista es la misma
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
        
        // --- EFECTOS DE SONIDO ---
        const sfxStr = "{sfx_b64}";
        if (sfxStr && !silenciado) {{
            let sfxAudio = new Audio("data:audio/mp3;base64," + sfxStr);
            sfxAudio.volume = 0.8;
            sfxAudio.play().catch(e => console.log("Autoplay SFX bloqueado"));
        }}
    }} catch (error) {{
        console.log("Error de audio:", error);
    }}
    </script>
    """
    components.html(js_code, width=0, height=0)
    
    # Consumimos el efecto para que no se repita
    st.session_state['sfx_pendiente'] = None

# Renderizar el audio al principio de la carga de la página
renderizar_gestor_audio()

# --- 4. FUNCIONES AUXILIARES Y MOTOR JURÍDICO ---
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
    if " ✅ " in val: return 'background-color: #dcfce7; color: black; font-weight: bold;'
    elif " ⚠️ " in val: return 'background-color: #fef08a; color: black; font-weight: bold;'
    elif " ❌ " in val: return 'background-color: #fee2e2; color: black;'
    return ''

def limpiar_y_separar_sujetos(texto):
    texto_limpio = limpiar_texto_usuario(texto)
    sujetos = re.split(r'\s+Y\s+|\s+E\s+|,', texto_limpio)
    return [s.strip() for s in sujetos if len(s.strip()) > 3]

def motor_juridico_final(pdf_file):
    texto_acumulado = ""
    try:
        pdf_file.seek(0)
        reader = PyPDF2.PdfReader(pdf_file)
        for i in range(min(12, len(reader.pages))):
            texto_acumulado += reader.pages[i].extract_text() + " \n "
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
# RUTEO DE PANTALLAS ESTRICTO
# =====================================================================

# PANTALLA 1: BIENVENIDA (ECOMODA)
if st.session_state['pagina_actual'] == 'bienvenida':
    # Si fade_out es True, aplicamos la clase de animación css para desvanecer toda la vista
    fade_class = "fade-out-anim" if st.session_state.get('fade_out') else ""
    st.markdown(f"<div class='{fade_class}'>", unsafe_allow_html=True)
    
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
            # AQUÍ ARRANCA EL SONIDO (1/4 botones que suenan)
            st.session_state['musica_activa'] = True
            st.session_state['musica_pista'] = "INCIDENTAL1_mezcla.mp3"
            st.session_state['sfx_pendiente'] = "Boton1.mp3"
            st.session_state['fade_out'] = True
            st.rerun()

    st.markdown("""
        <a href='https://www.researchgate.net/publication/359064966_Linea_Jurisprudencial_en_8_simples_pasos' target='_blank' class='guide-button'>
            📖  ¿Dudas sobre la línea jurisprudencial? Aquí encontrarás una guía
        </a>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Lógica de espera para el fade out antes de pasar a la pantalla de carga
    if st.session_state.get('fade_out'):
        time.sleep(1)
        st.session_state['fade_out'] = False
        st.session_state['pagina_actual'] = 'cargando'
        st.rerun()

# PANTALLA INTERMEDIA: LÍNEA DE CARGA
elif st.session_state['pagina_actual'] == 'cargando':
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        mensajes_carga = [
            "Buscando en la relatoría de la corte...", "Leyendo sobre el realismo jurídico...", "Analizando estadísticas...", "Yendo por café para trabajar...", "¿Análisis jurisprudencial? Vamos a ello...",
            "Buscando sentencias relevantes...", "Conectando con el servidor jurisprudencial...", "Explorando la relatoría constitucional...", "Indexando precedentes relevantes...",
            "Analizando línea jurisprudencial en construcción...", "Preparando café jurídico  ☕ ...", "Ordenando el caos jurisprudencial...", "Ejecutando análisis de consistencia jurisprudencial..."
        ]
        mensaje_actual = random.choice(mensajes_carga)
        st.markdown(f"<h4 style='text-align: center; color: #1a1a1a;'>{mensaje_actual}</h4>", unsafe_allow_html=True)
        barra_carga = st.progress(0)
        for porcentaje in range(100):
            time.sleep(0.015)
            barra_carga.progress(porcentaje + 1)
            
        st.session_state['pagina_actual'] = 'login'
        st.rerun()

# PANTALLA 2: FIREWALL DE SEGURIDAD (LOGIN)
elif st.session_state['pagina_actual'] == 'login':
    st.markdown("<div class='login-wrapper'>", unsafe_allow_html=True)
    st.markdown("<div class='main-title'> 🔒 ACCESO RESTRINGIDO GARZÓN</div>", unsafe_allow_html=True)
    
    if img_login_b64:
        st.markdown(f"""
        <img src="data:image/png;base64,{img_login_b64}" class="login-img-container">
        """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<div class='btn-back'>", unsafe_allow_html=True)
        if st.button("🔙 Volver a la Bienvenida"):
            st.session_state['pagina_actual'] = 'bienvenida'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        st.info("Por favor, identifícate para acceder al motor de análisis.")
        with st.form(key='login_form', clear_on_submit=False):
            clave = st.text_input("Ingrese la clave de seguridad:", type="password")
            submit_button = st.form_submit_button("INGRESAR")
            if submit_button:
                if clave == "Juan007":
                    # AQUÍ ARRANCA EL SONIDO (2/4 botones que suenan)
                    st.session_state['sfx_pendiente'] = "Boton2.mp3"
                    # Al pasar de la zona de ingreso al análisis, se cambia la pista
                    st.session_state['musica_pista'] = "INCIDENTAL 2_mezcla.mp3"
                    st.session_state['auth'] = True
                    st.session_state['pagina_actual'] = 'app_garzon'
                    st.rerun()
                else:
                    st.error("Acceso denegado. Clave incorrecta.")
    st.markdown("</div>", unsafe_allow_html=True)

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
            st.session_state['musica_activa'] = False # Silencia la música al salir
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
            # AQUÍ ARRANCA EL SONIDO (3/4 botones que suenan)
            st.session_state['sfx_pendiente'] = "Boton1.mp3"
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
                            <li><b>Calidad Encontrada (Sujeto):</b> {ext_base['calidad']}</li>
                            <li><b>Accionado Encontrado (Objeto):</b> {ext_base['accionado']}</li>
                            <li><b>Derechos Encontrados (Tema):</b> {", ".join(ext_base['derechos'])}</li>
                        </ul>
                    </div>
                    """
                    
                    resultados = []
                    for f in files_comp:
                        info = motor_juridico_final(f)
                        estado = ""
                        fallos = []
                        
                        match_calidad = (info['calidad'] == ext_base['calidad']) or (ext_base['calidad'] == "NO IDENTIFICADA (CIVIL)")
                        if not match_calidad: fallos.append(f"Calidad difiere ({info['calidad']})")
                            
                        match_accionado = False
                        if ext_base['accionado'] == "NO IDENTIFICADO":
                            match_accionado = True
                        else:
                            acc_base_lista = limpiar_y_separar_sujetos(ext_base['accionado'])
                            acc_comp_lista = limpiar_y_separar_sujetos(info['accionado'])
                            for a_base in acc_base_lista:
                                for a_comp in acc_comp_lista:
                                    siglas_base = generar_siglas(a_base)
                                    siglas_comp = generar_siglas(a_comp)
                                    if (len(a_base) > 2 and len(a_comp) > 2 and (a_base in a_comp or a_comp in a_base)) or \
                                       (len(siglas_base) >= 2 and siglas_base in a_comp) or \
                                       (len(siglas_comp) >= 2 and siglas_comp in a_base) or \
                                       (len(siglas_base) >= 2 and siglas_base == siglas_comp):
                                        match_accionado = True
                                        break
                                if match_accionado: break
                        if not match_accionado: fallos.append(f"Accionado difiere")
                            
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
                        if not match_derecho: fallos.append("Derecho difiere")

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
                        
                    try:
                        st.session_state['pdf_binario'] = pdf.output(dest='S').encode('latin-1')
                    except AttributeError:
                        st.session_state['pdf_binario'] = bytes(pdf.output())
                        
                    st.session_state['analisis_terminado'] = True

    if st.session_state['analisis_terminado']:
        st.markdown(st.session_state['html_parametros'], unsafe_allow_html=True)
        st.dataframe(st.session_state['resultados_df'].style.applymap(highlight_veredicto, subset=['Veredicto']), use_container_width=True)
        
        st.download_button(
            label=" 📥 DESCARGAR INFORME EN PDF",
            data=st.session_state['pdf_binario'],
            file_name="Reporte_Ingenieria_Inversa.pdf",
            mime="application/pdf"
        )

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
    with col_u1:
        u_accionante = st.text_input("Nombre (Ej: Juan Pérez)")
    with col_u2:
        opts_calidad = ["No aplica", "Periodista/Comunicador social", "Docente", "Funcionario público", "Civil", "Otro"]
        u_calidad_sel = st.selectbox("Calidad del Accionante", opts_calidad)
    with col_u3:
        u_calidad = ""
        if u_calidad_sel == "Otro":
            u_calidad = st.text_input("Especifique la calidad:")
        elif u_calidad_sel != "No aplica":
            u_calidad = u_calidad_sel
        if u_calidad == "Periodista/Comunicador social": u_calidad = "PERIODISTA"

    st.markdown("<br><b> 🏢 Datos del Accionado (Quien vulnera el derecho):</b>", unsafe_allow_html=True)
    col_a1, col_a2, col_a3 = st.columns(3)
    with col_a1:
        u_accionado_nombre = st.text_input("Nombre / Particular (Ej: Carlos Gómez)")
    with col_a2:
        u_accionado_calidad = st.text_input("Cargo / Calidad (Ej: Alcalde, Gerente)")
    with col_a3:
        u_accionado_entidad = st.text_input("Entidad vinculada (Ej: Ministerio, UNP)")

    st.markdown("<br><b> ⚖️ Datos del Derecho Vulnerado (Tema):</b>", unsafe_allow_html=True)
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        u_derecho_sel = st.selectbox("Seleccione el Derecho Fundamental principal:", LISTA_DERECHOS)
    with col_d2:
        u_derecho = ""
        if u_derecho_sel == "Otro":
            u_derecho = st.text_input("Especifique el derecho:")
        elif u_derecho_sel != "No aplica":
            u_derecho = u_derecho_sel

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
        st.session_state['pdf_binario_g'] = None
        st.session_state['html_parametros_g'] = ""

    col_btn1_g, col_btn2_g = st.columns(2)
    with col_btn2_g:
        if st.button(" 🧹 LIMPIAR DATOS", key="limpiar_g"):
            st.session_state['analisis_terminado_g'] = False
            st.session_state['uploader_key'] += 1 
            st.rerun()

    with col_btn1_g:
        ejecutar_g = st.button(" 🚀 EJECUTAR ANÁLISIS GUIADO", key="exec_g")
        if ejecutar_g:
            # AQUÍ ARRANCA EL SONIDO (4/4 botones que suenan)
            st.session_state['sfx_pendiente'] = "Boton1.mp3"
            if not file_arq_g or not files_comp_g:
                st.error("Faltan archivos para procesar.")
            else:
                with st.spinner("Garzón está fusionando parámetros e IA..."):
                    ext_base = motor_juridico_final(file_arq_g)
                    
                    param_u_cal = limpiar_texto_usuario(u_calidad)
                    param_u_acc = limpiar_texto_usuario(u_accionante)
                    param_u_der = limpiar_texto_usuario(u_derecho)
                    partes_accionado_u = [limpiar_texto_usuario(x) for x in [u_accionado_nombre, u_accionado_calidad, u_accionado_entidad] if limpiar_texto_usuario(x)]

                    final_calidad = param_u_cal if param_u_cal else ext_base['calidad']
                    final_accionante = param_u_acc if param_u_acc else ext_base['accionante']
                    final_accionado_display = " | ".join(partes_accionado_u) if partes_accionado_u else ext_base['accionado']
                    
                    derechos_base_limpios = [limpiar_texto_usuario(d) for d in ext_base['derechos']]
                    
                    alerta_derecho = ""
                    if param_u_der and param_u_der != "NO APLICA":
                        encontrado = False
                        for d_base in derechos_base_limpios:
                            if param_u_der in d_base or d_base in param_u_der:
                                encontrado = True
                                break
                        if not encontrado:
                            alerta_derecho = f"<div style='margin-top: 15px; padding: 10px; background-color: #ffeeba; border-left: 5px solid #ffc107; color: #856404;'><b> ⚠️ ¡Atención!</b> Tu derecho guía ({u_derecho}) no se encontró en la sentencia Arquimédica. Sin embargo, Garzón logró identificar los siguientes y les dará mayor peso: <b>{', '.join(ext_base['derechos'])}</b></div>"
                            
                    final_derecho_display = ", ".join(ext_base['derechos'])
                    if param_u_der and param_u_der != "NO APLICA":
                        final_derecho_display += f" <br><small>(Guía del usuario: {u_derecho})</small>"

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
                        {alerta_derecho}
                    </div>
                    """
                    
                    resultados = []
                    for f in files_comp_g:
                        info = motor_juridico_final(f)
                        estado = ""
                        fallos = []

                        match_calidad = (info['calidad'] == final_calidad) or (final_calidad == "NO IDENTIFICADA (CIVIL)")
                        if not match_calidad: fallos.append(f"Calidad difiere ({info['calidad']})")

                        match_accionado = False
                        acc_comp_lista = limpiar_y_separar_sujetos(info['accionado'])
                        
                        if partes_accionado_u:
                            for parte in partes_accionado_u:
                                for a_comp in acc_comp_lista:
                                    if len(parte) > 2 and parte in a_comp:
                                        match_accionado = True
                                        break
                                if match_accionado: break
                        else:
                            if ext_base['accionado'] == "NO IDENTIFICADO": match_accionado = True
                            else:
                                acc_base_lista = limpiar_y_separar_sujetos(ext_base['accionado'])
                                for a_base in acc_base_lista:
                                    for a_comp in acc_comp_lista:
                                        siglas_base = generar_siglas(a_base)
                                        siglas_comp = generar_siglas(a_comp)
                                        if (len(a_base) > 2 and len(a_comp) > 2 and (a_base in a_comp or a_comp in a_base)) or \
                                           (len(siglas_base) >= 2 and siglas_base in a_comp) or \
                                           (len(siglas_comp) >= 2 and siglas_comp in a_base) or \
                                           (len(siglas_base) >= 2 and siglas_base == siglas_comp):
                                            match_accionado = True
                                            break
                                    if match_accionado: break
                                    
                        if not match_accionado: fallos.append(f"Accionado difiere ({info['accionado'][:20]}...)")

                        match_derecho = False
                        derechos_info_limpios = [limpiar_texto_usuario(d) for d in info['derechos']]
                        
                        if ext_base['derechos'] == ["NO IDENTIFICADO"] and (not param_u_der or param_u_der == "NO APLICA"):
                            match_derecho = True
                        else:
                            for d_base in derechos_base_limpios:
                                if d_base == "NO IDENTIFICADO": continue
                                for d_info in derechos_info_limpios:
                                    if d_base in d_info or d_info in d_base:
                                        match_derecho = True
                                        break
                                if match_derecho: break
                                
                            if not match_derecho and param_u_der and param_u_der != "NO APLICA":
                                for d_info in derechos_info_limpios:
                                    if param_u_der in d_info or d_info in param_u_der:
                                        match_derecho = True
                                        break
                                        
                        if not match_derecho: fallos.append("Derecho difiere")

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
                        
                    st.session_state['resultados_df_g'] = pd.DataFrame(resultados)
                    
                    def safe_pdf(txt): return str(txt).encode('latin-1', 'replace').decode('latin-1')

                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font("Arial", 'B', 14)
                    pdf.cell(0, 10, "REPORTE DE INGENIERIA EN REVERSA (GUIADO) - GARZON", 0, 1, 'C')
                    pdf.set_font("Arial", '', 10)
                    pdf.ln(5)
                    pdf.multi_cell(0, 7, safe_pdf(f"REGLA UNICA APLICADA:\nSujeto (Calidad): {final_calidad}\nObjeto (Accionado): {final_accionado_display}\nTema (Derecho): {final_derecho_display}\n" + "="*50))
                    
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
        st.dataframe(st.session_state['resultados_df_g'].style.applymap(highlight_veredicto, subset=['Veredicto']), use_container_width=True)
        
        st.download_button(
            label=" 📥 DESCARGAR INFORME EN PDF",
            data=st.session_state['pdf_binario_g'],
            file_name="Reporte_Ingenieria_Inversa_Guiado.pdf",
            mime="application/pdf"
        )
