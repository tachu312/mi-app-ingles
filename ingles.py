import streamlit as st
import openai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, re, json, os, base64
from datetime import datetime
from difflib import SequenceMatcher

# ==================== 1. CONFIGURACIÓN Y MEMORIA BLINDADA ====================
st.set_page_config(page_title="Nexus Pro v8.0: General English Mastery", page_icon="🦅", layout="wide")

def inicializar_sistema():
    """Garantiza que la app sea estable y profesional desde el inicio"""
    variables = {
        "usuario_activo": None, "nivel_actual": "A1.1", "fase": "explicacion",
        "frase_actual": 0, "pregunta_actual": 0, "respuestas_correctas": 0,
        "last_audio_id": None, "fecha_inicio": datetime.now().isoformat()
    }
    for key, value in variables.items():
        if key not in st.session_state: st.session_state[key] = value

inicializar_sistema()
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== 2. CURRÍCULO MAESTRO (A1-C1) ====================
# Estructura de 10 secciones por nivel con enfoque 100% conversacional
CURRICULO = {}
temas = {
    "A1": ["Saludos", "Identidad (To Be)", "Familia", "Números y Tiempo", "Descripción Física", "La Casa", "Comida Básica", "Ropa", "Clima", "Repaso A1"],
    "A2": ["Rutina Diaria", "Pasado Simple", "Planes Futuros", "Compras", "Salud", "Viajes", "Habilidades", "Experiencias", "Sentimientos", "Repaso A2"],
    "B1": ["Vida Laboral", "Consejos y Sugerencias", "Opiniones", "Cultura", "Relaciones", "Medio Ambiente", "Tecnología Humana", "Sueños", "Narración", "Repaso B1"],
    "B2": ["Debate Político", "Hipótesis (If)", "Causas y Efectos", "Resolución de Conflictos", "Arte y Sociedad", "Ética", "Ciencia", "Historias Complejas", "Entrevistas", "Repaso B2"],
    "C1": ["Matices del Idioma", "Ironía y Sarcasmo", "Argumentación Crítica", "Jerga Profesional", "Escritura Creativa", "Análisis Social", "Filosofía", "Persuasión", "Debate Avanzado", "Maestría Final"]
}

# Generación de la estructura robusta solicitada
for nivel, lista_temas in temas.items():
    for i in range(1, 11):
        CURRICULO[f"{nivel}.{i}"] = {
            "tema": lista_temas[i-1],
            "clase": f"Clase {nivel}.{i}: Dominando el tema de {lista_temas[i-1]} para la comunicación real.",
            "frases": [], "examen": []
        }

# --- CONTENIDO REAL DE INICIO (EJEMPLO A1.1) ---
CURRICULO["A1.1"]["clase"] = """**👨‍🏫 Clase Magistral: Conexiones Reales**
En inglés no hablamos cortado. 'My name is' suena como 'mainéimis'. 
La clave es el 'Linking' (unir palabras) para sonar natural en una conversación."""
CURRICULO["A1.1"]["frases"] = [
    {"ingles": "Hello", "español": "Hola", "fonetica": "jelóu"},
    {"ingles": "My name is Anna", "español": "Mi nombre es Anna", "fonetica": "mai néim is ána"},
    {"ingles": "How are you", "español": "¿Cómo estás?", "fonetica": "jáu ar iu"},
    {"ingles": "I am fine", "español": "Estoy bien", "fonetica": "ái am fáin"},
    {"ingles": "Nice to meet you", "español": "Mucho gusto", "fonetica": "náis tu míit iu"},
    {"ingles": "I am from Colombia", "español": "Soy de Colombia", "fonetica": "ái am from colómbia"},
    {"ingles": "Where are you from", "español": "¿De dónde eres?", "fonetica": "uér ar iu from"},
    {"ingles": "What is your name", "español": "¿Cuál es tu nombre?", "fonetica": "uát is ior néim"},
    {"ingles": "Have a nice day", "español": "Ten un lindo día", "fonetica": "jav a náis déi"},
    {"ingles": "Goodbye see you soon", "español": "Adiós nos vemos pronto", "fonetica": "gudbái si iu sún"}
]
CURRICULO["A1.1"]["examen"] = [
    {"pregunta": "¿Cómo saludas informalmente?", "respuesta": "Hello"},
    {"pregunta": "Preséntate: Mi nombre es...", "respuesta": "My name is"},
    {"pregunta": "Pregunta: ¿De dónde eres?", "respuesta": "Where are you from"},
    {"pregunta": "Di 'Mucho gusto'", "respuesta": "Nice to meet you"},
    {"pregunta": "Despídete formalmente", "respuesta": "Goodbye"}
]

# ==================== 3. MOTOR DE MENTORÍA IA PROFESIONAL ====================
def mentor_ia_pedagogico(objetivo, dicho):
    """Analiza la pronunciación y explica el error como un profesor humano"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""Eres un profesor de inglés paciente. El alumno dijo '{dicho}' para la frase '{objetivo}'.
    Explica en español qué sonido falló (ej: la lengua, la vibración de las cuerdas vocales o la unión de palabras) 
    para que logre el 100%. Sé breve y profesional."""
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except: return "¡Muy cerca! Intenta conectar más las palabras y soltar aire suave en la letra H."

def transcribir_y_comparar(audio_bytes, objetivo):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes); audio_file.name = "audio.wav"
        trans = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
        dicho = trans.text.strip()
        # Similitud
        t1 = re.sub(r'[^\w\s]', '', dicho.lower().strip())
        t2 = re.sub(r'[^\w\s]', '', objetivo.lower().strip())
        prec = int(SequenceMatcher(None, t1, t2).ratio() * 100)
        return dicho, prec
    except: return "", 0

# ==================== 4. INTERFAZ Y NAVEGACIÓN (FLUJO CORREGIDO) ====================
if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v8.0")
    u = st.text_input("👤 Usuario"); p = st.text_input("🔒 Contraseña", type="password")
    if st.button("🚀 Iniciar Bootcamp"):
        if u in {"nasly": "1994", "sofia": "2009", "andres": "1988"}:
            st.session_state.usuario_activo = u; st.rerun()
        else: st.error("Acceso denegado")
    st.stop()

niveles_list = list(CURRICULO.keys())
indice_actual = niveles_list.index(st.session_state.nivel_actual)

with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    st.metric("📊 Progreso General", f"{int((indice_actual/len(CURRICULO))*100)}%")
    st.divider()
    st.subheader("🗺️ Itinerario Completo")
    for k in niveles_list:
        if k == st.session_state.nivel_actual: st.info(f"🎯 {k}: {CURRICULO[k]['tema']}")
        elif niveles_list.index(k) < indice_actual: st.success(f"✅ {k}: {CURRICULO[k]['tema']}")
        else: st.caption(f"🔒 {k}: {CURRICULO[k]['tema']}")
    if st.button("🗑️ Reiniciar Sesión"):
        user = st.session_state.usuario_activo; st.session_state.clear()
        st.session_state.usuario_activo = user; inicializar_sistema(); st.rerun()

# ==================== 5. EL AULA VIRTUAL ====================
st.title("🦅 Nexus Pro v8.0: Aula Elite")
config = CURRICULO[st.session_state.nivel_actual]
st.markdown(f"## {st.session_state.nivel_actual}: {config['tema']}")

# --- FASE 1: EXPLICACIÓN ---
if st.session_state.fase == "explicacion":
    st.subheader("👨‍🏫 Clase Magistral")
    st.write(config['clase'])
    if st.button("✅ Ir a la Práctica de 10 Frases", type="primary"):
        st.session_state.fase = "practica"; st.rerun()

# --- FASE 2: PRÁCTICA CON MENTORÍA IA ---
elif st.session_state.fase == "practica":
    total_f = len(config['frases'])
    if total_f == 0: st.warning("Contenido pronto disponible."); st.stop()
    
    frase_obj = config['frases'][st.session_state.frase_actual]
    st.progress(st.session_state.frase_actual / total_f)
    st.subheader(f"Frase {st.session_state.frase_actual + 1}/{total_f}")
    
    with st.container(border=True):
        st.write(f"📝 **Inglés:** {frase_obj['ingles']}")
        st.write(f"🇪🇸 **Español:** {frase_obj['español']}")
        st.caption(f"🔊 **Fonética:** {frase_obj['fonetica']}")
        tts = gTTS(text=frase_obj['ingles'], lang='en')
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0); st.audio(fp, format="audio/mp3")

    audio_p = mic_recorder(start_prompt="🎙️ Grabar Pronunciación", key=f"p_{st.session_state.frase_actual}")
    
    if audio_p and audio_p.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_p.get("id")
        dicho, prec = transcribir_y_comparar(audio_p['bytes'], frase_obj['ingles'])
        if dicho:
            st.session_state.res_practica = {"prec": prec, "texto": dicho}

    if "res_practica" in st.session_state:
        res = st.session_state.res_practica
        if res["prec"] >= 85:
            st.success(f"✅ ¡Excelente! ({res['prec']}%)")
            if res["prec"] < 100:
                with st.expander("👨‍🏫 ¿Por qué no saqué 100%?"):
                    st.write(mentor_ia_pedagogico(frase_obj['ingles'], res['texto']))
            if st.button("➡️ SIGUIENTE FRASE"):
                if st.session_state.frase_actual < total_f - 1:
                    st.session_state.frase_actual += 1
                else:
                    st.session_state.fase = "examen"; st.session_state.pregunta_actual = 0
                del st.session_state.res_practica; st.rerun()
        else: st.error(f"❌ Intenta de nuevo ({res['prec']}%). Escucha el audio guía.")

# --- FASE 3: EXAMEN DE CERTIFICACIÓN ---
elif st.session_state.fase == "examen":
    total_ex = len(config['examen'])
    if total_ex == 0: st.success("Nivel superado."); st.stop()
    pregunta = config['examen'][st.session_state.pregunta_actual]
    st.subheader(f"📝 Examen: Pregunta {st.session_state.pregunta_actual + 1}/{total_ex}")
    st.info(f"**Traduce o responde en inglés:** {pregunta['pregunta']}")
    
    audio_ex = mic_recorder(start_prompt="🎙️ Responder con Audio", key=f"ex_{st.session_state.pregunta_actual}")
    if audio_ex and audio_ex.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_ex.get("id")
        dicho, prec = transcribir_y_comparar(audio_ex['bytes'], pregunta['respuesta'])
        if dicho:
            st.session_state.res_examen = {"prec": prec, "texto": dicho}
            if prec >= 75: st.session_state.respuestas_correctas += 1

    if "res_examen" in st.session_state:
        if st.button("➡️ CONTINUAR"):
            if st.session_state.pregunta_actual < total_ex - 1:
                st.session_state.pregunta_actual += 1
            else:
                if st.session_state.respuestas_correctas >= 4:
                    st.balloons(); st.success("🎊 ¡Nivel Superado!"); st.session_state.nivel_actual = niveles_list[indice_actual + 1]
                st.session_state.fase = "explicacion"; st.session_state.frase_actual = 0; st.session_state.pregunta_actual = 0; st.session_state.respuestas_correctas = 0
            del st.session_state.res_examen; st.rerun()
