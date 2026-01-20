import streamlit as st
import openai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import re
import base64
from datetime import datetime
from difflib import SequenceMatcher

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="Nexus Pro v4.3: Bootcamp A1→C1",
    page_icon="🦅",
    layout="wide"
)

# Cargar API Key desde secretos
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    st.error("Falta la OPENAI_API_KEY en los secretos de Streamlit.")
    st.stop()

# ==================== USUARIOS ====================
USUARIOS = {"nasly": "1994", "sofia": "2009", "andres": "1988"}

if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v4.3")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("👤 Usuario").lower()
        p = st.text_input("🔒 Contraseña", type="password")
        if st.button("🚀 Entrar al Bootcamp", use_container_width=True):
            if u in USUARIOS and USUARIOS[u] == p:
                st.session_state.usuario_activo = u
                st.rerun()
            else: st.error("❌ Credenciales incorrectas")
    st.stop()

# ==================== ITINERARIO MAESTRO (A1 -> C1) ====================
# He estructurado las claves para que el sistema las ordene automáticamente
CURRICULO = {
    "A1.1": {
        "tema": "Saludos y Presentaciones",
        "explicacion": "👨‍🏫 **Clase 1.1:** Enfócate en la 'H' aspirada (como un suspiro) y en unir 'My name is' como una sola palabra.",
        "frases": [
            {"ingles": "Hello", "español": "Hola", "fonetica": "jelóu"},
            {"ingles": "My name is Andres", "español": "Mi nombre es Andres", "fonetica": "mai néim is ándres"},
            {"ingles": "I am from Colombia", "español": "Soy de Colombia", "fonetica": "ái am from colómbia"},
            {"ingles": "Nice to meet you", "español": "Mucho gusto", "fonetica": "náis tu míit iu"},
            {"ingles": "What is your name", "español": "¿Cuál es tu nombre?", "fonetica": "uát is ior néim"}
        ],
        "examen": [
            {"pregunta": "Saluda y di tu nombre", "respuesta": "Hello my name is Andres"},
            {"pregunta": "Di 'Mucho gusto'", "respuesta": "Nice to meet you"}
        ]
    },
    "A1.2": {
        "tema": "Verbo To Be y Estados",
        "explicacion": "👨‍🏫 **Clase 1.2:** El verbo 'To Be' es ser o estar. Pronuncia la 'm' final de 'I am' cerrando los labios.",
        "frases": [
            {"ingles": "I am a student", "español": "Soy un estudiante", "fonetica": "ái am a stiúdent"},
            {"ingles": "She is happy", "español": "Ella está feliz", "fonetica": "shi is jápi"},
            {"ingles": "We are ready", "español": "Estamos listos", "fonetica": "uí ar rédi"}
        ],
        "examen": [{"pregunta": "Di 'Soy un estudiante'", "respuesta": "I am a student"}]
    },
    # Marcadores de posición para niveles superiores (Se pueden llenar progresivamente)
    "B1.1": {"tema": "Experiencias (Present Perfect)", "explicacion": "Uso de 'Have' como auxiliar.", "frases": [{"ingles": "I have traveled a lot", "español": "He viajado mucho", "fonetica": "ái jav trávuled a lot"}], "examen": []},
    "C1.1": {"tema": "Modismos Avanzados", "explicacion": "Lenguaje figurado y naturalidad.", "frases": [{"ingles": "Let's call it a day", "español": "Terminemos por hoy", "fonetica": "lets col it a déi"}], "examen": []}
}

# ==================== FUNCIONES DE LÓGICA Y IA ====================

def obtener_feedback_estricto(objetivo, dicho):
    """Profesor IA que explica por qué no se llegó al 100%"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""Actúa como un profesor de fonética inglesa EXTREMADAMENTE ESTRICTO.
    Frase correcta: '{objetivo}'
    Frase dicha: '{dicho}'
    
    Explica en español y en máximo 2 frases qué sonido exacto falló o qué palabra se omitió. 
    Sé técnico (ej. 'La d final desapareció', 'La vocal fue muy cerrada')."""
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except: return "No fue perfecto. Escucha el audio guía y repite con precisión."

def similitud_texto(texto1, texto2):
    """Calcula precisión ignorando puntuación y mayúsculas"""
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

# ==================== GESTIÓN DE ESTADO ====================
if "datos_cargados" not in st.session_state:
    st.session_state.nivel_actual = "A1.1"
    st.session_state.fase = "explicacion"
    st.session_state.frase_actual = 0
    st.session_state.pregunta_actual = 0
    st.session_state.respuestas_correctas = 0
    st.session_state.last_audio_id = None
    st.session_state.datos_cargados = True

config = CURRICULO.get(st.session_state.nivel_actual, CURRICULO["A1.1"])
niveles_list = sorted(list(CURRICULO.keys()))
indice_nivel = niveles_list.index(st.session_state.nivel_actual)

# ==================== BARRA LATERAL ====================
with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    progreso = int((indice_nivel / len(CURRICULO)) * 100)
    st.metric("📊 Progreso General", f"{progreso}%")
    st.divider()
    st.subheader("🗺️ Itinerario del Bootcamp")
    for k in niveles_list:
        if k == st.session_state.nivel_actual: st.info(f"🎯 {k}: {CURRICULO[k]['tema']}")
        elif niveles_list.index(k) < indice_nivel: st.success(f"✅ {k}: {CURRICULO[k]['tema']}")
        else: st.caption(f"🔒 {k}: {CURRICULO[k]['tema']}")
    
    if st.button("🗑️ Reiniciar Todo"):
        user = st.session_state.usuario_activo
        st.session_state.clear()
        st.session_state.usuario_activo = user
        st.rerun()

# ==================== INTERFAZ PRINCIPAL ====================
st.title("🦅 Nexus Pro v4.3")
st.markdown(f"### {st.session_state.nivel_actual}: {config['tema']}")

# --- FASE 1: EXPLICACIÓN ---
if st.session_state.fase == "explicacion":
    st.markdown(config.get('explicacion', "Comencemos con esta lección."))
    if st.button("✅ Entendido, ir a práctica (100% requerido)", type="primary"):
        st.session_state.fase = "practica"
        st.rerun()

# --- FASE 2: PRÁCTICA (MODO ESTRICTO) ---
elif st.session_state.fase == "practica":
    frases = config['frases']
    total_f = len(frases)
    
    if st.session_state.frase_actual < total_f:
        frase_obj = frases[st.session_state.frase_actual]
        st.progress(st.session_state.frase_actual / total_f)
        st.subheader(f"Frase {st.session_state.frase_actual + 1} de {total_f}")
        
        # UI de Frase
        with st.container(border=True):
            st.write(f"🇬🇧 **Inglés:** ### {frase_obj['ingles']}")
            st.write(f"🇪🇸 **Español:** {frase_obj['español']}")
            st.caption(f"🔊 Pronunciación: {frase_obj['fonetica']}")
        
        # Audio Guía
        audio_b = generar_audio_ingles(frase_obj['ingles'])
        if audio_b: st.audio(base64.b64decode(audio_b), format="audio/mp3")

        # Grabadora
        audio_p = mic_recorder(start_prompt="🎙️ Grabar Pronunciación", key=f"p_{st.session_state.nivel_actual}_{st.session_state.frase_actual}")

        if audio_p and audio_p.get("id") != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio_p.get("id")
            transcripcion = transcribir_audio(audio_p['bytes'])
            if transcripcion:
                prec = similitud_texto(transcripcion, frase_obj['ingles'])
                st.session_state.resultado_vocal = {"prec": prec, "texto": transcripcion}

        # Validación Estricta
        if "resultado_vocal" in st.session_state:
            res = st.session_state.resultado_vocal
            if res["prec"] == 100:
                st.success("🎯 **¡EXCELENTE! 100% de precisión.**")
                if st.button("➡️ SIGUIENTE FRASE", type="primary"):
                    st.session_state.frase_actual += 1
                    del st.session_state.resultado_vocal
                    st.rerun()
            else:
                st.error(f"❌ Precisión: {res['prec']}%. No puedes avanzar sin el 100%.")
                st.markdown("#### 👨‍🏫 Corrección técnica:")
                feedback = obtener_feedback_estricto(frase_obj['ingles'], res['texto'])
                st.info(feedback)
                st.caption(f"Dijiste: '{res['texto']}'. Inténtalo de nuevo.")
    else:
        st.session_state.fase = "examen"
        st.rerun()

# --- FASE 3: EXAMEN ---
elif st.session_state.fase == "examen":
    examen_preguntas = config.get('examen', [])
    if not examen_preguntas: # Si no hay examen definido, saltar al siguiente nivel
        st.session_state.respuestas_correctas = 5 
    else:
        total_ex = len(examen_preguntas)
        if st.session_state.pregunta_actual < total_ex:
            pregunta = examen_preguntas[st.session_state.pregunta_actual]
            st.subheader(f"📝 Certificación: {st.session_state.pregunta_actual + 1}/{total_ex}")
            st.info(f"**Pregunta:** {pregunta['pregunta']}")
            
            audio_ex = mic_recorder(start_prompt="🎙️ Responder en Inglés", key=f"ex_{st.session_state.pregunta_actual}")
            
            if audio_ex and audio_ex.get("id") != st.session_state.last_audio_id:
                st.session_state.last_audio_id = audio_ex.get("id")
                texto_ex = transcribir_audio(audio_ex['bytes'])
                if texto_ex:
                    prec_ex = similitud_texto(texto_ex, pregunta['respuesta'])
                    if prec_ex >= 85: 
                        st.session_state.respuestas_correctas += 1
                        st.success("✅ Respuesta aceptada")
                    else: 
                        st.error(f"❌ Respuesta incorrecta o mala pronunciación ({prec_ex}%)")
                    
                    if st.button("Continuar"):
                        st.session_state.pregunta_actual += 1
                        st.rerun()
            st.stop()

    # Resultados del Examen e Incremento de Nivel
    if st.session_state.respuestas_correctas >= (len(examen_preguntas) * 0.8):
        st.balloons()
        st.success("🎊 ¡Felicidades! Has dominado este nivel.")
        if st.button("🚀 SUBIR AL SIGUIENTE NIVEL"):
            if indice_nivel < len(niveles_list) - 1:
                st.session_state.nivel_actual = niveles_list[indice_nivel + 1]
            st.session_state.fase = "explicacion"
            st.session_state.frase_actual = 0
            st.session_state.pregunta_actual = 0
            st.session_state.respuestas_correctas = 0
            st.rerun()
    else:
        st.error("No has alcanzado el puntaje mínimo en el examen.")
        if st.button("🔄 Reintentar Lección"):
            st.session_state.fase = "explicacion"
            st.session_state.frase_actual = 0
            st.session_state.pregunta_actual = 0
            st.session_state.respuestas_correctas = 0
            st.rerun()
