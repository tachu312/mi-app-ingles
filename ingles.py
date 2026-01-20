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

# ==================== 1. CONFIGURACIÓN E INICIALIZACIÓN BLINDADA ====================
st.set_page_config(
    page_title="Nexus Pro v5.1: Bootcamp Elite",
    page_icon="🦅",
    layout="wide"
)

# --- FUNCIÓN DE INICIALIZACIÓN (EVITA EL ATTRIBUTEERROR) ---
def inicializar_todo():
    if "usuario_activo" not in st.session_state:
        st.session_state.usuario_activo = None
    if "nivel_actual" not in st.session_state:
        st.session_state.nivel_actual = "A1.1"
    if "fase" not in st.session_state:
        st.session_state.fase = "explicacion"
    if "frase_actual" not in st.session_state:
        st.session_state.frase_actual = 0
    if "pregunta_actual" not in st.session_state:
        st.session_state.pregunta_actual = 0
    if "respuestas_correctas" not in st.session_state:
        st.session_state.respuestas_correctas = 0
    if "last_audio_id" not in st.session_state:
        st.session_state.last_audio_id = None
    if "fecha_inicio" not in st.session_state:
        st.session_state.fecha_inicio = datetime.now().isoformat()

inicializar_todo()

# Validación de API Key
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Configura 'OPENAI_API_KEY' en los Secrets.")
    st.stop()
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== 2. CURRÍCULO ROBUSTO (10 SECCIONES POR NIVEL) ====================
CURRICULO = {
    # NIVEL A1: 10 SECCIONES
    "A1.1": {
        "tema": "Saludos y Presentaciones",
        "clase": "Aprende a conectar sonidos: 'My name is' debe sonar como 'mainéimis'.",
        "frases": [
            {"ingles": "Hello", "español": "Hola", "fonetica": "jelóu"},
            {"ingles": "My name is Anna", "español": "Mi nombre es Anna", "fonetica": "mai néim is ána"},
            {"ingles": "I am from Colombia", "español": "Soy de Colombia", "fonetica": "ái am from colómbia"},
            {"ingles": "Nice to meet you", "español": "Mucho gusto", "fonetica": "náis tu míit iu"},
            {"ingles": "How are you today", "español": "¿Cómo estás hoy?", "fonetica": "jáu ar iu tudéi"},
            {"ingles": "I am fine thank you", "español": "Estoy bien gracias", "fonetica": "ái am fáin zank iu"},
            {"ingles": "What is your name", "español": "¿Cuál es tu nombre?", "fonetica": "uát is ior néim"},
            {"ingles": "I live in a big city", "español": "Vivo en una ciudad grande", "fonetica": "ái liv in a big síti"},
            {"ingles": "It is a pleasure to meet you", "español": "Es un placer conocerte", "fonetica": "it is a pléshur tu míit iu"},
            {"ingles": "Goodbye see you soon", "español": "Adiós nos vemos pronto", "fonetica": "gudbái si iu sún"}
        ],
        "examen": [
            {"pregunta": "¿Cómo saludas?", "respuesta": "Hello"},
            {"pregunta": "Di 'Mucho gusto'", "respuesta": "Nice to meet you"},
            {"pregunta": "¿Cómo pides el nombre?", "respuesta": "What is your name"},
            {"pregunta": "Di 'Soy de Colombia'", "respuesta": "I am from Colombia"},
            {"pregunta": "Di 'Es un placer conocerte'", "respuesta": "It is a pleasure to meet you"}
        ]
    },
    "A1.2": {"tema": "Verbo To Be y Estados", "frases": [], "examen": []},
    "A1.3": {"tema": "Artículos y Pronombres", "frases": [], "examen": []},
    "A1.4": {"tema": "Números y Cantidades", "frases": [], "examen": []},
    "A1.5": {"tema": "Colores y Adjetivos", "frases": [], "examen": []},
    "A1.6": {"tema": "Familia y Relaciones", "frases": [], "examen": []},
    "A1.7": {"tema": "Rutinas Diarias", "frases": [], "examen": []},
    "A1.8": {"tema": "Comida y Restaurantes", "frases": [], "examen": []},
    "A1.9": {"tema": "Ropa y Compras", "frases": [], "examen": []},
    "A1.10": {"tema": "Certificación Final A1", "frases": [], "examen": []},
    # NIVEL A2...
    "A2.1": {"tema": "Pasado Simple", "frases": [], "examen": []},
}

# ==================== 3. LOGIN ====================
USUARIOS = {"nasly": "1994", "sofia": "2009", "andres": "1988"}

if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v5.1")
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

# ==================== 4. FUNCIONES IA ====================
def obtener_feedback_profesor(objetivo, dicho):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Profesor de inglés: El alumno dijo '{dicho}' para la frase '{objetivo}'. Explica en español corto qué sonido falló para no llegar al 100%."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except: return "¡Casi perfecto! Cuida la última palabra."

def similitud_texto(texto1, texto2):
    t1 = re.sub(r'[^\w\s]', '', texto1.lower().strip())
    t2 = re.sub(r'[^\w\s]', '', texto2.lower().strip())
    return int(SequenceMatcher(None, t1, t2).ratio() * 100)

def transcribir_audio(audio_bytes):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes); audio_file.name = "audio.wav"
        trans = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
        return trans.text.strip()
    except: return ""

def generar_audio_guia(texto):
    try:
        tts = gTTS(text=texto, lang='en')
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
        return base64.b64encode(fp.read()).decode()
    except: return None

# ==================== 5. INTERFAZ Y PROGRESO ====================
config = CURRICULO.get(st.session_state.nivel_actual)
niveles_list = list(CURRICULO.keys())
indice_actual = niveles_list.index(st.session_state.nivel_actual)

with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    st.metric("📊 Progreso General", f"{int((indice_actual/len(CURRICULO))*100)}%")
    st.divider()
    st.subheader("🗺️ Itinerario A1→C1")
    for k in niveles_list:
        if k == st.session_state.nivel_actual: st.info(f"🎯 {k}: {CURRICULO[k]['tema']}")
        elif niveles_list.index(k) < indice_actual: st.success(f"✅ {k}: {CURRICULO[k]['tema']}")
        else: st.caption(f"🔒 {k}: {CURRICULO[k]['tema']}")
    
    if st.button("🗑️ Reiniciar Sesión"):
        user = st.session_state.usuario_activo
        st.session_state.clear(); st.session_state.usuario_activo = user
        inicializar_todo(); st.rerun()

# ==================== 6. ÁREA DE CLASE ====================
st.title("🦅 Nexus Pro v5.1")
st.markdown(f"## {st.session_state.nivel_actual}: {config['tema']}")

# --- FASE 1: EXPLICACIÓN ---
if st.session_state.fase == "explicacion":
    st.subheader("👨‍🏫 Clase Magistral")
    st.write(config['clase'])
    if st.button("✅ Comenzar Práctica de 10 frases", type="primary"):
        st.session_state.fase = "practica"; st.rerun()

# --- FASE 2: PRÁCTICA ---
elif st.session_state.fase == "practica":
    total_f = len(config['frases'])
    if total_f == 0: st.warning("Contenido en preparación."); st.stop()
    
    frase_obj = config['frases'][st.session_state.frase_actual]
    st.progress(st.session_state.frase_actual / total_f)
    st.subheader(f"Frase {st.session_state.frase_actual + 1}/{total_f}")
    
    st.info(f"📝 **Inglés:** {frase_obj['ingles']} \n\n 🇪🇸 **Español:** {frase_obj['español']} \n\n 🔊 **Pronunciación:** {frase_obj['fonetica']}")
    
    audio_b = generar_audio_guia(frase_obj['ingles'])
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
            st.success(f"✅ ¡Logrado! ({res['prec']}%)")
            if res["prec"] < 100:
                with st.expander("👨‍🏫 Mentoría IA (Feedback)"):
                    st.write(obtener_feedback_profesor(frase_obj['ingles'], res['texto']))
            if st.button("➡️ SIGUIENTE FRASE"):
                if st.session_state.frase_actual < total_f - 1: st.session_state.frase_actual += 1
                else: st.session_state.fase = "examen"; st.session_state.pregunta_actual = 0
                del st.session_state.res_practica; st.rerun()
        else: st.error(f"❌ Precisión insuficiente ({res['prec']}%)")

# --- FASE 3: EXAMEN ---
elif st.session_state.fase == "examen":
    total_ex = len(config['examen'])
    pregunta = config['examen'][st.session_state.pregunta_actual]
    st.subheader(f"📝 Examen: {st.session_state.pregunta_actual + 1}/{total_ex}")
    st.info(f"**Pregunta:** {pregunta['pregunta']}")
    
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
            if st.session_state.pregunta_actual < total_ex - 1: st.session_state.pregunta_actual += 1
            else:
                if st.session_state.respuestas_correctas >= 4:
                    st.balloons(); st.success("🎊 ¡NIVEL COMPLETADO!")
                    if indice_actual < len(niveles_list) - 1:
                        st.session_state.nivel_actual = niveles_list[indice_actual + 1]
                        st.session_state.fase = "explicacion"
                else: st.error("No pasaste. Repite."); st.session_state.fase = "explicacion"
                st.session_state.frase_actual = 0; st.session_state.pregunta_actual = 0; st.session_state.respuestas_correctas = 0
            del st.session_state.res_examen; st.rerun()
