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
    page_title="Nexus Pro v4.2: Bootcamp A1→C1",
    page_icon="🦅",
    layout="wide"
)

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== USUARIOS ====================
USUARIOS = {"nasly": "1994", "sofia": "2009", "andres": "1988"}

if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v4.2")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("👤 Usuario")
        p = st.text_input("🔒 Contraseña", type="password")
        if st.button("🚀 Entrar al Bootcamp", use_container_width=True):
            if u in USUARIOS and USUARIOS[u] == p:
                st.session_state.usuario_activo = u
                st.rerun()
            else: st.error("❌ Credenciales incorrectas")
    st.stop()

# ==================== ITINERARIO Y CONTENIDO PROFESIONAL ====================
CURRICULO = {
    "A1.1": {
        "tema": "Saludos y Presentaciones",
        "explicacion": "👨‍🏫 **CLASE MAGISTRAL:** Aprende a conectar sonidos. En 'My name is', no pauses; intenta decir 'mainéimis'.",
        "frases": [
            {"ingles": "Hello", "español": "Hola", "fonetica": "jelóu"},
            {"ingles": "My name is Anna", "español": "Mi nombre es Anna", "fonetica": "mai néim is ána"},
            {"ingles": "I am from Colombia", "español": "Soy de Colombia", "fonetica": "ái am from colómbia"},
            {"ingles": "Nice to meet you", "español": "Mucho gusto", "fonetica": "náis tu míit iu"},
            {"ingles": "How are you", "español": "¿Cómo estás?", "fonetica": "jáu ar iu"},
            {"ingles": "I am fine thank you", "español": "Estoy bien gracias", "fonetica": "ái am fáin zank iu"},
            {"ingles": "Good morning", "español": "Buenos días", "fonetica": "gud mórnin"},
            {"ingles": "What is your name", "español": "¿Cuál es tu nombre?", "fonetica": "uát is ior néim"},
            {"ingles": "Where are you from", "español": "¿De dónde eres?", "fonetica": "uér ar iu from"},
            {"ingles": "Goodbye see you later", "español": "Adiós nos vemos luego", "fonetica": "gudbái si iu léiter"}
        ],
        "examen": [
            {"pregunta": "¿Cómo dices 'Hola' en inglés?", "respuesta": "Hello"},
            {"pregunta": "Di 'Mucho gusto' en inglés", "respuesta": "Nice to meet you"}
        ]
    },
    "A1.2": {
        "tema": "Verbo To Be (SER/ESTAR)",
        "explicacion": "👨‍🏫 **CLASE MAGISTRAL:** El verbo 'To Be' cambia según la persona: I am, You are, She is.",
        "frases": [
            {"ingles": "I am a student", "español": "Soy un estudiante", "fonetica": "ái am a stiúdent"},
            {"ingles": "She is happy", "español": "Ella está feliz", "fonetica": "shi is jápi"}
        ],
        "examen": [{"pregunta": "Di 'Soy un estudiante'", "respuesta": "I am a student"}]
    },
    "A1.3": {"tema": "Artículos y Pronombres", "frases": [], "examen": []},
    "A1.4": {"tema": "Números y Cantidades", "frases": [], "examen": []},
    "A1.5": {"tema": "Colores y Objetos", "frases": [], "examen": []},
    "A1.6": {"tema": "Familia y Relaciones", "frases": [], "examen": []}
}

# ==================== FUNCIONES DE APOYO PEDAGÓGICO ====================

def obtener_feedback_profesor(objetivo, dicho):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Profesor de inglés: El alumno dijo '{dicho}' para la frase '{objetivo}'. Explica en español y en una frase corta qué sonido falló para no llegar al 100%."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except: return "¡Casi perfecto! Cuida un poco más la entonación final."

def similitud_texto(texto1, texto2):
    t1 = re.sub(r'[^\w\s]', '', texto1.lower().strip())
    t2 = re.sub(r'[^\w\s]', '', texto2.lower().strip())
    return int(SequenceMatcher(None, t1, t2).ratio() * 100)

def transcribir_audio(audio_bytes):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        trans = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
        return trans.text.strip()
    except: return ""

def generar_audio_ingles(texto):
    try:
        tts = gTTS(text=texto, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode()
    except: return None

# ==================== INICIALIZACIÓN DE ESTADO ====================
if "usuario_activo" in st.session_state and "datos_cargados" not in st.session_state:
    st.session_state.nivel_actual = "A1.1"
    st.session_state.fase = "explicacion"
    st.session_state.frase_actual = 0
    st.session_state.pregunta_actual = 0
    st.session_state.respuestas_correctas = 0
    st.session_state.last_audio_id = None
    st.session_state.fecha_inicio = datetime.now().isoformat()
    st.session_state.datos_cargados = True

config = CURRICULO[st.session_state.nivel_actual]
niveles_list = list(CURRICULO.keys())
indice_actual = niveles_list.index(st.session_state.nivel_actual)

# ==================== BARRA LATERAL (ITINERARIO COMPLETO) ====================
with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    st.metric("📊 Progreso General", f"{int((indice_actual/len(CURRICULO))*100)}%")
    st.divider()
    st.subheader("🗺️ Itinerario de Temas")
    for k in niveles_list:
        if k == st.session_state.nivel_actual: st.info(f"🎯 {k}: {CURRICULO[k]['tema']}")
        elif niveles_list.index(k) < indice_actual: st.success(f"✅ {k}: {CURRICULO[k]['tema']}")
        else: st.caption(f"🔒 {k}: {CURRICULO[k]['tema']}")
    
    if st.button("🗑️ Reiniciar Todo"):
        user = st.session_state.usuario_activo
        st.session_state.clear()
        st.session_state.usuario_activo = user
        st.rerun()

# ==================== INTERFAZ PRINCIPAL ====================
st.title(f"🦅 Nexus Pro v4.2")
st.markdown(f"## {st.session_state.nivel_actual}: {config['tema']}")

# --- FASE 1: EXPLICACIÓN ---
if st.session_state.fase == "explicacion":
    st.markdown(config['explicacion'])
    if st.button("✅ Entendido, comenzar práctica", type="primary"):
        st.session_state.fase = "practica"
        st.rerun()

# --- FASE 2: PRÁCTICA ---
elif st.session_state.fase == "practica":
    total_f = len(config['frases'])
    frase_obj = config['frases'][st.session_state.frase_actual]
    st.progress(st.session_state.frase_actual / total_f)
    st.subheader(f"Frase {st.session_state.frase_actual + 1}/{total_f}")
    
    st.info(f"📝 **Inglés:** {frase_obj['ingles']} \n\n 🇪🇸 **Español:** {frase_obj['español']} \n\n 🔊 **Pronunciación:** {frase_obj['fonetica']}")
    
    audio_b = generar_audio_ingles(frase_obj['ingles'])
    if audio_b: st.audio(base64.b64decode(audio_b), format="audio/mp3")

    audio_p = mic_recorder(start_prompt="🎙️ Grabar", key=f"p_{st.session_state.frase_actual}")

    if audio_p and audio_p.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_p.get("id")
        texto = transcribir_audio(audio_p['bytes'])
        if texto:
            prec = similitud_texto(texto, frase_obj['ingles'])
            st.session_state.res_practica = {"prec": prec, "texto": texto}

    if "res_practica" in st.session_state:
        res = st.session_state.res_practica
        if res["prec"] >= 85:
            st.success(f"✅ ¡Correcto! ({res['prec']}%)")
            if res["prec"] < 100:
                with st.expander("👨‍🏫 Tip del Profesor para el 100%"):
                    st.write(obtener_feedback_profesor(frase_obj['ingles'], res['texto']))
            
            if st.button("➡️ SIGUIENTE FRASE", type="primary"):
                if st.session_state.frase_actual < total_f - 1:
                    st.session_state.frase_actual += 1
                else:
                    st.session_state.fase = "examen"
                    st.session_state.pregunta_actual = 0
                del st.session_state.res_practica
                st.rerun()
        else:
            st.error(f"❌ Precisión: {res['prec']}% (Mínimo 85%)")

# --- FASE 3: EXAMEN (CORRECCIÓN DE AVANCE DE NIVEL) ---
elif st.session_state.fase == "examen":
    total_ex = len(config['examen'])
    pregunta = config['examen'][st.session_state.pregunta_actual]
    st.subheader(f"📝 Examen Final: {st.session_state.pregunta_actual + 1}/{total_ex}")
    st.info(f"**{pregunta['pregunta']}**")
    
    audio_ex = mic_recorder(start_prompt="🎙️ Responder", key=f"ex_{st.session_state.pregunta_actual}")
    
    if audio_ex and audio_ex.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_ex.get("id")
        texto = transcribir_audio(audio_ex['bytes'])
        if texto:
            prec = similitud_texto(texto, pregunta['respuesta'])
            st.session_state.res_examen = {"prec": prec}
            if prec >= 75: st.session_state.respuestas_correctas += 1

    if "res_examen" in st.session_state:
        if st.button("➡️ CONTINUAR"):
            if st.session_state.pregunta_actual < total_ex - 1:
                st.session_state.pregunta_actual += 1
            else:
                # AQUÍ ESTÁ LA CORRECCIÓN CLAVE: AVANZAR AL SIGUIENTE NIVEL
                if st.session_state.respuestas_correctas == total_ex:
                    st.balloons()
                    st.success("¡NIVEL COMPLETADO!")
                    # Cambiar al siguiente nivel del diccionario CURRICULO
                    if indice_actual < len(niveles_list) - 1:
                        st.session_state.nivel_actual = niveles_list[indice_actual + 1]
                        st.session_state.fase = "explicacion"
                else:
                    st.error("Examen no superado. Repasemos la lección.")
                    st.session_state.fase = "explicacion"
                
                # Reset de contadores para el nuevo nivel o repetición
                st.session_state.frase_actual = 0
                st.session_state.pregunta_actual = 0
                st.session_state.respuestas_correctas = 0
            
            del st.session_state.res_examen
            st.rerun()
