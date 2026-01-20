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
    page_title="Nexus Pro v4.1: A1→C1 Elite Bootcamp",
    page_icon="🦅",
    layout="wide"
)

# Validación de API Key
if "OPENAI_API_KEY" not in st.secrets:
    st.error("⚠️ Configura 'OPENAI_API_KEY' en los Secrets de Streamlit.")
    st.stop()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== USUARIOS ====================
USUARIOS = {"nasly": "1994", "sofia": "2009", "andres": "1988"}

if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v4.1: Acceso")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("👤 Usuario")
        p = st.text_input("🔒 Contraseña", type="password")
        if st.button("🚀 Entrar al Sistema", use_container_width=True):
            if u in USUARIOS and USUARIOS[u] == p:
                st.session_state.usuario_activo = u
                st.rerun()
            else: st.error("❌ Credenciales incorrectas")
    st.stop()

# ==================== CURRÍCULO PROFESIONAL (10 FRASES ÚNICAS) ====================
CURRICULO = {
    "A1.1": {
        "tema": "Saludos y Presentaciones",
        "explicacion": """**👨‍🏫 CLASE MAGISTRAL: Saludos**
En inglés, la entonación es clave. No solo importa la palabra, sino cómo conectas los sonidos. 
- **Hello**: La 'H' suena como un suspiro suave.
- **My name is**: Evita separar las palabras; intenta que suene como 'mainéimis'.""",
        "frases": [
            {"ingles": "Hello", "español": "Hola", "fonetica": "jelóu"},
            {"ingles": "My name is Anna", "español": "Mi nombre es Anna", "fonetica": "mai néim is ána"},
            {"ingles": "I am from Colombia", "español": "Soy de Colombia", "fonetica": "ái am from colómbia"},
            {"ingles": "Nice to meet you", "español": "Mucho gusto", "fonetica": "náis tu míit iu"},
            {"ingles": "How are you today", "español": "¿Cómo estás hoy?", "fonetica": "jáu ar iu tudéi"},
            {"ingles": "I am fine thank you", "español": "Estoy bien gracias", "fonetica": "ái am fáin zank iu"},
            {"ingles": "Good morning teacher", "español": "Buenos días profesor", "fonetica": "gud mórnin tícher"},
            {"ingles": "What is your name", "español": "¿Cuál es tu nombre?", "fonetica": "uát is ior néim"},
            {"ingles": "Where do you live", "español": "¿Dónde vives?", "fonetica": "uér du iu liv"},
            {"ingles": "See you later friend", "español": "Nos vemos luego amigo", "fonetica": "síi iu léiter frend"}
        ],
        "examen": [
            {"pregunta": "¿Cómo dices 'Hola' de forma profesional?", "respuesta": "Hello"},
            {"pregunta": "¿Cómo preguntas '¿De dónde eres?'?", "respuesta": "Where are you from"}
        ]
    },
    "A1.2": {"tema": "Verbo To Be", "frases": [], "explicacion": "Cargando lección..."},
    "A1.3": {"tema": "Artículos", "frases": [], "explicacion": "Cargando lección..."}
}

# ==================== FUNCIONES DE IA Y APOYO ====================

def obtener_feedback_profesor(objetivo, dicho):
    """Usa GPT para explicar por qué no llegó al 100%"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""Actúa como un profesor de inglés nativo. 
La frase objetivo era: "{objetivo}". 
El alumno pronunció: "{dicho}".
Dile de forma muy breve y motivadora en qué falló específicamente para no llegar al 100% de precisión."""
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content
    except: return "¡Buen intento! Sigue practicando para perfeccionar el sonido."

def similitud_texto(texto1, texto2):
    t1 = re.sub(r'[^\w\s]', '', texto1.lower().strip())
    t2 = re.sub(r'[^\w\s]', '', texto2.lower().strip())
    return int(SequenceMatcher(None, t1, t2).ratio() * 100)

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

# ==================== ESTADO DE SESIÓN ====================
if "usuario_activo" in st.session_state and "datos_cargados" not in st.session_state:
    st.session_state.nivel_actual = "A1.1"
    st.session_state.fase = "explicacion"
    st.session_state.frase_actual = 0
    st.session_state.pregunta_actual = 0
    st.session_state.respuestas_correctas = 0
    st.session_state.last_audio_id = None
    st.session_state.datos_cargados = True

# ==================== BARRA LATERAL (PROFESIONAL) ====================
with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    st.metric("🎯 Nivel", st.session_state.nivel_actual)
    st.divider()
    st.subheader("🗺️ Itinerario")
    for k in CURRICULO.keys():
        if k == st.session_state.nivel_actual: st.info(f"🎯 {k}: {CURRICULO[k]['tema']}")
        else: st.caption(f"🔒 {k}: {CURRICULO[k]['tema']}")
    
    if st.button("🗑️ Reiniciar Sesión"):
        user = st.session_state.usuario_activo
        st.session_state.clear()
        st.session_state.usuario_activo = user
        st.rerun()

# ==================== INTERFAZ PRINCIPAL ====================
st.title("🦅 Nexus Pro v4.1")
config = CURRICULO[st.session_state.nivel_actual]

# --- FASE: EXPLICACIÓN ---
if st.session_state.fase == "explicacion":
    st.markdown(config['explicacion'])
    if st.button("✅ Entendido, comenzar práctica de 10 frases", type="primary"):
        st.session_state.fase = "practica"
        st.rerun()

# --- FASE: PRÁCTICA ---
elif st.session_state.fase == "practica":
    total_f = len(config['frases'])
    # CORRECCIÓN: Usar el índice frase_actual para obtener frases distintas
    frase_obj = config['frases'][st.session_state.frase_actual]
    
    st.progress(st.session_state.frase_actual / total_f)
    st.markdown(f"### Frase {st.session_state.frase_actual + 1}/{total_f}")
    
    st.info(f"""
📝 **Inglés:** {frase_obj['ingles']}  
🇪🇸 **Español:** {frase_obj['español']}  
🔊 **Pronunciación:** {frase_obj['fonetica']}
""")
    
    audio_b = generar_audio_ingles(frase_obj['ingles'])
    if audio_b: st.audio(base64.b64decode(audio_b), format="audio/mp3")

    audio_p = mic_recorder(start_prompt="🎙️ Grabar", key=f"p_{st.session_state.frase_actual}")

    if audio_p and audio_p.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_p.get("id")
        with st.spinner("🎧 Analizando..."):
            texto = transcribir_audio(audio_p['bytes'])
        if texto:
            prec = similitud_texto(texto, frase_obj['ingles'])
            st.session_state.res_practica = {"prec": prec, "texto": texto}

    if "res_practica" in st.session_state:
        res = st.session_state.res_practica
        if res["prec"] >= 85:
            st.success(f"✅ ¡Excelente! ({res['prec']}%)")
            # FEEDBACK DEL PROFESOR SI NO ES 100%
            if res["prec"] < 100:
                with st.expander("👨‍🏫 Tip del Profesor para el 100%"):
                    feedback = obtener_feedback_profesor(frase_obj['ingles'], res['texto'])
                    st.write(feedback)
            
            if st.button("➡️ SIGUIENTE FRASE", type="primary"):
                if st.session_state.frase_actual < total_f - 1:
                    st.session_state.frase_actual += 1
                else:
                    st.session_state.fase = "examen" # SALTO AL EXAMEN
                    st.session_state.pregunta_actual = 0
                del st.session_state.res_practica
                st.rerun()
        else:
            st.error(f"❌ Precisión: {res['prec']}% (Mínimo 85%)")
            st.warning(f"Dijiste: '{res['texto']}'")

# --- FASE: EXAMEN ---
elif st.session_state.fase == "examen":
    total_ex = len(config['examen'])
    pregunta = config['examen'][st.session_state.pregunta_actual]
    st.markdown(f"### 📝 Examen Final de Nivel: {st.session_state.pregunta_actual + 1}/{total_ex}")
    st.info(f"**{pregunta['pregunta']}**")
    
    audio_ex = mic_recorder(start_prompt="🎙️ Responder en Inglés", key=f"ex_{st.session_state.pregunta_actual}")
    
    if audio_ex and audio_ex.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_ex.get("id")
        texto = transcribir_audio(audio_ex['bytes'])
        if texto:
            prec = similitud_texto(texto, pregunta['respuesta'])
            st.session_state.res_examen = {"prec": prec, "texto": texto}
            if prec >= 75: st.session_state.respuestas_correctas += 1

    if "res_examen" in st.session_state:
        res = st.session_state.res_examen
        if res["prec"] >= 75: st.success("✅ Respuesta correcta")
        else: st.error(f"❌ Incorrecto. Se esperaba: {pregunta['respuesta']}")
        
        if st.button("➡️ CONTINUAR"):
            if st.session_state.pregunta_actual < total_ex - 1:
                st.session_state.pregunta_actual += 1
            else:
                st.balloons()
                st.success("¡NIVEL COMPLETADO!")
                st.session_state.fase = "explicacion"
                st.session_state.frase_actual = 0
                st.session_state.pregunta_actual = 0
            del st.session_state.res_examen
            st.rerun()
