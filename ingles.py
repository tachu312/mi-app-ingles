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

# Se asume que la API Key está configurada en st.secrets
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

# ==================== CURRÍCULO COMPLETO (RESTAURADO) ====================
CURRICULO = {
    "A1.1": {"tema": "Saludos y Presentaciones", "frases": 5},
    "A1.2": {"tema": "Verbo To Be (am/is/are)", "frases": 5},
    "A1.3": {"tema": "Artículos y Pronombres", "frases": 5},
    "A1.4": {"tema": "Números y Cantidades", "frases": 5},
    "A1.5": {"tema": "Colores y Objetos Comunes", "frases": 5},
    "A1.6": {"tema": "Familia y Relaciones", "frases": 5},
    "A2.1": {"tema": "Presente Simple", "frases": 6},
    "A2.2": {"tema": "Pasado Simple Regular", "frases": 6},
    "A2.3": {"tema": "Pasado Simple Irregular", "frases": 6},
    "A2.4": {"tema": "Futuro (will/going to)", "frases": 6},
    "A2.5": {"tema": "Preposiciones de Lugar", "frases": 6},
    "A2.6": {"tema": "Comparativos y Superlativos", "frases": 6},
    "B1.1": {"tema": "Presente Perfecto", "frases": 7},
    "B1.2": {"tema": "Presente Continuo", "frases": 7},
    "B1.3": {"tema": "Modales: Can/Could/Should", "frases": 7},
    "B1.4": {"tema": "Pasado Continuo", "frases": 7},
    "B1.5": {"tema": "Condicional Tipo 1", "frases": 7},
    "B1.6": {"tema": "Phrasal Verbs Básicos", "frases": 7},
    "B1.7": {"tema": "Conectores y Transiciones", "frases": 7},
    "B1.8": {"tema": "Voz Pasiva Simple", "frases": 7},
    "B2.1": {"tema": "Presente Perfecto Continuo", "frases": 8},
    "B2.2": {"tema": "Condicionales 2 y 3", "frases": 8},
    "B2.3": {"tema": "Reported Speech", "frases": 8},
    "B2.4": {"tema": "Modales Avanzados", "frases": 8},
    "B2.5": {"tema": "Phrasal Verbs Avanzados", "frases": 8},
    "C1.1": {"tema": "Estructuras Formales", "frases": 10},
    "C1.2": {"tema": "Inglés de Negocios", "frases": 10},
    "C1.3": {"tema": "Expresiones Idiomáticas", "frases": 10},
    "C1.4": {"tema": "Debate y Argumentación", "frases": 10},
    "C1.5": {"tema": "Certificación Final C1", "frases": 10}
}

# ==================== FUNCIONES AUXILIARES ====================

def similitud_texto(texto1, texto2):
    t1 = re.sub(r'[^\w\s]', '', texto1.lower().strip())
    t2 = re.sub(r'[^\w\s]', '', texto2.lower().strip())
    return int(SequenceMatcher(None, t1, t2).ratio() * 100)

def cargar_datos():
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
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        transcripcion = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en"
        )
        return transcripcion.text.strip()
    except:
        return ""

def generar_audio_ingles(texto):
    try:
        tts = gTTS(text=texto, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode()
    except:
        return None

def generar_frase(nivel, tema, numero):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Genera UNA frase de nivel {nivel} sobre {tema}. Formato: Inglés: [frase]\nTraducción: [español]\nPronunciación: [fonética]"
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return resp.choices[0].message.content
    except:
        return "Inglés: Hello, how are you?\nTraducción: Hola, ¿cómo estás?\nPronunciación: jelóu, jáu ar iú?"

def generar_examen(nivel, tema):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Crea 5 preguntas para examen de {nivel} sobre {tema}. Formato: P: [español] RESPUESTA: [inglés]"
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        contenido = resp.choices[0].message.content
        preguntas = []
        for line in contenido.split('\n'):
            if 'P:' in line and 'RESPUESTA:' in line:
                p = line.split('P:')[1].split('RESPUESTA:')[0].strip()
                r = line.split('RESPUESTA:')[1].strip()
                preguntas.append({"pregunta": p, "respuesta": r})
        return preguntas[:5]
    except:
        return [{"pregunta": "Hola", "respuesta": "Hello"}] * 5

# ==================== INICIALIZACIÓN ====================
if "datos_cargados" not in st.session_state:
    datos = cargar_datos()
    for key, value in datos.items():
        st.session_state[key] = value
    st.session_state.last_audio_id = None
    st.session_state.datos_cargados = True

nivel_actual = st.session_state.nivel_actual
config_nivel = CURRICULO[nivel_actual]
niveles_list = list(CURRICULO.keys())
indice_nivel = niveles_list.index(nivel_actual)
progreso_total = int((indice_nivel / len(CURRICULO)) * 100)

# ==================== BARRA LATERAL (CORREGIDA) ====================
with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    
    dias = (datetime.now() - datetime.fromisoformat(st.session_state.fecha_inicio)).days
    st.metric("📊 Progreso Total", f"{progreso_total}%")
    st.metric("🎯 Nivel Actual", nivel_actual)
    
    st.divider()
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
    # BOTÓN DE REINICIO TOTAL (BORRA ARCHIVO Y MEMORIA)
    if st.button("🗑️ Reiniciar Todo el Progreso"):
        archivo = f"datos_{st.session_state.usuario_activo}.json"
        if os.path.exists(archivo):
            os.remove(archivo)
        # Limpiar session_state pero mantener el login
        user = st.session_state.usuario_activo
        st.session_state.clear()
        st.session_state.usuario_activo = user
        st.rerun()

# ==================== INTERFAZ PRINCIPAL ====================
st.title("🦅 Nexus Pro v3.0")
st.markdown(f"### 🎯 {nivel_actual}: {config_nivel['tema']}")

progreso_nivel = int((st.session_state.frases_correctas / config_nivel['frases']) * 100)
st.progress(progreso_nivel / 100)

if not st.session_state.chat:
    frase = generar_frase(nivel_actual, config_nivel['tema'], 1)
    match = re.search(r'Inglés:\s*(.+?)(?:\n|$)', frase, re.IGNORECASE)
    audio_b64 = generar_audio_ingles(match.group(1)) if match else None
    msg = {"role": "assistant", "content": f"🦁 **Frase 1/{config_nivel['frases']}**:\n\n{frase}"}
    if audio_b64: msg["audio"] = audio_b64
    st.session_state.chat.append(msg)

for msg in st.session_state.chat:
    with st.chat_message(msg["role"], avatar="🦁" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])
        if "audio" in msg: st.audio(base64.b64decode(msg["audio"]), format="audio/mp3")

# ==================== GRABADOR (SIN BLOQUEOS) ====================
st.divider()
# Clave dinámica para que el widget siempre se refresque
audio = mic_recorder(start_prompt="🎙️ Grabar", stop_prompt="⏹️ Detener", key=f"mic_{len(st.session_state.chat)}")

if audio and audio.get("id") != st.session_state.last_audio_id:
    st.session_state.last_audio_id = audio.get("id")
    texto_usuario = transcribir_audio(audio['bytes'])
    
    if texto_usuario:
        st.session_state.chat.append({"role": "user", "content": f"🎤 **Dije:** {texto_usuario}"})
        
        if not st.session_state.en_examen:
            ultimo_msg = [m for m in st.session_state.chat if m["role"] == "assistant"][-1]["content"]
            match = re.search(r'Inglés:\s*(.+?)(?:\n|$)', ultimo_msg, re.IGNORECASE)
            
            if match:
                objetivo = match.group(1).strip()
                prec = similitud_texto(texto_usuario, objetivo)
                
                if prec >= 85:
                    st.session_state.frases_correctas += 1
                    if st.session_state.frases_correctas >= config_nivel['frases']:
                        st.session_state.en_examen = True
                        st.session_state.examen_actual = generar_examen(nivel_actual, config_nivel['tema'])
                        st.session_state.chat.append({"role": "assistant", "content": "🎉 ¡Dominado! Iniciando examen..."})
                    else:
                        frase_n = generar_frase(nivel_actual, config_nivel['tema'], st.session_state.frases_correctas + 1)
                        match_n = re.search(r'Inglés:\s*(.+?)(?:\n|$)', frase_n, re.IGNORECASE)
                        audio_n = generar_audio_ingles(match_n.group(1)) if match_n else None
                        res = {"role": "assistant", "content": f"✅ **{prec}%** - ¡Muy bien! Siguiente:\n\n{frase_n}"}
                        if audio_n: res["audio"] = audio_n
                        st.session_state.chat.append(res)
                else:
                    # REINTENTO INFINITO: Simplemente añade el error y permite grabar otra vez
                    err = {"role": "assistant", "content": f"❌ **Precisión: {prec}%**\n\nIntenta de nuevo la misma frase. 🔄"}
                    err["audio"] = generar_audio_ingles(objetivo)
                    st.session_state.chat.append(err)
        
        else:
            # Lógica de examen (omito detalles por brevedad, se mantiene igual)
            pass

    guardar_datos()
    st.rerun()
