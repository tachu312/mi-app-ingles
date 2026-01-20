import streamlit as st
import openai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io, re, json, os, base64
from datetime import datetime
from difflib import SequenceMatcher

# ==================== 1. CONFIGURACIÓN Y ESTADO BLINDADO ====================
st.set_page_config(page_title="Nexus Pro v9.5", page_icon="🦅", layout="wide")

def inicializar_sistema():
    variables = {
        "usuario_activo": None, "nivel_actual": "A1.1", "fase": "explicacion",
        "frase_actual": 0, "pregunta_actual": 0, "respuestas_correctas": 0,
        "examen_finalizado": False, "last_audio_id": None
    }
    for key, value in variables.items():
        if key not in st.session_state: st.session_state[key] = value

inicializar_sistema()
OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== 2. ITINERARIO COMPLETO (RESTAURADO) ====================
CURRICULO = {}
niveles = {
    "A1": ["Saludos", "Identidad", "Familia", "Tiempo", "Descripciones", "Hogar", "Comida", "Ropa", "Clima", "Repaso A1"],
    "A2": ["Rutinas", "Pasado", "Futuro", "Compras", "Salud", "Viajes", "Habilidades", "Experiencias", "Sentimientos", "Repaso A2"],
    "B1": ["Trabajo", "Consejos", "Opiniones", "Cultura", "Relaciones", "Ambiente", "Tecnología", "Sueños", "Narración", "Repaso B1"],
    "B2": ["Debate", "Hipótesis", "Causas", "Conflictos", "Arte", "Ética", "Ciencia", "Historias", "Entrevistas", "Repaso B2"],
    "C1": ["Matices", "Ironía", "Argumentación", "Jerga", "Escritura", "Análisis", "Filosofía", "Persuasión", "Debate Pro", "Certificación"]
}

for n, temas in niveles.items():
    for i, tema in enumerate(temas, 1):
        CURRICULO[f"{n}.{i}"] = {"tema": tema, "frases": [], "examen": []}

# CONTENIDO A1.1 (EJEMPLO PARA PRUEBAS)
CURRICULO["A1.1"]["clase"] = "En inglés, conecta los sonidos. 'My name is' suena como 'mainéimis'."
CURRICULO["A1.1"]["frases"] = [
    {"ingles": "Hello", "español": "Hola", "fonetica": "jelóu"},
    {"ingles": "My name is Anna", "español": "Mi nombre es Anna", "fonetica": "mai néim is ána"}
]
CURRICULO["A1.1"]["examen"] = [
    {"pregunta": "¿Cómo saludas formalmente?", "respuesta": "Hello"},
    {"pregunta": "Di 'Mucho gusto' en inglés", "respuesta": "Nice to meet you"}
]

# ==================== 3. LÓGICA DE EXAMEN PROFESIONAL ====================
def mentor_ia_examen(objetivo, dicho):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Profesor de inglés: El alumno dijo '{dicho}' pero la respuesta era '{objetivo}'. Explica brevemente en español qué sonido falló."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except: return "Casi lo logras. Revisa la pronunciación de las vocales."

def procesar_audio(audio_bytes, objetivo):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes); audio_file.name = "audio.wav"
        trans = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
        dicho = trans.text.strip()
        prec = int(SequenceMatcher(None, dicho.lower(), objetivo.lower()).ratio() * 100)
        return dicho, prec
    except: return "", 0

# ==================== 4. INTERFAZ Y NAVEGACIÓN ====================
if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v9.5")
    u = st.text_input("👤 Usuario"); p = st.text_input("🔒 Contraseña", type="password")
    if st.button("🚀 Entrar"):
        if u in {"nasly": "1994", "sofia": "2009", "andres": "1988"}:
            st.session_state.usuario_activo = u; st.rerun()
    st.stop()

niveles_list = list(CURRICULO.keys())
indice_actual = niveles_list.index(st.session_state.nivel_actual)

with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    st.metric("📊 Progreso", f"{int((indice_actual/len(CURRICULO))*100)}%")
    st.divider(); st.subheader("🗺️ Itinerario Elite")
    for k in niveles_list: # MOSTRANDO ITINERARIO COMPLETO SIN MODIFICAR
        if k == st.session_state.nivel_actual: st.info(f"🎯 {k}: {CURRICULO[k]['tema']}")
        elif niveles_list.index(k) < indice_actual: st.success(f"✅ {k}: {CURRICULO[k]['tema']}")
        else: st.caption(f"🔒 {k}: {CURRICULO[k]['tema']}")

# ==================== 5. EL AULA DE CLASE ====================
st.title("🦅 Nexus Pro: Aula de Aprendizaje")
config = CURRICULO[st.session_state.nivel_actual]

if st.session_state.fase == "explicacion":
    st.markdown(f"### {st.session_state.nivel_actual}: {config['tema']}")
    st.write(config.get('clase', 'Cargando lección...'))
    if st.button("🚀 Ir a la Práctica"):
        st.session_state.fase = "practica"; st.rerun()

elif st.session_state.fase == "practica":
    total_f = len(config['frases'])
    frase_obj = config['frases'][st.session_state.frase_actual]
    st.subheader(f"Práctica: Frase {st.session_state.frase_actual + 1}/{total_f}")
    st.info(f"📝 **Inglés:** {frase_obj['ingles']} | 🇪🇸 {frase_obj['español']}")
    
    audio_p = mic_recorder(start_prompt="🎙️ Grabar", key=f"p_{st.session_state.frase_actual}")
    if audio_p and audio_p.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio_p.get("id")
        dicho, prec = procesar_audio(audio_p['bytes'], frase_obj['ingles'])
        if dicho: st.session_state.res_practica = {"prec": prec, "texto": dicho}

    if "res_practica" in st.session_state:
        res = st.session_state.res_practica
        if res["prec"] >= 85:
            st.success(f"✅ ¡Bien hecho! ({res['prec']}%)")
            if st.button("➡️ SIGUIENTE"):
                if st.session_state.frase_actual < total_f - 1: st.session_state.frase_actual += 1
                else: st.session_state.fase = "examen"; st.session_state.pregunta_actual = 0
                del st.session_state.res_practica; st.rerun()
        else: st.error(f"❌ Intenta de nuevo ({res['prec']}%)")

# --- FASE EXAMEN: CORRECCIÓN DE FEEDBACK Y RESULTADOS ---
elif st.session_state.fase == "examen":
    total_ex = len(config['examen'])
    if st.session_state.examen_finalizado:
        # PANTALLA DE RESULTADOS FINALES (YA NO TE MANDA AL VACÍO)
        st.subheader("📊 Resultado Final del Examen")
        nota = (st.session_state.respuestas_correctas / total_ex) * 100
        st.metric("Puntaje", f"{nota:.0f}%", f"{st.session_state.respuestas_correctas}/{total_ex} correctas")

        if st.session_state.respuestas_correctas == total_ex:
            st.balloons(); st.success("🎊 ¡Felicidades! Has superado el nivel.")
            if st.button("🚀 IR AL SIGUIENTE NIVEL"):
                st.session_state.nivel_actual = niveles_list[indice_actual + 1]
                st.session_state.fase = "explicacion"; st.session_state.examen_finalizado = False
                st.session_state.respuestas_correctas = 0; st.session_state.pregunta_actual = 0; st.rerun()
        else:
            st.error("😔 No superaste el examen. Debes volver a empezar la Fase de Práctica.")
            if st.button("🔄 REINICIAR NIVEL"):
                st.session_state.fase = "practica"; st.session_state.examen_finalizado = False
                st.session_state.respuestas_correctas = 0; st.session_state.pregunta_actual = 0; st.session_state.frase_actual = 0; st.rerun()
    else:
        pregunta = config['examen'][st.session_state.pregunta_actual]
        st.subheader(f"📝 Examen: Pregunta {st.session_state.pregunta_actual + 1}/{total_ex}")
        st.info(f"**Traduce o responde:** {pregunta['pregunta']}")
        
        audio_ex = mic_recorder(start_prompt="🎙️ Responder", key=f"ex_{st.session_state.pregunta_actual}")
        if audio_ex and audio_ex.get("id") != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio_ex.get("id")
            dicho, prec = procesar_audio(audio_ex['bytes'], pregunta['respuesta'])
            if dicho:
                correcta = prec >= 75
                if correcta: st.session_state.respuestas_correctas += 1
                st.session_state.res_examen = {"prec": prec, "texto": dicho, "correcta": correcta}

        if "res_examen" in st.session_state:
            res = st.session_state.res_examen
            if res["correcta"]: st.success(f"✅ ¡Correcta! ({res['prec']}%)")
            else:
                st.error(f"❌ Incorrecta ({res['prec']}%)")
                with st.expander("👨‍🏫 Tip del Profesor"):
                    st.write(mentor_ia_examen(pregunta['respuesta'], res['texto']))
            
            if st.button("➡️ CONTINUAR"):
                if st.session_state.pregunta_actual < total_ex - 1: st.session_state.pregunta_actual += 1
                else: st.session_state.examen_finalizado = True
                del st.session_state.res_examen; st.rerun()
