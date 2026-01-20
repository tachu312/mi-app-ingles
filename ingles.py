import streamlit as st
import openai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, re, json, os, base64
from datetime import datetime
from difflib import SequenceMatcher

# ==================== 1. CONFIGURACIÓN Y ESTADO BLINDADO ====================
st.set_page_config(page_title="Nexus Pro v9.0: English Elite System", page_icon="🦅", layout="wide")

def inicializar_sistema():
    variables = {
        "usuario_activo": None, "nivel_actual": "A1.1", "fase": "explicacion",
        "frase_actual": 0, "pregunta_actual": 0, "respuestas_correctas": 0,
        "examen_finalizado": False, "last_audio_id": None, "fecha_inicio": datetime.now().isoformat()
    }
    for key, value in variables.items():
        if key not in st.session_state: st.session_state[key] = value

inicializar_sistema()
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== 2. CURRÍCULO GENERAL (A1-C1) ====================
CURRICULO = {}
temas_base = {
    "A1": ["Saludos", "Identidad", "Familia", "Tiempo", "Descripciones", "Hogar", "Comida", "Ropa", "Clima", "Repaso A1"],
    "A2": ["Rutinas", "Pasado", "Futuro", "Compras", "Salud", "Viajes", "Habilidades", "Experiencias", "Sentimientos", "Repaso A2"],
    "B1": ["Trabajo", "Consejos", "Opiniones", "Cultura", "Relaciones", "Ambiente", "Tecnología", "Sueños", "Narración", "Repaso B1"]
}

for nivel, lista in temas_base.items():
    for i, tema in enumerate(lista, 1):
        CURRICULO[f"{nivel}.{i}"] = {"tema": tema, "clase": f"Dominio de {tema}.", "frases": [], "examen": []}

# Contenido A1.1 para pruebas reales
CURRICULO["A1.1"]["clase"] = "Para sonar profesional, conecta 'My name is' como 'mainéimis'. Suelta aire suave en la 'H' de 'Hello'."
CURRICULO["A1.1"]["frases"] = [
    {"ingles": "Hello", "español": "Hola", "fonetica": "jelóu"},
    {"ingles": "My name is Anna", "español": "Mi nombre es Anna", "fonetica": "mai néim is ána"}
]
CURRICULO["A1.1"]["examen"] = [
    {"pregunta": "¿Cómo saludas formalmente?", "respuesta": "Hello"},
    {"pregunta": "Di 'Mucho gusto' en inglés", "respuesta": "Nice to meet you"},
    {"pregunta": "¿Cómo preguntas el nombre?", "respuesta": "What is your name"},
    {"pregunta": "Di 'Soy de Colombia'", "respuesta": "I am from Colombia"},
    {"pregunta": "Di 'Ten un buen día'", "respuesta": "Have a nice day"}
]

# ==================== 3. MENTORÍA IA Y PROCESAMIENTO ====================
def mentor_ia_examen(objetivo, dicho):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Profesor de inglés: El alumno respondió '{dicho}' a la pregunta cuya respuesta era '{objetivo}'. Explica en español y en una frase corta qué sonido debe mejorar para que sea perfecto."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except: return "¡Casi! Intenta pronunciar con más claridad."

def procesar_audio(audio_bytes, objetivo):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes); audio_file.name = "audio.wav"
        trans = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
        dicho = trans.text.strip()
        t1 = re.sub(r'[^\w\s]', '', dicho.lower().strip())
        t2 = re.sub(r'[^\w\s]', '', objetivo.lower().strip())
        prec = int(SequenceMatcher(None, t1, t2).ratio() * 100)
        return dicho, prec
    except: return "", 0

# ==================== 4. INTERFAZ Y NAVEGACIÓN ====================
if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v9.0")
    u = st.text_input("👤 Usuario"); p = st.text_input("🔒 Contraseña", type="password")
    if st.button("🚀 Entrar"):
        if u in {"nasly": "1994", "sofia": "2009", "andres": "1988"}:
            st.session_state.usuario_activo = u; st.rerun()
        else: st.error("Acceso denegado")
    st.stop()

niveles_list = list(CURRICULO.keys())
indice_actual = niveles_list.index(st.session_state.nivel_actual)

with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    st.metric("📊 Progreso", f"{int((indice_actual/len(CURRICULO))*100)}%")
    st.divider()
    st.subheader("🗺️ Itinerario Elite")
    for k in niveles_list[:15]: # Muestra los primeros 15 por espacio
        if k == st.session_state.nivel_actual: st.info(f"🎯 {k}: {CURRICULO[k]['tema']}")
        elif niveles_list.index(k) < indice_actual: st.success(f"✅ {k}: {CURRICULO[k]['tema']}")
        else: st.caption(f"🔒 {k}: {CURRICULO[k]['tema']}")
    if st.button("🗑️ Reiniciar Sesión"):
        user = st.session_state.usuario_activo; st.session_state.clear()
        st.session_state.usuario_activo = user; inicializar_sistema(); st.rerun()

# ==================== 5. EL AULA DE CLASE ====================
st.title("🦅 Nexus Pro v9.0: Aula Elite")
config = CURRICULO[st.session_state.nivel_actual]
st.markdown(f"## {st.session_state.nivel_actual}: {config['tema']}")

# --- FASE 1: EXPLICACIÓN ---
if st.session_state.fase == "explicacion":
    st.subheader("👨‍🏫 Clase Magistral")
    st.write(config['clase'])
    if st.button("🚀 Ir a la Práctica", type="primary"):
        st.session_state.fase = "practica"; st.rerun()

# --- FASE 2: PRÁCTICA ---
elif st.session_state.fase == "practica":
    total_f = len(config['frases'])
    if total_f == 0: st.warning("Contenido pronto disponible."); st.stop()
    frase_obj = config['frases'][st.session_state.frase_actual]
    st.progress(st.session_state.frase_actual / total_f)
    st.subheader(f"Práctica: Frase {st.session_state.frase_actual + 1}/{total_f}")
    
    with st.container(border=True):
        st.write(f"📝 **Inglés:** {frase_obj['ingles']} | 🇪🇸 {frase_obj['español']}")
        st.caption(f"🔊 **Fonética:** {frase_obj['fonetica']}")
        tts = gTTS(text=frase_obj['ingles'], lang='en')
        fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0); st.audio(fp, format="audio/mp3")

    audio_p = mic_recorder(start_prompt="🎙️ Grabar Pronunciación", key=f"p_{st.session_state.frase_actual}")
    if audio_p and audio_p.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_p.get("id")
        dicho, prec = procesar_audio(audio_p['bytes'], frase_obj['ingles'])
        if dicho: st.session_state.res_practica = {"prec": prec, "texto": dicho}

    if "res_practica" in st.session_state:
        res = st.session_state.res_practica
        if res["prec"] >= 85:
            st.success(f"✅ ¡Excelente! ({res['prec']}%)")
            if st.button("➡️ SIGUIENTE"):
                if st.session_state.frase_actual < total_f - 1: st.session_state.frase_actual += 1
                else: st.session_state.fase = "examen"; st.session_state.pregunta_actual = 0
                del st.session_state.res_practica; st.rerun()
        else: st.error(f"❌ Precisión baja ({res['prec']}%). Intenta de nuevo.")

# --- FASE 3: EXAMEN PROFESIONAL (LÓGICA MEJORADA) ---
elif st.session_state.fase == "examen":
    total_ex = len(config['examen'])
    if st.session_state.examen_finalizado:
        # PANTALLA DE RESULTADOS FINALES
        nota = (st.session_state.respuestas_correctas / total_ex) * 100
        st.subheader("📊 Resultados del Examen")
        col1, col2 = st.columns(2)
        col1.metric("Correctas", f"{st.session_state.respuestas_correctas}/{total_ex}")
        col2.metric("Nota Final", f"{nota:.0f}%")

        if st.session_state.respuestas_correctas >= 4:
            st.balloons(); st.success("🎊 ¡Felicidades! Has superado el nivel.")
            if st.button("🚀 IR AL SIGUIENTE NIVEL", type="primary"):
                st.session_state.nivel_actual = niveles_list[indice_actual + 1]
                st.session_state.fase = "explicacion"; st.session_state.examen_finalizado = False
                st.session_state.respuestas_correctas = 0; st.session_state.pregunta_actual = 0; st.rerun()
        else:
            st.error("😔 No has alcanzado el mínimo (4/5). Debes repasar la práctica.")
            if st.button("🔄 REPETIR PRÁCTICA"):
                st.session_state.fase = "practica"; st.session_state.examen_finalizado = False
                st.session_state.respuestas_correctas = 0; st.session_state.pregunta_actual = 0; st.session_state.frase_actual = 0; st.rerun()
    else:
        # DESARROLLO DEL EXAMEN CON FEEDBACK
        pregunta = config['examen'][st.session_state.pregunta_actual]
        st.subheader(f"📝 Examen: Pregunta {st.session_state.pregunta_actual + 1}/{total_ex}")
        st.info(f"**Traduce o responde:** {pregunta['pregunta']}")
        
        audio_ex = mic_recorder(start_prompt="🎙️ Responder con Audio", key=f"ex_{st.session_state.pregunta_actual}")
        if audio_ex and audio_ex.get("id") != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio_ex.get("id")
            dicho, prec = procesar_audio(audio_ex['bytes'], pregunta['respuesta'])
            if dicho:
                es_correcta = prec >= 75
                if es_correcta: st.session_state.respuestas_correctas += 1
                st.session_state.res_examen = {"prec": prec, "texto": dicho, "correcta": es_correcta}

        if "res_examen" in st.session_state:
            res = st.session_state.res_examen
            if res["correcta"]: st.success(f"✅ Respuesta Correcta ({res['prec']}%)")
            else:
                st.error(f"❌ Incorrecta ({res['prec']}%)")
                with st.expander("👨‍🏫 Tip del Profesor"):
                    st.write(mentor_ia_examen(pregunta['respuesta'], res['texto']))
            
            if st.button("➡️ CONTINUAR"):
                if st.session_state.pregunta_actual < total_ex - 1:
                    st.session_state.pregunta_actual += 1
                else:
                    st.session_state.examen_finalizado = True
                del st.session_state.res_examen; st.rerun()
