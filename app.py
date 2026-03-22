import streamlit as st
import PyPDF2
import re
import pandas as pd

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(page_title="Garzón - Lector Jurídico", page_icon="⚖️", layout="wide")

# ==========================================
# 2. FUNCIONES AUXILIARES
# ==========================================
def limpiar_texto_usuario(texto):
    """Limpia saltos de línea y espacios extra de un texto."""
    if not isinstance(texto, str):
        return ""
    return re.sub(r'\s+', ' ', texto).strip()

# ==========================================
# 3. MOTOR DE EXTRACCIÓN JURÍDICO FINAL
# ==========================================
def motor_juridico_final(pdf_file):
    texto_acumulado = ""
    try:
        pdf_file.seek(0)
        reader = PyPDF2.PdfReader(pdf_file)
        # Leer solo las primeras 12 páginas para no saturar
        for i in range(min(12, len(reader.pages))):
            texto_acumulado += reader.pages[i].extract_text() + " \n "
    except Exception as e:
        return {"accionante": "ERROR_LECTURA", "calidad": "ERROR", "accionado": "ERROR_LECTURA", "derechos": ["ERROR"]}

    texto_limpio = re.sub(r'\s+', ' ', texto_acumulado)

    # ---------------------------------------------------------
    # DETECCIÓN DE MÚLTIPLES EXPEDIENTES (ACUMULACIÓN)
    # ---------------------------------------------------------
    expedientes = []
    es_multiple = False
    
    m_ref = re.search(r"(?:Referencia|Ref)\s*:?(.*?)(?:Asunto\s*:|Magistrad|Tema|Procedencia|Accionantes?|Demandantes?)", texto_limpio, re.IGNORECASE | re.DOTALL)
    if m_ref:
        bloque_ref = m_ref.group(1)
        # Busca patrones tipo T-10.980.057 o T 10980057
        expedientes_crudos = re.findall(r"T\s*[\.\-\_]?\s*\d{1,3}(?:\.\d{3})*(?:\s*AC)?", bloque_ref, re.IGNORECASE)
        for e in expedientes_crudos:
            e_clean = re.sub(r'\s+', '', e).upper()
            if e_clean not in expedientes:
                expedientes.append(e_clean)

    if len(expedientes) > 1:
        es_multiple = True
        try:
            # Notificamos en la interfaz si hay varios
            st.toast(f"¡Uy! Detecté {len(expedientes)} expedientes acumulados en {pdf_file.name}. Esto será más complejo... 🤯", icon="🤯")
        except:
            pass

    # ---------------------------------------------------------
    # A. EXTRACCIÓN ACCIONANTE Y ACCIONADO
    # ---------------------------------------------------------
    accionantes_lista = []
    accionados_lista = []

    if es_multiple:
        # Intentar extraer desde el Asunto dividiendo por casos
        m_asunto = re.search(r"Asunto\s*:?(.*?)(?:Magistrad|Tema|Sentencia|Fundamentos|Corte Constitucional|I\.\s*ANTECEDENTES)", texto_limpio, re.IGNORECASE | re.DOTALL)
        if m_asunto:
            bloque_asunto = m_asunto.group(1).strip()
            
            # Limpiamos preámbulos genéricos que estorban
            bloque_asunto = re.sub(r'(?i)(?:acciones de tutela presentadas por|acción de tutela interpuesta por|tutelas instauradas por|tutela formulada por)', '', bloque_asunto)
            
            # Cortamos por punto y coma, punto, salto de línea o guiones
            casos = re.split(r';|\.|\n| - | — ', bloque_asunto)
            
            for caso in casos:
                # Limpiar conectores al inicio de cada caso ("y", "e", "por", "de")
                caso_limpio = re.sub(r'^\s*(?:y\s+|e\s+|por\s+|de\s+)', '', caso, flags=re.IGNORECASE).strip()
                
                if "contra" in caso_limpio.lower() or "frente a" in caso_limpio.lower():
                    # Buscar el patrón "X contra Y" dentro del fragmento ya limpio
                    m_pair = re.search(r"([A-ZÁÉÍÓÚÑa-záéíóúñ\s\,]{3,150}?)\s+(?:contra|en contra de|frente a)\s+(?:la\s+|el\s+|los\s+|las\s+)?([A-ZÁÉÍÓÚÑa-záéíóúñ\s\(\)_\-\,\.]{3,150}?)(?=$|para\s|a fin de\s)", caso_limpio, re.IGNORECASE)
                    
                    if m_pair:
                        acc = m_pair.group(1).strip().upper()
                        ado = m_pair.group(2).strip().upper()
                        
                        # Limpiar basuritas si quedaron al principio
                        acc = re.sub(r'^(?:LA SEÑORA|EL SEÑOR|LOS CIUDADANOS)\s*', '', acc).strip()
                        
                        accionantes_lista.append(acc)
                        accionados_lista.append(ado)

    accionante = "NO IDENTIFICADO"
    accionado = "NO IDENTIFICADO"

    # Si NO es múltiple, o si falló el parseo del Asunto por casos, usamos la lógica clásica
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
        # Formatear el resultado múltiple encontrado "Exp 1: A | Exp 2: B"
        acc_str = ""
        ado_str = ""
        for i in range(len(accionantes_lista)):
            exp_label = expedientes[i] if i < len(expedientes) else f"EXP_{i+1}"
            acc_str += f"[{exp_label}] {accionantes_lista[i]} | "
            ado_str += f"[{exp_label}] {accionados_lista[i]} | "
        accionante = acc_str.strip(" | ")
        accionado = ado_str.strip(" | ")

    # ---------------------------------------------------------
    # C. EXTRACCIÓN CALIDAD
    # ---------------------------------------------------------
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
        # Si es múltiple, tomamos el primer nombre de toda la cadena
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

    # ---------------------------------------------------------
    # D. EXTRACCIÓN DERECHOS VULNERADOS
    # ---------------------------------------------------------
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
                
    return {"accionante": accionante, "calidad": calidad, "accionado": accionado, "derechos": ", ".join(derechos_finales)}

# ==========================================
# 4. INTERFAZ DE USUARIO (STREAMLIT)
# ==========================================
st.title("⚖️ Garzón - Asistente de Lectura Jurídica")
st.markdown("Sube tus sentencias o autos en PDF. Garzón extraerá la información clave por ti, incluso si hay expedientes acumulados.")

archivos_subidos = st.file_uploader("Sube los documentos (PDF)", type=["pdf"], accept_multiple_files=True)

if archivos_subidos:
    if st.button("Analizar Documentos con Garzón 🚀"):
        resultados = []
        with st.spinner("Garzón se puso las gafas y está leyendo... 👓"):
            for archivo in archivos_subidos:
                datos = motor_juridico_final(archivo)
                datos["Archivo"] = archivo.name
                resultados.append(datos)
        
        st.success("¡Análisis completado!")
        
        # Mostrar tabla de resultados
        df = pd.DataFrame(resultados)
        df = df[["Archivo", "accionante", "accionado", "calidad", "derechos"]]
        
        # Le damos un formato bonito a la tabla
        st.dataframe(
            df, 
            column_config={
                "Archivo": "Documento",
                "accionante": "Accionante(s)",
                "accionado": "Accionado(s)",
                "calidad": "Calidad del Accionante",
                "derechos": "Derechos Invocados"
            },
            use_container_width=True
        )
