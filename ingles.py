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

# Seguridad de API Key
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Falta OPENAI_API_KEY en st.secrets")
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

# ==================== CURRÍCULO (A1.1, A1.2, A1.3) ====================
CURRICULO = {
    "A1.1": {
        "tema": "Saludos y Presentaciones",
        "explicacion": """**📚 LECCIÓN: Saludos y Presentaciones**\nAprenderás formas básicas de saludar y presentarte.""",
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
            {"ingles": "You are my friend", "español": "Eres mi amigo", "fonética": "iú ar mai frend"}
        ],
        "examen": [
            {"pregunta": "Completa: I ___ a student", "respuesta": "am"}
        ]
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
        "nivel_actual": "A1.1", "fase": "explicacion",
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

# ==================== BARRA LATERAL ====================
with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    st.metric("🎯 Nivel", nivel_actual)
    if st.button("🗑️ Reiniciar"):
        archivo = f"datos_{st.session_state.usuario_activo}.json"
        if os.path.exists(archivo): os.remove(archivo)
        user = st.session_state.usuario_activo
        st.session_state.clear()
        st.session_state.usuario_activo = user
        st.rerun()

# ==================== INTERFAZ PRINCIPAL ====================
st.title("🦅 Nexus Pro v4.0")
st.markdown(f"### {nivel_actual}: {config['tema']}")

# --- FASE: EXPLICACIÓN ---
if st.session_state.fase == "explicacion":
    st.markdown(config['explicacion'])
    if st.button("✅ Ir a Práctica", type="primary"):
        st.session_state.fase = "practica"
        st.session_state.frase_actual = 0
        guardar_datos()
        st.rerun()

# --- FASE: PRÁCTICA (CORREGIDA) ---
elif st.session_state.fase == "practica":
    total_f = len(config['frases'])
    frase_obj = config['frases'][st.session_state.frase_actual]
    st.progress(st.session_state.frase_actual / total_f)
    
    st.info(f"**Frase {st.session_state.frase_actual + 1}/{total_f}:** {frase_obj['ingles']}\n\n({frase_obj['español']})")
    
    # Audio de guía
    audio_b64 = generar_audio_ingles(frase_obj['ingles'])
    if audio_b64: st.audio(base64.b64decode(audio_b64), format="audio/mp3")

    # Micrófono
    audio_p = mic_recorder(start_prompt="🎙️ Grabar", key=f"p_{st.session_state.frase_actual}")

    if audio_p and audio_p.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_p.get("id")
        with st.spinner("🎧 Analizando..."):
            texto = transcribir_audio(audio_p['bytes'])
        if texto:
            prec = similitud_texto(texto, frase_obj['ingles'])
            # GUARDAMOS RESULTADO EN SESSION_STATE
            st.session_state.res_practica = {"prec": prec, "texto": texto}

    # MOSTRAR RESULTADO Y BOTÓN FUERA DEL GRABADOR
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
                del st.session_state.res_practica # Limpiar para la siguiente
                guardar_datos()
                st.rerun()
        else:
            st.error(f"❌ Precisión baja ({res['prec']}%). Dijiste: {res['texto']}")
            st.info("🔄 Intenta de nuevo con el micrófono.")

# --- FASE: EXAMEN ---
elif st.session_state.fase == "examen":
    total_p = len(config['examen'])
    pregunta = config['examen'][st.session_state.pregunta_actual]
    st.progress(st.session_state.pregunta_actual / total_p)
    st.info(f"**Examen - Pregunta {st.session_state.pregunta_actual + 1}:** {pregunta['pregunta']}")

    audio_ex = mic_recorder(start_prompt="🎙️", key=f"ex_{st.session_state.pregunta_actual}")

    if audio_ex and audio_ex.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_ex.get("id")
        with st.spinner("🎧 Evaluando..."):
            texto = transcribir_audio(audio_ex['bytes'])
        if texto:
            prec = similitud_texto(texto, pregunta['respuesta'])
            st.session_state.res_examen = {"prec": prec, "texto": texto}
            if prec >= 70: st.session_state.respuestas_correctas += 1

    if "res_examen" in st.session_state:
        res = st.session_state.res_examen
        if res["prec"] >= 70: st.success("✅ Correcto")
        else: st.error(f"❌ Error. Era: {pregunta['respuesta']}")

        if st.button("➡️ CONTINUAR"):
            if st.session_state.pregunta_actual < total_p - 1:
                st.session_state.pregunta_actual += 1
            else:
                # Finalizar o Repetir
                if st.session_state.respuestas_correctas == total_p:
                    st.session_state.nivel_actual = niveles_list[indice + 1] if indice+1 < len(niveles_list) else nivel_actual
                    st.session_state.fase = "explicacion"
                    st.balloons()
                else:
                    st.session_state.fase = "explicacion"
                st.session_state.frase_actual = 0
                st.session_state.pregunta_actual = 0
                st.session_state.respuestas_correctas = 0
            
            del st.session_state.res_examen
            guardar_datos()
            st.rerun()
