import streamlit as st
import openai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, re, json, os, base64
from datetime import datetime
from difflib import SequenceMatcher

# ==================== 1. CONFIGURACIÓN E INICIALIZACIÓN GLOBAL ====================
st.set_page_config(page_title="Nexus Pro v11.0: Global English Mastery", page_icon="🦅", layout="wide")

def inicializar_sistema():
    """Garantiza la estabilidad total del sistema y variables de memoria"""
    defaults = {
        "usuario_activo": None, "nivel_actual": "A1.1", "fase": "explicacion",
        "frase_actual": 0, "pregunta_actual": 0, "respuestas_correctas": 0,
        "examen_finalizado": False, "last_audio_id": None
    }
    for key, value in defaults.items():
        if key not in st.session_state: st.session_state[key] = value

inicializar_sistema()
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== 2. EL MAPA MAESTRO (ITINERARIO COMPLETO) ====================
ITINERARIO = {
    "A1": ["Saludos", "Identidad", "Familia", "Tiempo", "Hogar", "Comida", "Ropa", "Ciudad", "Clima", "Repaso A1"],
    "A2": ["Rutina", "Pasado", "Futuro", "Compras", "Salud", "Viajes", "Habilidades", "Experiencias", "Planes", "Certificación A2"],
    "B1": ["Trabajo", "Consejos", "Opiniones", "Cultura", "Relaciones", "Ambiente", "Tecnología", "Sueños", "Narración", "Certificación B1"],
    "B2": ["Debate", "Hipótesis", "Causas", "Conflictos", "Arte", "Ética", "Ciencia", "Historias", "Entrevistas", "Certificación B2"],
    "C1": ["Matices", "Ironía", "Argumentación", "Jerga", "Escritura", "Análisis", "Filosofía", "Persuasión", "Debate Pro", "MAESTRÍA FINAL"]
}

CURRICULO = {}
for nivel, temas in ITINERARIO.items():
    for i, tema in enumerate(temas, 1):
        CURRICULO[f"{nivel}.{i}"] = {"tema": tema, "clase": "", "frases": [], "examen": []}

# --- CONTENIDO DE ALTA CALIDAD PRE-CARGADO (NIVEL A1.1) ---
CURRICULO["A1.1"] = {
    "tema": "Saludos y Presentaciones",
    "clase": "Para sonar natural, conecta sonidos: 'My name is' suena 'mainéimis'. La 'H' en 'Hello' es un suspiro suave.",
    "frases": [
        {"ingles": "Hello, good morning", "español": "Hola, buenos días", "fonetica": "jelóu, gud mórnin"},
        {"ingles": "My name is David", "español": "Mi nombre es David", "fonetica": "mai néim is déivid"},
        {"ingles": "I am from Colombia", "español": "Soy de Colombia", "fonetica": "ái am from colómbia"},
        {"ingles": "It is nice to meet you", "español": "Es un gusto conocerte", "fonetica": "it is náis tu míit iu"},
        {"ingles": "How are you today?", "español": "¿Cómo estás hoy?", "fonetica": "jáu ar iu tudéi"},
        {"ingles": "I am fine, thank you", "español": "Estoy bien, gracias", "fonetica": "ái am fáin, zank iu"},
        {"ingles": "What is your name?", "español": "¿Cuál es tu nombre?", "fonetica": "uát is ior néim"},
        {"ingles": "Where are you from?", "español": "¿De dónde eres?", "fonetica": "uér ar iu from"},
        {"ingles": "Excuse me, please", "español": "Disculpe, por favor", "fonetica": "ekskiús mi, plíis"},
        {"ingles": "Goodbye, see you later", "español": "Adiós, nos vemos luego", "fonetica": "gudbái, si iu léiter"}
    ],
    "examen": [
        {"pregunta": "Saluda formalmente por la mañana", "respuesta": "Good morning"},
        {"pregunta": "Di: Mi nombre es...", "respuesta": "My name is"},
        {"pregunta": "Pregunta: ¿Cómo estás hoy?", "respuesta": "How are you today"},
        {"pregunta": "Responde: Estoy bien, gracias", "respuesta": "I am fine thank you"},
        {"pregunta": "Despídete: Nos vemos luego", "respuesta": "See you later"}
    ]
}

# ==================== 3. MOTOR DE GENERACIÓN INTELIGENTE ====================
def cargar_leccion_dinamica(nivel_key):
    if CURRICULO[nivel_key]["frases"]: return CURRICULO[nivel_key]
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    tema = CURRICULO[nivel_key]["tema"]
    prompt = f"Genera una lección de inglés nivel {nivel_key} sobre '{tema}'. JSON con 'clase', 10 'frases' y 5 'examen'."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}], response_format={"type": "json_object"})
        data = json.loads(resp.choices[0].message.content)
        CURRICULO[nivel_key].update(data)
        return CURRICULO[nivel_key]
    except: return CURRICULO["A1.1"]

# ==================== 4. LÓGICA DE AUDIO Y MENTORÍA ====================
def mentor_ia(objetivo, dicho):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Profesor de inglés: El alumno dijo '{dicho}' para '{objetivo}'. Explica brevemente en español qué sonido falló."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except: return "Sigue practicando la entonación."

def procesar_audio(audio_bytes, objetivo):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes); audio_file.name = "audio.wav"
        trans = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
        dicho = trans.text.strip()
        prec = int(SequenceMatcher(None, dicho.lower(), objetivo.lower()).ratio() * 100)
        return dicho, prec
    except: return "", 0

# ==================== 5. INTERFAZ Y NAVEGACIÓN ====================
if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v11.0")
    u = st.text_input("Usuario"); p = st.text_input("Contraseña", type="password")
    if st.button("🚀 Iniciar Bootcamp"):
        if u in {"nasly": "1994", "sofia": "2009", "andres": "1988"}:
            st.session_state.usuario_activo = u; st.rerun()
    st.stop()

niveles_list = list(CURRICULO.keys())
indice_actual = niveles_list.index(st.session_state.nivel_actual)
config = cargar_leccion_dinamica(st.session_state.nivel_actual)

with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    st.metric("📊 Progreso", f"{int((indice_actual/len(CURRICULO))*100)}%")
    st.divider(); st.subheader("🗺️ Itinerario Completo")
    for k in niveles_list:
        if k == st.session_state.nivel_actual: st.info(f"🎯 {k}: {CURRICULO[k]['tema']}")
        elif niveles_list.index(k) < indice_actual: st.success(f"✅ {k}: {CURRICULO[k]['tema']}")
        else: st.caption(f"🔒 {k}: {CURRICULO[k]['tema']}")

# ==================== 6. FASES DE APRENDIZAJE ====================
st.title(f"🦅 Nexus Pro: {st.session_state.nivel_actual}")

if st.session_state.fase == "explicacion":
    st.subheader("👨‍🏫 Clase Magistral")
    st.write(config['clase'])
    if st.button("🚀 Comenzar Práctica", type="primary"):
        st.session_state.fase = "practica"; st.rerun()

elif st.session_state.fase == "practica":
    total_f = len(config['frases'])
    frase_obj = config['frases'][st.session_state.frase_actual]
    st.progress(st.session_state.frase_actual / total_f)
    st.subheader(f"Frase {st.session_state.frase_actual + 1}/{total_f}")
    
    with st.container(border=True):
        st.write(f"🇬🇧 **{frase_obj['ingles']}**"); st.write(f"🇪🇸 {frase_obj['español']}")
        tts = gTTS(text=frase_obj['ingles'], lang='en'); fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0); st.audio(fp)

    audio_p = mic_recorder(start_prompt="🎙️ Grabar", key=f"p_{st.session_state.nivel_actual}_{st.session_state.frase_actual}")
    if audio_p and audio_p.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_p.get("id")
        dicho, prec = procesar_audio(audio_p['bytes'], frase_obj['ingles'])
        if dicho: st.session_state.res_practica = {"prec": prec, "texto": dicho}

    if "res_practica" in st.session_state:
        res = st.session_state.res_practica
        if res["prec"] >= 85:
            st.success(f"✅ ¡Correcto! ({res['prec']}%)")
            if st.button("➡️ Siguiente"):
                if st.session_state.frase_actual < total_f - 1: st.session_state.frase_actual += 1
                else: st.session_state.fase = "examen"; st.session_state.pregunta_actual = 0
                del st.session_state.res_practica; st.rerun()
        else: st.error(f"❌ Precisión insuficiente ({res['prec']}%)")

elif st.session_state.fase == "examen":
    total_ex = len(config['examen'])
    if st.session_state.examen_finalizado:
        if st.session_state.respuestas_correctas == total_ex:
            st.balloons(); st.success("🏆 ¡DOMINIO TOTAL!")
            if st.button("🚀 SIGUIENTE NIVEL"):
                st.session_state.nivel_actual = niveles_list[indice_actual + 1]
                st.session_state.fase = "explicacion"; st.session_state.examen_finalizado = False
                st.session_state.respuestas_correctas = 0; st.session_state.pregunta_actual = 0; st.rerun()
        else:
            st.error("Examen no superado. Repite la práctica."); st.session_state.fase = "practica"
            st.session_state.examen_finalizado = False; st.session_state.respuestas_correctas = 0; st.session_state.frase_actual = 0; st.rerun()
    else:
        pregunta = config['examen'][st.session_state.pregunta_actual]
        st.info(f"**Traduce:** {pregunta['pregunta']}")
        audio_ex = mic_recorder(start_prompt="🎙️ Responder", key=f"ex_{st.session_state.nivel_actual}_{st.session_state.pregunta_actual}")
        if audio_ex and audio_ex.get("id") != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio_ex.get("id")
            dicho, prec = procesar_audio(audio_ex['bytes'], pregunta['respuesta'])
            if dicho:
                correcta = prec >= 90
                if correcta: st.session_state.respuestas_correctas += 1
                st.session_state.res_examen = {"prec": prec, "texto": dicho, "correcta": correcta}
        
        if "res_examen" in st.session_state:
            if st.button("➡️ Continuar"):
                if st.session_state.pregunta_actual < total_ex - 1: st.session_state.pregunta_actual += 1
                else: st.session_state.examen_finalizado = True
                del st.session_state.res_examen; st.rerun()
