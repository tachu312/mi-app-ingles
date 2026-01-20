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
    page_title="Nexus Pro v4.0: A1→C1 Bootcamp",
    page_icon="🦅",
    layout="wide"
)

if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Configura 'OPENAI_API_KEY' en los Secrets de Streamlit.")
    st.stop()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== USUARIOS ====================
USUARIOS = {"nasly": "1994", "sofia": "2009", "andres": "1988"}

if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v4.0")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("👤 Usuario")
        p = st.text_input("🔒 Contraseña", type="password")
        if st.button("🚀 Entrar", use_container_width=True):
            if u in USUARIOS and USUARIOS[u] == p:
                st.session_state.usuario_activo = u
                st.rerun()
            else: st.error("❌ Credenciales incorrectas")
    st.stop()

# ==================== CURRÍCULO COMPLETO ====================
CURRICULO = {
    "A1.1": {
        "tema": "Saludos y Presentaciones",
        "explicacion": """**📚 LECCIÓN: Saludos y Presentaciones**\nFormas básicas de saludar y presentarte.""",
        "frases": [
            {"ingles": "Hello", "español": "Hola", "fonética": "jelóu"},
            {"ingles": "My name is Anna", "español": "Mi nombre es Anna", "fonética": "mai néim is ána"},
            {"ingles": "I am from Colombia", "español": "Soy de Colombia", "fonética": "ái am from colómbia"},
            {"ingles": "Nice to meet you", "español": "Mucho gusto", "fonética": "náis tu míit iu"},
            {"ingles": "How are you", "español": "¿Cómo estás?", "fonética": "jáu ar iu"},
            {"ingles": "I am fine thank you", "español": "Estoy bien gracias", "fonética": "ái am fáin zank iu"},
            {"ingles": "Good morning", "español": "Buenos días", "fonética": "gud mórnin"},
            {"ingles": "What is your name", "español": "¿Cuál es tu nombre?", "fonética": "uát is ior néim"},
            {"ingles": "Where are you from", "español": "¿De dónde eres?", "fonética": "uér ar iu from"},
            {"ingles": "Goodbye see you later", "español": "Adiós nos vemos luego", "fonética": "gudbái si iu léiter"}
        ],
        "examen": [
            {"pregunta": "¿Cómo dices 'Hola' en inglés?", "respuesta": "Hello"},
            {"pregunta": "Di 'Mucho gusto' en inglés", "respuesta": "Nice to meet you"}
        ]
    },
    "A1.2": {
        "tema": "Verbo To Be (am/is/are)",
        "explicacion": """**📚 LECCIÓN: Verbo TO BE**\nSignifica SER o ESTAR.""",
        "frases": [
            {"ingles": "I am a student", "español": "Soy un estudiante", "fonética": "ái am a stiúdent"},
            {"ingles": "You are my friend", "español": "Eres mi amigo", "fonética": "iú ar mai frend"},
            {"ingles": "She is a teacher", "español": "Ella es una profesora", "fonética": "shi is a tícher"},
            {"ingles": "He is tall", "español": "Él es alto", "fonética": "ji is tol"},
            {"ingles": "It is a book", "español": "Es un libro", "fonética": "it is a buk"},
            {"ingles": "We are happy", "español": "Estamos felices", "fonética": "ui ar jápi"},
            {"ingles": "They are from Spain", "español": "Ellos son de España", "fonética": "déi ar from spéin"},
            {"ingles": "I am not tired", "español": "No estoy cansado", "fonética": "ái am not táired"},
            {"ingles": "Are you ready", "español": "¿Estás listo?", "fonética": "ar iú rédi"},
            {"ingles": "This is my house", "español": "Esta es mi casa", "fonética": "dis is mai jáus"}
        ],
        "examen": [{"pregunta": "Completa: I ___ a student", "respuesta": "am"}]
    }
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
        "nivel_actual": "A1.1", "fase": "practica",
        "frase_actual": 0, "pregunta_actual": 0,
        "respuestas_correctas": 0, "historial": [],
        "fecha_inicio": datetime.now().isoformat()
    }

def guardar_datos():
    archivo = f"datos_{st.session_state.usuario_activo}.json"
    datos = {
        "nivel_actual": st.session_state.nivel_actual, "fase": st.session_state.fase,
        "frase_actual": st.session_state.frase_actual, "pregunta_actual": st.session_state.pregunta_actual,
        "respuestas_correctas": st.session_state.respuestas_correctas,
        "historial": st.session_state.historial, "fecha_inicio": st.session_state.fecha_inicio
    }
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def transcribir_audio(audio_bytes):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        transcripcion = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, language="en"
        )
        return transcripcion.text.strip()
    except: return ""

def generar_audio_ingles(texto):
    try:
        tts = gTTS(text=texto, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode()
    except: return None

# ==================== INICIALIZACIÓN ====================
if "datos_cargados" not in st.session_state:
    datos = cargar_datos()
    for key, value in datos.items():
        st.session_state[key] = value
    st.session_state.last_audio_id = None
    st.session_state.datos_cargados = True

nivel_actual = st.session_state.nivel_actual
config = CURRICULO.get(nivel_actual, CURRICULO["A1.1"])
niveles_list = list(CURRICULO.keys())
indice = niveles_list.index(nivel_actual)
progreso_total = int((indice / len(CURRICULO)) * 100)

# ==================== BARRA LATERAL (RESTAURADA) ====================
with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    
    # Métricas de progreso originales
    dias = (datetime.now() - datetime.fromisoformat(st.session_state.fecha_inicio)).days
    st.metric("📊 Progreso Total", f"{progreso_total}%")
    st.metric("📅 Días de Práctica", dias)
    st.metric("🎯 Nivel Actual", nivel_actual)
    
    st.divider()
    st.subheader("🗺️ Itinerario")
    for i, key in enumerate(niveles_list):
        tema = CURRICULO[key]["tema"]
        if i < indice: st.success(f"✅ {key}: {tema}")
        elif i == indice: st.info(f"🎯 {key}: {tema}")
        else: st.caption(f"🔒 {key}: {tema}")
    
    if st.button("🗑️ Reiniciar Progreso"):
        archivo = f"datos_{st.session_state.usuario_activo}.json"
        if os.path.exists(archivo): os.remove(archivo)
        st.session_state.clear()
        st.rerun()

# ==================== INTERFAZ PRINCIPAL ====================
st.title("🦅 Nexus Pro v4.0")
st.markdown(f"## {nivel_actual}: {config['tema']}")

# --- FASE: PRÁCTICA (CORREGIDA PARA FRASES DINÁMICAS) ---
if st.session_state.fase == "practica":
    total_f = len(config['frases'])
    # AQUÍ ESTÁ EL CAMBIO CLAVE: Lee la frase según el índice frase_actual
    frase_obj = config['frases'][st.session_state.frase_actual]
    
    st.progress(st.session_state.frase_actual / total_f)
    st.markdown(f"### Frase {st.session_state.frase_actual + 1}/{total_f}")
    
    # CUADRO DETALLADO
    st.info(f"""
📝 **Inglés:** {frase_obj['ingles']}  
🇪🇸 **Español:** {frase_obj['español']}  
🔊 **Pronunciación:** {frase_obj['fonética']}
""")
    
    audio_b64 = generar_audio_ingles(frase_obj['ingles'])
    if audio_b64:
        st.markdown("🔊 **Escucha la pronunciación:**")
        st.audio(base64.b64decode(audio_b64), format="audio/mp3")

    # Micrófono con key única por frase para evitar bloqueos
    audio_p = mic_recorder(start_prompt="🎙️ Grabar", key=f"p_{nivel_actual}_{st.session_state.frase_actual}")

    if audio_p and audio_p.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_p.get("id")
        with st.spinner("🎧 Analizando..."):
            texto = transcribir_audio(audio_p['bytes'])
        if texto:
            prec = similitud_texto(texto, frase_obj['ingles'])
            st.session_state.res_practica = {"prec": prec, "texto": texto}

    # Mostrar resultado y botón de avance
    if "res_practica" in st.session_state:
        res = st.session_state.res_practica
        if res["prec"] >= 75:
            st.success(f"✅ ¡Excelente! ({res['prec']}%)")
            if st.button("➡️ SIGUIENTE FRASE", type="primary"):
                if st.session_state.frase_actual < total_f - 1:
                    st.session_state.frase_actual += 1
                else:
                    st.session_state.fase = "examen"
                    st.session_state.pregunta_actual = 0
                
                # Limpiar resultado para que la siguiente frase empiece limpia
                del st.session_state.res_practica
                guardar_datos()
                st.rerun()
        else:
            st.error(f"❌ Intenta de nuevo ({res['prec']}%). Dijiste: {res['texto']}")
