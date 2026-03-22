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
import random

# ==========================================
# 1. CONFIGURACIÓN Y ESTILOS VISUALES
# ==========================================
st.set_page_config(page_title="ECOMODA - Servidor Jurídico", layout="wide")

def cargar_imagen_base64(ruta):
    if os.path.exists(ruta):
        with open(ruta, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ""

# Asegúrate de tener estas imágenes en tu carpeta, o deja las rutas vacías si no las tienes.
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
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LISTAS Y CONFIGURACIONES
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

# ==========================================
# 3. FUNCIONES AUXILIARES
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
    """Toma una cadena con varios nombres y expedientes, y devuelve una lista limpia ['A', 'B', 'C']"""
    texto_limpio = limpiar_texto_usuario(texto)
    texto_limpio = re.sub(r'\[T[-\w\.]+\]\s*', '', texto_limpio)
    sujetos = re.split(r'\s+Y\s+|\s+E\s+|,|\|', texto_limpio)
    return [s.strip() for s in sujetos if len(s.strip()) > 3]

# ==========================================
# 4. MOTOR DE EXTRACCIÓN JURÍDICO 
# ==========================================
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

    # DETECCIÓN DE MÚLTIPLES EXPEDIENTES
    expedientes = []
    es_multiple = False
    
    m_ref = re.search(r"(?:Referencia|Ref)\s*:?(.*?)(?:Asunto\s*:|Magistrad|Tema|Procedencia|Accionantes?|Demandantes?)", texto_limpio, re.IGNORECASE | re.DOTALL)
    if m_ref:
        bloque_ref = m_ref.group(1)
        expedientes_crudos = re.findall(r"T\s*[\.\-\_]?\s*\d{1,3}(?:\.\d{3})*(?:\s*AC)?", bloque_ref, re.IGNORECASE)
        for e in expedientes_crudos:
            e_clean = re.sub(r'\s+', '', e).upper()
            if e_clean not in expedientes:
                expedientes.append(e_clean)

    if len(expedientes) > 1:
        es_multiple = True
        try:
            st.toast(f"¡Uy! Detecté {len(expedientes)} expedientes acumulados en {pdf_file.name}. Esto será más complejo de lo que pensé... 🤯", icon="🤯")
        except:
            pass

    # A. EXTRACCIÓN ACCIONANTE Y ACCIONADO
    accionantes_lista = []
    accionados_lista = []

    if es_multiple:
        m_asunto = re.search(r"Asunto\s*:?(.*?)(?:Magistrad|Tema|Sentencia|Fundamentos|Corte Constitucional|I\.\s*ANTECEDENTES)", texto_limpio, re.IGNORECASE | re.DOTALL)
        if m_asunto:
            bloque_asunto = m_asunto.group(1).strip()
            casos = re.split(r';\s*y\s*|;', bloque_asunto, flags=re.IGNORECASE)
            for caso in casos:
                m_pair = re.search(r"(?:por|de|presentada[s]? por|interpuesta[s]? por)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,150}?)\s+(?:contra|en contra de|frente a)\s+(?:la\s+|el\s+|los\s+|las\s+)?([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_\-\,\.]{3,150}?)(?=\.|$|\n|para|a fin de)", caso, re.IGNORECASE)
                if m_pair:
                    accionantes_lista.append(m_pair.group(1).strip().upper())
                    accionados_lista.append(m_pair.group(2).strip().upper())

    accionante = "NO IDENTIFICADO"
    accionado = "NO IDENTIFICADO"

    if not accionantes_lista or not accionados_lista:
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
                    if es_multiple: accionante = f"[MÚLTIPLES EXP] {cand}"
                    else: accionante = cand
                    break

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
                    if es_multiple: accionado = f"[MÚLTIPLES EXP] {cand}"
                    else: accionado = cand
                    break
                    
        if accionado == "NO IDENTIFICADO" or accionado == "[MÚLTIPLES EXP] NO IDENTIFICADO":
            m_salvavidas = re.search(r"contra\s+(?:la\s+|el\s+|los\s+|las\s+)?([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s\,]{4,150}?)(?=\.|\n| a | para |/| en |\()", texto_limpio)
            if m_salvavidas:
                cand = m_salvavidas.group(1).strip().upper()
                if not any(b in cand for b in ["PROVIDENCIA", "SENTENCIA", "FALLO", "DECISION", "RESOLUCION", "TUTELA", "DERECHO", "VIDA", "INTEGRIDAD", "SALUD", "PETICION"]):
                    if es_multiple: accionado = f"[MÚLTIPLES EXP] {cand}"
                    else: accionado = cand
    else:
        acc_str = ""
        ado_str = ""
        for i in range(len(accionantes_lista)):
            exp_label = expedientes[i] if i < len(expedientes) else f"EXP_{i+1}"
            acc_str += f"[{exp_label}] {accionantes_lista[i]} | "
            ado_str += f"[{exp_label}] {accionados_lista[i]} | "
        accionante = acc_str.strip(" | ")
        accionado = ado_str.strip(" | ")

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
            
    if calidad == "NO IDENTIFICADA (CIVIL)" and "NO IDENTIFICADO" not in accionante:
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
# PANTALLAS: BIENVENIDA, CARGA, LOGIN
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
            st.session_state['pagina_actual'] = 'cargando'
            st.rerun()
        
        st.markdown("""
            <a href='https://www.researchgate.net/publication/359064966_Linea_Jurisprudencial_en_8_simples_pasos' target='_blank' class='guide-button'>
                📖 ¿Dudas sobre la línea jurisprudencial? Aquí encontrarás una guía
            </a>
        """, unsafe_allow_html=True)
    st.stop()

if st.session_state['pagina_actual'] == 'cargando':
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        mensajes_carga = [
            "Buscando en la relatoría de la corte...",
            "Traduciendo 'lenguaje jurídico' a 'lenguaje humano'...",
            "Consultando a la Corte... (modo intenso activado)",
            "¿Seguro que esto no podía ser más simple?",
            "Cuando creías que ya habías terminado... aparece otra sentencia",
            "Cruzando criterios de las altas cortes...",
            "Ordenando el caos jurisprudencial...",
            "Intentando que todo esto tenga sentido...",
            "Negociando con precedentes rebeldes...",
            "Preparando café jurídico ☕..."
        ]
        mensaje_actual = random.choice(mensajes_carga)
        
        st.markdown(f"<h4 style='text-align: center; color: #1a1a1a;'>{mensaje_actual}</h4>", unsafe_allow_html=True)
        barra_carga = st.progress(0)
        
        for porcentaje in range(100):
            time.sleep(0.015) 
            barra_carga.progress(porcentaje + 1)
            
        st.session_state['pagina_actual'] = 'login'
        st.rerun()

if st.session_state['pagina_actual'] == 'login':
    st.markdown("<div class='main-title'>🔒 ACCESO RESTRINGIDO GARZÓN</div>", unsafe_allow_html=True)
    if img_login_b64:
        st.markdown(f"<img src='data:image/png;base64,{img_login_b64}' class='login-img-container'>", unsafe_allow_html=True)
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


# =====================================================================
# PANTALLA 3: APLICACIÓN PRINCIPAL (MODO AUTOMÁTICO)
# =====================================================================
if st.session_state['pagina_actual'] == 'app_garzon' and st.session_state['auth']:
    st.markdown("<div class='main-title'>GARZÓN - INGENIERÍA EN REVERSA JURISPRUDENCIAL</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #f8f9fa; border-left: 5px solid #0f172a; padding: 15px; margin-bottom: 20px; border-radius: 5px; color: black;">
        <b>🕵️‍♂️ ¿Ya tienes definido tu escenario y tu tema jurídico? (Modo Facultativo)</b><br>
        Si ya sabes exactamente qué sujetos vas a analizar y qué derechos están en juego, puedes ingresar los parámetros manualmente.
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
    with col2:
        st.subheader("📂 2. Sentencias a Filtrar")
        files_comp = st.file_uploader("Sube las sentencias citadas", type="pdf", accept_multiple_files=True, key=f"masivo_{st.session_state['uploader_key']}")

    if 'analisis_terminado' not in st.session_state:
        st.session_state['analisis_terminado'] = False
        st.session_state['resultados_df'] = None
        st.session_state['html_parametros'] = ""

    col_btn1, col_btn2 = st.columns(2)
    with col_btn2:
        if st.button("🧹 LIMPIAR DATOS (Empezar de nuevo)"):
            st.session_state['analisis_terminado'] = False
            st.session_state['uploader_key'] += 1 
            st.rerun()
    with col_btn1:
        ejecutar = st.button("🚀 EJECUTAR ANÁLISIS AUTOMÁTICO")

    if ejecutar:
        if not file_arq or not files_comp:
            st.error("Faltan archivos para procesar.")
        else:
            with st.spinner("Garzón está analizando (Modo Automático)..."):
                ext_base = motor_juridico_final(file_arq)
                derechos_base_limpios = [limpiar_texto_usuario(d) for d in ext_base['derechos']]
                
                st.session_state['html_parametros'] = f"""
                <div class="param-box">
                    <b style="font-size: 18px;">📋 REGLAS BASE EXTRAÍDAS (Sujeto, Objeto y Tema):</b><br><br>
                    <ul>
                        <li><b>Calidad Encontrada (Sujeto):</b> {ext_base['calidad']}</li>
                        <li><b>Entidad Accionada Encontrada (Objeto):</b> {ext_base['accionado']}</li>
                        <li><b>Derechos Detectados (Tema):</b> {", ".join(ext_base['derechos'])}</li>
                    </ul>
                </div>
                """

                resultados = []

                for f in files_comp:
                    info = motor_juridico_final(f)
                    fallos = []
                    
                    # 1. MATCH CALIDAD
                    match_calidad = False
                    calidad_limpia_info = limpiar_texto_usuario(info['calidad'])
                    calidad_limpia_final = limpiar_texto_usuario(ext_base['calidad'])
                    if calidad_limpia_final in calidad_limpia_info or calidad_limpia_info in calidad_limpia_final:
                        match_calidad = True
                    else:
                        fallos.append("Calidad difiere")
                    
                    # 2. MATCH ACCIONADO (Manejo de Acumulaciones con limpiar_y_separar_sujetos)
                    match_accionado = False
                    acc_base_lista = limpiar_y_separar_sujetos(ext_base["accionado"])
                    acc_comp_lista = limpiar_y_separar_sujetos(info["accionado"])
                    
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
                        
                    if not match_accionado:
                        fallos.append("Accionado difiere")
                        
                    # 3. MATCH DERECHO
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

                    # VEREDICTO
                    if not match_calidad or not match_accionado:
                        estado = "❌ EXCLUIDA"
                    elif match_calidad and match_accionado and match_derecho:
                        estado = "✅ INCLUIDA"
                    elif match_calidad and match_accionado and not match_derecho:
                        estado = "⚠️ INCLUIDA (El derecho no coincide exactamente, pero el escenario es similar)"
                        
                    resultados.append({
                        "Archivo": f.name,
                        "Accionante Evaluado": info['accionante'],
                        "Calidad Evaluada": info['calidad'],
                        "Accionado Evaluado": info['accionado'],
                        "Derechos Evaluados": ", ".join(info['derechos']),
                        "Fallo/Motivo": ", ".join(fallos) if fallos else "Coincidencia plena",
                        "Veredicto": estado
                    })
                    
                st.session_state['resultados_df'] = pd.DataFrame(resultados)
                st.session_state['analisis_terminado'] = True

    if st.session_state['analisis_terminado']:
        st.markdown(st.session_state['html_parametros'], unsafe_allow_html=True)
        st.subheader("📊 Resultados del Análisis Automático")
        df_display = st.session_state['resultados_df']
        st.dataframe(df_display.style.applymap(highlight_veredicto, subset=['Veredicto']), use_container_width=True)

# =====================================================================
# PANTALLA 4: APLICACIÓN PRINCIPAL (MODO GUIADO / MANUAL)
# =====================================================================
if st.session_state.get('pagina_actual') == 'app_garzon_guiado' and st.session_state.get('auth'):
    st.markdown("<div class='main-title'>GARZÓN - MODO GUIADO (PARAMETRIZADO)</div>", unsafe_allow_html=True)
    
    col_nav1, col_nav2 = st.columns([1, 1])
    with col_nav1:
        if st.button("🚪 Cerrar Sesión / Volver a ECOMODA"):
            st.session_state['auth'] = False
            st.session_state['pagina_actual'] = 'bienvenida'
            st.rerun()
    with col_nav2:
        st.markdown("<div class='btn-guiado'>", unsafe_allow_html=True)
        if st.button("🤖 VOLVER AL MODO AUTOMÁTICO"):
            st.session_state['pagina_actual'] = 'app_garzon'
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    st.write("---")

    st.markdown("### 📝 Define tus parámetros de búsqueda:")
    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        calidad_manual = st.text_input("1. Calidad del Accionante (Ej: Periodista, Indígena)")
    with col_p2:
        accionado_manual = st.text_input("2. Entidad/Sujeto Accionado (Ej: Fiscalía, YouTube)")
    with col_p3:
        derecho_manual = st.selectbox("3. Derecho Principal en Juego", LISTA_DERECHOS)
    
    st.write("---")
    st.subheader("📂 Sube las sentencias a evaluar")
    files_comp_manual = st.file_uploader("Selecciona los PDFs a comparar", type="pdf", accept_multiple_files=True, key=f"masivo_manual_{st.session_state['uploader_key']}")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn2:
        if st.button("🧹 LIMPIAR DATOS (Empezar de nuevo)"):
            st.session_state['uploader_key'] += 1 
            st.rerun()
    with col_btn1:
        ejecutar_manual = st.button("🚀 EJECUTAR ANÁLISIS GUIADO")

    if ejecutar_manual:
        if not calidad_manual or not accionado_manual:
            st.error("Debes ingresar la Calidad y el Accionado para comparar.")
        elif not files_comp_manual:
            st.error("Faltan archivos para procesar.")
        else:
            with st.spinner("Garzón está analizando bajo tus parámetros..."):
                resultados_manuales = []
                
                calidad_base = limpiar_texto_usuario(calidad_manual)
                acc_base_lista = limpiar_y_separar_sujetos(accionado_manual)
                derecho_base = limpiar_texto_usuario(derecho_manual)

                for f in files_comp_manual:
                    info = motor_juridico_final(f)
                    fallos = []
                    
                    # 1. MATCH CALIDAD
                    match_calidad = False
                    calidad_info = limpiar_texto_usuario(info['calidad'])
                    if calidad_base in calidad_info or calidad_info in calidad_base:
                        match_calidad = True
                    else:
                        fallos.append("Calidad difiere")
                        
                    # 2. MATCH ACCIONADO
                    match_accionado = False
                    acc_comp_lista = limpiar_y_separar_sujetos(info["accionado"])
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
                        
                    if not match_accionado:
                        fallos.append("Accionado difiere")
                        
                    # 3. MATCH DERECHO
                    match_derecho = False
                    derechos_info_limpios = [limpiar_texto_usuario(d) for d in info['derechos']]
                    
                    if derecho_base == "NO APLICA" or derecho_base == "OTRO":
                        match_derecho = True
                    else:
                        for d_info in derechos_info_limpios:
                            if derecho_base in d_info or d_info in derecho_base:
                                match_derecho = True
                                break
                        if not match_derecho:
                            fallos.append("Derecho difiere")

                    # VEREDICTO
                    if not match_calidad or not match_accionado:
                        estado = "❌ EXCLUIDA"
                    elif match_calidad and match_accionado and match_derecho:
                        estado = "✅ INCLUIDA"
                    elif match_calidad and match_accionado and not match_derecho:
                        estado = "⚠️ INCLUIDA (El derecho no coincide exactamente, pero el escenario sí)"

                    resultados_manuales.append({
                        "Archivo": f.name,
                        "Accionante Evaluado": info['accionante'],
                        "Calidad Evaluada": info['calidad'],
                        "Accionado Evaluado": info['accionado'],
                        "Derechos Evaluados": ", ".join(info['derechos']),
                        "Fallo/Motivo": ", ".join(fallos) if fallos else "Coincidencia plena",
                        "Veredicto": estado
                    })
                
                st.subheader("📊 Resultados del Análisis Guiado")
                df_manual = pd.DataFrame(resultados_manuales)
                st.dataframe(df_manual.style.applymap(highlight_veredicto, subset=['Veredicto']), use_container_width=True)
