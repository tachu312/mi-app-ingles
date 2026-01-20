import streamlit as st
import openai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import re
import json
import os
import base64

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Nexus Pro: C1 Bootcamp", page_icon="🦅", layout="wide")

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# --- 2. USUARIOS ---
USUARIOS = {"nasly": "1994", "sofia": "2009", "andres": "1988"}

if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro: Acceso Elite")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.usuario_activo = u
            st.rerun()
    st.stop()

# --- 3. PERSISTENCIA ---
ARCHIVO_DATOS = f"datos_{st.session_state.usuario_activo}.json"
CURRICULO = [
    "A1: Saludos y Presentaciones Básicas", 
    "A1: Verbo To Be (I am, You are)",
    "A2: Pasado Simple", 
    "B1: Fluidez Intermedia",
    "C1: Maestría Profesional"
]

def cargar():
    if os.path.exists(ARCHIVO_DATOS):
        with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f: return json.load(f)
    return {"progreso": 0, "chat": [], "frases_vistas": 0}

if "datos_cargados" not in st.session_state:
    d = cargar()
    st.session_state.update(d)
    st.session_state.last_audio_id = None
    st.session_state.datos_cargados = True

tema_actual = CURRICULO[st.session_state.progreso]
porcentaje = int((st.session_state.progreso / len(CURRICULO)) * 100)

# --- 4. BARRA LATERAL (MAPA DE RUTA) ---
with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    st.subheader("🗺️ Tu Mapa al C1")
    for i, tema in enumerate(CURRICULO):
        if i < st.session_state.progreso: st.success(f"✅ {tema}")
        elif i == st.session_state.progreso: st.info(f"🎯 {tema}")
        else: st.caption(f"🔒 {tema}")
    
    st.divider()
    if st.button("🗑️ REINICIAR ENTRENAMIENTO"):
        if os.path.exists(ARCHIVO_DATOS): os.remove(ARCHIVO_DATOS)
        st.session_state.clear(); st.rerun()

# --- 5. FUNCIONES IA ---
def transcribir(audio_bytes):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes); audio_file.name = "audio.wav"
        return client.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    except: return ""

def hablar_coach(prompt):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": f"""Eres un Coach PRO de inglés nivel A1. 
            REGLA DE ORO: Cada vez que enseñes una frase nueva, DEBES incluir obligatoriamente:
            1. Inglés: [Frase]
            2. Traducción: [Significado en español]
            3. Pronunciación: [Cómo suena para un hispano]
            
            Si el alumno lo dice bien, di 'CORRECTO' y da la siguiente frase con el mismo formato.
            Tras 3 frases correctas lanza examen A, B, C."""},
                      {"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content
    except Exception as e: return f"Error: {e}"

# --- 6. INTERFAZ ---
st.title("🦅 Nexus Pro: Entrenamiento de Alto Nivel")
st.markdown(f"### 🎯 Lección: {tema_actual}")
st.progress(porcentaje / 100)
st.write(f"Meta C1: {porcentaje}% completado")

# SALUDO AUTOMÁTICO
if not st.session_state.chat:
    msg_ini = hablar_coach(f"Inicia el tema: {tema_actual}. Da la primera frase con traducción.")
    st.session_state.chat.append({"role": "assistant", "content": msg_ini})

# MOSTRAR CHAT
for msg in st.session_state.chat:
    with st.chat_message(msg["role"], avatar="🦁" if msg["role"]=="assistant" else "👤"):
        st.write(msg["content"])
        if "audio_ver" in msg:
            st.audio(base64.b64decode(msg["audio_ver"]), format="audio/wav")
        if msg["role"] == "assistant":
            try:
                tts = gTTS(text=re.sub(r'[*#_`]', '', msg["content"]), lang='es', tld='com.mx')
                fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
                st.audio(fp.read(), format="audio/mp3")
            except: pass

# --- 7. CONTROLES ---
st.divider()
c1, c2 = st.columns([1, 5])
with c1: audio = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key=f"mic_{len(st.session_state.chat)}")
with c2: txt = st.chat_input("Responde aquí...")

if audio and audio.get("id") != st.session_state.last_audio_id:
    st.session_state.last_audio_id = audio.get("id")
    texto_voz = transcribir(audio['bytes'])
    user_msg = {"role": "user", "content": f"🎤 Dije: {texto_voz}" if texto_voz else "🎤 [Audio enviado]"}
    user_msg["audio_ver"] = base64.b64encode(audio['bytes']).decode()
    st.session_state.chat.append(user_msg)
    
    with st.spinner("Coach analizando..."):
        resp = hablar_coach(f"Dijo: {texto_voz}. Evalúa y da la siguiente frase con TRADUCCIÓN.")
        if "CORRECTO" in resp: st.session_state.frases_vistas += 1
        if "APROBADO-SIGUIENTE" in resp:
            st.balloons(); st.session_state.progreso += 1; st.session_state.frases_vistas = 0; st.session_state.chat = []
        else:
            st.session_state.chat.append({"role": "assistant", "content": resp})
    
    with open(ARCHIVO_DATOS, "w") as f:
        json.dump({"progreso": st.session_state.progreso, "chat": st.session_state.chat, "frases_vistas": st.session_state.frases_vistas}, f)
    st.rerun()

elif txt:
    st.session_state.chat.append({"role": "user", "content": txt})
    st.session_state.chat.append({"role": "assistant", "content": hablar_coach(f"El alumno dice: {txt}. Responde con traducción.")})

    st.rerun()


