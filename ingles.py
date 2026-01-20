import streamlit as st
import openai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import re
import json
import os
import base64
from datetime import datetime
from difflib import SequenceMatcher

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="Nexus Pro v3.0: Bootcamp A1→C1",
    page_icon="🦅",
    layout="wide"
)

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== USUARIOS ====================
USUARIOS = {
    "nasly": "1994",
    "sofia": "2009",
    "andres": "1988"
}

# ==================== LOGIN ====================
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v3.0: Acceso Elite")
    st.markdown("### Sistema profesional de aprendizaje de inglés A1 → C1")
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("👤 Usuario")
        p = st.text_input("🔒 Contraseña", type="password")
        
        if st.button("🚀 Entrar al Bootcamp", use_container_width=True):
            if u in USUARIOS and USUARIOS[u] == p:
                st.session_state.usuario_activo = u
                st.success("✅ Acceso concedido")
                st.rerun()
            else:
                st.error("❌ Usuario o contraseña incorrectos")
    st.stop()

# ==================== CURRÍCULO COMPLETO ====================
CURRICULO = {
    # NIVEL A1 - Básico (30 días)
    "A1.1": {"tema": "Saludos y Presentaciones", "frases": 5},
    "A1.2": {"tema": "Verbo To Be (am/is/are)", "frases": 5},
    "A1.3": {"tema": "Artículos y Pronombres", "frases": 5},
    "A1.4": {"tema": "Números y Cantidades", "frases": 5},
    "A1.5": {"tema": "Colores y Objetos Comunes", "frases": 5},
    "A1.6": {"tema": "Familia y Relaciones", "frases": 5},
    
    # NIVEL A2 - Elemental (30 días)
    "A2.1": {"tema": "Presente Simple", "frases": 6},
    "A2.2": {"tema": "Pasado Simple Regular", "frases": 6},
    "A2.3": {"tema": "Pasado Simple Irregular", "frases": 6},
    "A2.4": {"tema": "Futuro (will/going to)", "frases": 6},
    "A2.5": {"tema": "Preposiciones de Lugar", "frases": 6},
    "A2.6": {"tema": "Comparativos y Superlativos", "frases": 6},
    
    # NIVEL B1 - Intermedio (60 días)
    "B1.1": {"tema": "Presente Perfecto", "frases": 7},
    "B1.2": {"tema": "Presente Continuo", "frases": 7},
    "B1.3": {"tema": "Modales: Can/Could/Should", "frases": 7},
    "B1.4": {"tema": "Pasado Continuo", "frases": 7},
    "B1.5": {"tema": "Condicional Tipo 1", "frases": 7},
    "B1.6": {"tema": "Phrasal Verbs Básicos", "frases": 7},
    "B1.7": {"tema": "Conectores y Transiciones", "frases": 7},
    "B1.8": {"tema": "Voz Pasiva Simple", "frases": 7},
    
    # NIVEL B2 - Intermedio Alto (30 días)
    "B2.1": {"tema": "Presente Perfecto Continuo", "frases": 8},
    "B2.2": {"tema": "Condicionales 2 y 3", "frases": 8},
    "B2.3": {"tema": "Reported Speech", "frases": 8},
    "B2.4": {"tema": "Modales Avanzados", "frases": 8},
    "B2.5": {"tema": "Phrasal Verbs Avanzados", "frases": 8},
    
    # NIVEL C1 - Avanzado (30 días)
    "C1.1": {"tema": "Estructuras Formales", "frases": 10},
    "C1.2": {"tema": "Inglés de Negocios", "frases": 10},
    "C1.3": {"tema": "Expresiones Idiomáticas", "frases": 10},
    "C1.4": {"tema": "Debate y Argumentación", "frases": 10},
    "C1.5": {"tema": "Certificación Final C1", "frases": 10}
}

# ==================== FUNCIONES AUXILIARES ====================

def similitud_texto(texto1, texto2):
    """Calcula similitud entre dos textos (0-100%) - IGNORA PUNTUACIÓN"""
    # Remover TODO: puntuación, convertir a minúsculas, quitar espacios extra
    t1 = re.sub(r'[^\w\s]', '', texto1.lower().strip())
    t1 = ' '.join(t1.split())  # Normalizar espacios
    
    t2 = re.sub(r'[^\w\s]', '', texto2.lower().strip())
    t2 = ' '.join(t2.split())  # Normalizar espacios
    
    return int(SequenceMatcher(None, t1, t2).ratio() * 100)

def comparar_palabras(texto_usuario, texto_objetivo):
    """Compara palabra por palabra y retorna análisis visual"""
    palabras_usuario = texto_usuario.lower().split()
    palabras_objetivo = texto_objetivo.lower().split()
    
    resultado = []
    max_len = max(len(palabras_usuario), len(palabras_objetivo))
    
    for i in range(max_len):
        p_usuario = palabras_usuario[i] if i < len(palabras_usuario) else "---"
        p_objetivo = palabras_objetivo[i] if i < len(palabras_objetivo) else "---"
        
        # Limpiar puntuación
        p_usuario_limpio = re.sub(r'[^\w]', '', p_usuario)
        p_objetivo_limpio = re.sub(r'[^\w]', '', p_objetivo)
        
        if p_usuario_limpio == p_objetivo_limpio:
            resultado.append(f"✅ {p_objetivo}")
        else:
            resultado.append(f"❌ {p_objetivo} (dijiste: {p_usuario})")
    
    return "\n".join(resultado)

def cargar_datos():
    """Carga datos del usuario desde JSON"""
    archivo = f"datos_{st.session_state.usuario_activo}.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    
    return {
        "nivel_actual": "A1.1",
        "frases_correctas": 0,
        "en_examen": False,
        "examen_actual": [],
        "respuestas_examen": [],
        "chat": [],
        "historial": [],
        "fecha_inicio": datetime.now().isoformat()
    }

def guardar_datos():
    """Guarda datos del usuario en JSON"""
    archivo = f"datos_{st.session_state.usuario_activo}.json"
    datos = {
        "nivel_actual": st.session_state.nivel_actual,
        "frases_correctas": st.session_state.frases_correctas,
        "en_examen": st.session_state.en_examen,
        "examen_actual": st.session_state.examen_actual,
        "respuestas_examen": st.session_state.respuestas_examen,
        "chat": st.session_state.chat,
        "historial": st.session_state.historial,
        "fecha_inicio": st.session_state.fecha_inicio
    }
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

# ==================== FUNCIONES DE IA ====================

def transcribir_audio(audio_bytes):
    """Transcribe audio a texto en inglés"""
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        
        transcripcion = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",
            prompt="English pronunciation practice. Transcribe in English only."
        )
        return transcripcion.text.strip()
    except Exception as e:
        st.error(f"Error al transcribir: {e}")
        return ""

def generar_audio_ingles(texto):
    """Genera audio en inglés con Google TTS"""
    try:
        tts = gTTS(text=texto, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode()
    except:
        return None

def generar_frase(nivel, tema, numero):
    """Genera una frase de práctica con IA"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""Genera UNA frase de práctica para nivel {nivel}: {tema}

Formato EXACTO:
Inglés: [frase clara y natural]
Traducción: [significado en español]
Pronunciación: [guía fonética para hispanos]

Frase #{numero} - Dificultad progresiva del tema."""
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return resp.choices[0].message.content
    except:
        return f"Inglés: Hello, I am a student.\nTraducción: Hola, soy un estudiante.\nPronunciación: jelóu, ái am a stiúdent."

def generar_examen(nivel, tema):
    """Genera 5 preguntas de examen"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""Crea 5 preguntas de examen para {nivel}: {tema}

FORMATO EXACTO para cada pregunta:
P1: [pregunta en español]
RESPUESTA: [respuesta en inglés]

P2: [pregunta en español]
RESPUESTA: [respuesta en inglés]

(etc. hasta P5)

Valida dominio completo del tema."""
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        contenido = resp.choices[0].message.content
        
        # Parsear preguntas
        preguntas = []
        bloques = contenido.split('\n\n')
        
        for bloque in bloques:
            if 'P' in bloque and 'RESPUESTA:' in bloque:
                lineas = bloque.strip().split('\n')
                pregunta = ""
                respuesta = ""
                
                for linea in lineas:
                    if linea.startswith('P'):
                        pregunta = linea.split(':', 1)[1].strip()
                    elif 'RESPUESTA:' in linea:
                        respuesta = linea.split('RESPUESTA:', 1)[1].strip()
                
                if pregunta and respuesta:
                    preguntas.append({
                        "pregunta": pregunta,
                        "respuesta": respuesta
                    })
        
        return preguntas[:5]
    except:
        return [
            {"pregunta": "Di 'Hola' en inglés", "respuesta": "Hello"},
            {"pregunta": "Di 'Adiós' en inglés", "respuesta": "Goodbye"},
            {"pregunta": "Di 'Gracias' en inglés", "respuesta": "Thank you"},
            {"pregunta": "Di 'Por favor' en inglés", "respuesta": "Please"},
            {"pregunta": "Di 'Lo siento' en inglés", "respuesta": "I'm sorry"}
        ]

# ==================== INICIALIZACIÓN ====================

if "datos_cargados" not in st.session_state:
    datos = cargar_datos()
    for key, value in datos.items():
        st.session_state[key] = value
    st.session_state.last_audio_id = None
    st.session_state.datos_cargados = True

# Asegurar variables críticas
if "nivel_actual" not in st.session_state:
    st.session_state.nivel_actual = "A1.1"
if "frases_correctas" not in st.session_state:
    st.session_state.frases_correctas = 0
if "en_examen" not in st.session_state:
    st.session_state.en_examen = False
if "examen_actual" not in st.session_state:
    st.session_state.examen_actual = []
if "respuestas_examen" not in st.session_state:
    st.session_state.respuestas_examen = []
if "chat" not in st.session_state:
    st.session_state.chat = []
if "historial" not in st.session_state:
    st.session_state.historial = []

# ==================== VARIABLES DEL NIVEL ACTUAL ====================

nivel_actual = st.session_state.nivel_actual
config_nivel = CURRICULO[nivel_actual]
niveles_list = list(CURRICULO.keys())
indice_nivel = niveles_list.index(nivel_actual)
progreso_total = int((indice_nivel / len(CURRICULO)) * 100)

# ==================== BARRA LATERAL ====================

with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    
    # Métricas
    dias = (datetime.now() - datetime.fromisoformat(st.session_state.fecha_inicio)).days
    st.metric("📊 Progreso Total", f"{progreso_total}%")
    st.metric("📅 Días de Práctica", dias)
    st.metric("🎯 Nivel Actual", nivel_actual)
    
    st.divider()
    
    # Roadmap
    st.subheader("🗺️ Tu Camino al C1")
    
    for i, key in enumerate(niveles_list):
        tema = CURRICULO[key]["tema"]
        
        if i < indice_nivel:
            st.success(f"✅ {key}: {tema}")
        elif i == indice_nivel:
            st.info(f"🎯 {key}: {tema}")
        else:
            st.caption(f"🔒 {key}: {tema}")
    
    st.divider()
    
    # Historial
    if st.session_state.historial:
        st.subheader("📜 Últimos Logros")
        for logro in st.session_state.historial[-3:]:
            st.caption(f"✅ {logro['nivel']}: {logro['nota']:.0f}%")
    
    st.divider()
    
    if st.button("🗑️ Reiniciar Progreso", use_container_width=True):
        archivo = f"datos_{st.session_state.usuario_activo}.json"
        if os.path.exists(archivo):
            os.remove(archivo)
        st.session_state.clear()
        st.rerun()

# ==================== INTERFAZ PRINCIPAL ====================

st.title("🦅 Nexus Pro v3.0: Bootcamp Intensivo")
st.markdown(f"### 🎯 {nivel_actual}: {config_nivel['tema']}")

# Métricas del nivel
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Frases Completadas", f"{st.session_state.frases_correctas}/{config_nivel['frases']}")

with col2:
    progreso_nivel = int((st.session_state.frases_correctas / config_nivel['frases']) * 100)
    st.metric("Progreso Nivel", f"{progreso_nivel}%")

with col3:
    if st.session_state.en_examen:
        st.metric("Estado", "🔥 EXAMEN")
    else:
        st.metric("Estado", "📚 Práctica")

st.progress(progreso_nivel / 100)

# ==================== INICIAR CONVERSACIÓN ====================

if not st.session_state.chat:
    # Generar primera frase
    frase_contenido = generar_frase(nivel_actual, config_nivel['tema'], 1)
    
    # Extraer frase en inglés
    match = re.search(r'Inglés:\s*(.+?)(?:\n|$)', frase_contenido, re.IGNORECASE)
    audio_b64 = None
    
    if match:
        texto_ingles = match.group(1).strip()
        audio_b64 = generar_audio_ingles(texto_ingles)
    
    mensaje_inicial = f"""🦁 **¡Bienvenido a {nivel_actual}!**

**Tema:** {config_nivel['tema']}

Debes completar **{config_nivel['frases']} frases** con pronunciación correcta (≥80%).

Luego harás un **examen de 5 preguntas** (necesitas 100% para avanzar).

---

**📢 Frase 1/{config_nivel['frases']}:**

{frase_contenido}

🔊 **Escucha el audio de abajo**
🎤 **Luego repite con tu micrófono**"""
    
    msg = {"role": "assistant", "content": mensaje_inicial}
    if audio_b64:
        msg["audio"] = audio_b64
    
    st.session_state.chat.append(msg)
    guardar_datos()

# ==================== MOSTRAR CHAT ====================

for msg in st.session_state.chat:
    with st.chat_message(msg["role"], avatar="🦁" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])
        
        # Audio del usuario
        if "audio_usuario" in msg:
            st.audio(base64.b64decode(msg["audio_usuario"]), format="audio/wav")
        
        # Audio del profesor
        if "audio" in msg:
            st.markdown("🔊 **Audio de pronunciación:**")
            st.audio(base64.b64decode(msg["audio"]), format="audio/mp3")

# ==================== CONTROLES ====================

st.divider()

col_mic, col_text = st.columns([1, 5])

with col_mic:
    audio = mic_recorder(
        start_prompt="🎙️",
        stop_prompt="⏹️",
        key=f"mic_{len(st.session_state.chat)}"
    )

with col_text:
    texto = st.chat_input("💬 O escribe aquí...")

# ==================== PROCESAMIENTO DE AUDIO ====================

if audio and audio.get("id") != st.session_state.last_audio_id:
    st.session_state.last_audio_id = audio.get("id")
    
    with st.spinner("🎧 Analizando tu pronunciación..."):
        texto_usuario = transcribir_audio(audio['bytes'])
    
    if not texto_usuario:
        st.error("❌ No pude escuchar bien. Intenta de nuevo.")
        st.stop()
    
    # Guardar mensaje del usuario
    msg_usuario = {
        "role": "user",
        "content": f"🎤 **Dije:** {texto_usuario}",
        "audio_usuario": base64.b64encode(audio['bytes']).decode()
    }
    st.session_state.chat.append(msg_usuario)
    
    # ===== MODO PRÁCTICA =====
    if not st.session_state.en_examen:
        # Buscar frase objetivo en el último mensaje del asistente
        ultimo_asistente = None
        for msg in reversed(st.session_state.chat):
            if msg["role"] == "assistant":
                ultimo_asistente = msg["content"]
                break
        
        if ultimo_asistente:
            match = re.search(r'Inglés:\s*(.+?)(?:\n|$)', ultimo_asistente, re.IGNORECASE)
            
            # DEBUG TEMPORAL
            if not match:
                # Si no encuentra "Inglés:", buscar "Objetivo:"
                match = re.search(r'Objetivo:\s*(.+?)(?:\n|$)', ultimo_asistente, re.IGNORECASE)
            
            if match:
                frase_objetivo = match.group(1).strip()
                precision = similitud_texto(texto_usuario, frase_objetivo)
                
                # ===== PRONUNCIACIÓN CORRECTA =====
                if precision >= 80:  # Bajado de 85 a 80 para ser más justo
                    st.session_state.frases_correctas += 1
                    
                    # ¿Completó todas las frases?
                    if st.session_state.frases_correctas >= config_nivel['frases']:
                        # INICIAR EXAMEN
                        respuesta = f"""🎉 **¡EXCELENTE! Precisión: {precision}%**

✅ Has dominado las {config_nivel['frases']} frases

🔥 **EXAMEN FINAL**

Te haré 5 preguntas. Necesitas **5/5 correctas** para avanzar.

Prepara tu micrófono..."""
                        
                        st.session_state.chat.append({"role": "assistant", "content": respuesta})
                        
                        # Generar examen
                        with st.spinner("📝 Generando examen..."):
                            st.session_state.examen_actual = generar_examen(nivel_actual, config_nivel['tema'])
                            st.session_state.en_examen = True
                            st.session_state.respuestas_examen = []
                        
                        # Mostrar primera pregunta
                        if st.session_state.examen_actual:
                            p1 = st.session_state.examen_actual[0]
                            msg_pregunta = f"""📝 **Pregunta 1/5:**

{p1['pregunta']}

🎤 **Responde en inglés con tu micrófono**"""
                            
                            st.session_state.chat.append({"role": "assistant", "content": msg_pregunta})
                    
                    else:
                        # Siguiente frase
                        siguiente = st.session_state.frases_correctas + 1
                        frase_nueva = generar_frase(nivel_actual, config_nivel['tema'], siguiente)
                        
                        # Audio de la nueva frase
                        match_nueva = re.search(r'Inglés:\s*(.+?)(?:\n|$)', frase_nueva, re.IGNORECASE)
                        audio_nueva = None
                        if match_nueva:
                            audio_nueva = generar_audio_ingles(match_nueva.group(1).strip())
                        
                        respuesta = f"""✅ **¡CORRECTO! Precisión: {precision}%**

**Frase {siguiente}/{config_nivel['frases']}:**

{frase_nueva}

🔊 **Escucha y repite**"""
                        
                        msg_resp = {"role": "assistant", "content": respuesta}
                        if audio_nueva:
                            msg_resp["audio"] = audio_nueva
                        
                        st.session_state.chat.append(msg_resp)
                
                # ===== PRONUNCIACIÓN INCORRECTA =====
                else:
                    audio_correcto = generar_audio_ingles(frase_objetivo)
                    analisis = comparar_palabras(texto_usuario, frase_objetivo)
                    
                    respuesta = f"""❌ **Casi! Precisión: {precision}%** (Necesitas ≥80%)

**📊 Análisis palabra por palabra:**
{analisis}

💡 **Tip:** Enfócate en las palabras marcadas con ❌

🔊 **Escucha el audio de abajo** y compara con tu pronunciación.

🔄 **Graba de nuevo** cuando estés listo. ¡Intentos ilimitados!"""
                    
                    msg_error = {"role": "assistant", "content": respuesta}
                    if audio_correcto:
                        msg_error["audio"] = audio_correcto
                    
                    st.session_state.chat.append(msg_error)
            
            else:
                # No encontró la frase - error de parsing
                st.session_state.chat.append({
                    "role": "assistant",
                    "content": f"⚠️ Error interno. Dijiste: {texto_usuario}\n\n🔄 Intenta de nuevo o reinicia el nivel."
                })
    
    # ===== MODO EXAMEN =====
    else:
        num_pregunta = len(st.session_state.respuestas_examen)
        
        if num_pregunta < 5:
            pregunta_actual = st.session_state.examen_actual[num_pregunta]
            respuesta_correcta = pregunta_actual['respuesta']
            
            precision = similitud_texto(texto_usuario, respuesta_correcta)
            
            # Evaluar respuesta
            if precision >= 75:
                st.session_state.respuestas_examen.append(True)
                feedback = f"✅ **Respuesta {num_pregunta + 1}/5 - CORRECTA** ({precision}%)"
            else:
                st.session_state.respuestas_examen.append(False)
                feedback = f"❌ **Respuesta {num_pregunta + 1}/5 - INCORRECTA** ({precision}%)\n\n**Esperaba:** {respuesta_correcta}\n**Dijiste:** {texto_usuario}"
            
            st.session_state.chat.append({"role": "assistant", "content": feedback})
            
            # ¿Terminó el examen?
            if len(st.session_state.respuestas_examen) == 5:
                correctas = sum(st.session_state.respuestas_examen)
                nota = (correctas / 5) * 100
                
                # APROBADO
                if correctas == 5:
                    siguiente_idx = indice_nivel + 1
                    
                    if siguiente_idx < len(niveles_list):
                        siguiente_nivel = niveles_list[siguiente_idx]
                        
                        resultado = f"""🎊 **¡EXAMEN APROBADO!**

📊 **Nota: {nota:.0f}%** ({correctas}/5 correctas)

✅ Nivel {nivel_actual} COMPLETADO
🚀 Avanzando a **{siguiente_nivel}**

¡Sigue así! 💪"""
                        
                        # Registrar logro
                        st.session_state.historial.append({
                            "nivel": nivel_actual,
                            "nota": nota,
                            "fecha": datetime.now().isoformat()
                        })
                        
                        # Avanzar nivel
                        st.session_state.nivel_actual = siguiente_nivel
                        st.session_state.frases_correctas = 0
                        st.session_state.en_examen = False
                        st.session_state.examen_actual = []
                        st.session_state.respuestas_examen = []
                        st.session_state.chat = []
                        
                        st.balloons()
                    
                    else:
                        resultado = f"""🏆 **¡CERTIFICACIÓN C1 OBTENIDA!**

Has completado TODO el bootcamp.

🎓 **Eres bilingüe C1**

¡Felicitaciones! 🎉"""
                    
                    st.session_state.chat.append({"role": "assistant", "content": resultado})
                
                # REPROBADO
                else:
                    resultado = f"""😔 **Examen Reprobado**

📊 Nota: {nota:.0f}% ({correctas}/5)

Necesitabas 5/5 para avanzar.

🔄 Repetirás {nivel_actual}

💪 ¡No te rindas!"""
                    
                    st.session_state.chat.append({"role": "assistant", "content": resultado})
                    
                    # Reiniciar nivel
                    st.session_state.frases_correctas = 0
                    st.session_state.en_examen = False
                    st.session_state.examen_actual = []
                    st.session_state.respuestas_examen = []
                    st.session_state.chat = []
            
            # Mostrar siguiente pregunta
            elif len(st.session_state.respuestas_examen) < 5:
                siguiente_p = st.session_state.examen_actual[len(st.session_state.respuestas_examen)]
                
                msg_sig = f"""📝 **Pregunta {len(st.session_state.respuestas_examen) + 1}/5:**

{siguiente_p['pregunta']}

🎤 **Responde en inglés**"""
                
                st.session_state.chat.append({"role": "assistant", "content": msg_sig})
    
    guardar_datos()
    st.rerun()

# ===== PROCESAMIENTO DE TEXTO =====
elif texto:
    st.session_state.chat.append({"role": "user", "content": texto})
    
    if st.session_state.en_examen:
        st.session_state.chat.append({
            "role": "assistant",
            "content": "🎤 El examen requiere audio. Usa el micrófono."
        })
    else:
        st.session_state.chat.append({
            "role": "assistant",
            "content": "🎤 Por favor usa el micrófono para practicar pronunciación."
        })
    
    guardar_datos()
    st.rerun()
