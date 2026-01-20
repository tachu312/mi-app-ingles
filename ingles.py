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
    page_title="Nexus Pro v5.2: Elite Bootcamp",
    page_icon="🦅",
    layout="wide"
)

# --- INICIALIZACIÓN (SOLUCIONA EL ATTRIBUTEERROR) ---
def inicializar_estado():
    if "nivel_actual" not in st.session_state: st.session_state.nivel_actual = "A1.1"
    if "fase" not in st.session_state: st.session_state.fase = "explicacion"
    if "frase_actual" not in st.session_state: st.session_state.frase_actual = 0
    if "pregunta_actual" not in st.session_state: st.session_state.pregunta_actual = 0
    if "respuestas_correctas" not in st.session_state: st.session_state.respuestas_correctas = 0
    if "last_audio_id" not in st.session_state: st.session_state.last_audio_id = None
    if "usuario_activo" not in st.session_state: st.session_state.usuario_activo = None
    if "fecha_inicio" not in st.session_state: st.session_state.fecha_inicio = datetime.now().isoformat()

inicializar_estado()

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== 2. CURRÍCULO COMPLETO (A1 a C1) ====================
# Definimos todas las secciones para que el itinerario sea largo y profesional
CURRICULO = {}

# Generación automática de secciones para mostrar el itinerario completo
temas_a1 = ["Saludos", "Verbo To Be", "Artículos", "Números", "Colores", "Familia", "Rutinas", "Comida", "Ropa", "Certificación A1"]
temas_a2 = ["Pasado Simple", "Futuro Will", "Comparativos", "Preposiciones", "Habilidades", "Viajes", "Salud", "Experiencias", "Planes", "Certificación A2"]
temas_b1 = ["Presente Perfecto", "Voz Pasiva", "Condicionales", "Modales", "Trabajo", "Tecnología", "Opiniones", "Cultura", "Negocios", "Certificación B1"]

for i in range(1, 11):
    CURRICULO[f"A1.{i}"] = {"tema": temas_a1[i-1], "clase": "Lección de nivel A1.", "frases": [], "examen": []}
for i in range(1, 11):
    CURRICULO[f"A2.{i}"] = {"tema": temas_a2[i-1], "clase": "Lección de nivel A2.", "frases": [], "examen": []}
for i in range(1, 11):
    CURRICULO[f"B1.{i}"] = {"tema": temas_b1[i-1], "clase": "Lección de nivel B1.", "frases": [], "examen": []}
CURRICULO["C1.1"] = {"tema": "Dominio Avanzado", "clase": "Nivel Experto.", "frases": [], "examen": []}

# Agregamos datos reales al A1.1 para que puedas probarlo ya
CURRICULO["A1.1"]["clase"] = "En inglés, la 'H' suena como un suspiro frío. Di 'Hello' sin fuerza. Conecta: 'My name is' -> 'mainéimis'."
CURRICULO["A1.1"]["frases"] = [
    {"ingles": "Hello", "español": "Hola", "fonetica": "jelóu"},
    {"ingles": "My name is Anna", "español": "Mi nombre es Anna", "fonetica": "mai néim is ána"}
]
CURRICULO["A1.1"]["examen"] = [{"pregunta": "¿Cómo saludas?", "respuesta": "Hello"}]

# ==================== 3. LOGIN ====================
USUARIOS = {"nasly": "1994", "sofia": "2009", "andres": "1988"}
if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v5.2")
    u = st.text_input("👤 Usuario")
    p = st.text_input("🔒 Contraseña", type="password")
    if st.button("🚀 Entrar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.usuario_activo = u
            st.rerun()
        else: st.error("❌ Credenciales incorrectas")
    st.stop()

# ==================== 4. FUNCIONES IA ====================
def mentor_ia_explicar(objetivo, dicho):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"Profesor de inglés: El alumno dijo '{dicho}' para la frase '{objetivo}'. Explica en español y en una frase corta qué sonido o letra falló específicamente para no llegar al 100%."
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except: return "¡Casi perfecto! Presta atención a la última palabra."

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

# ==================== 5. BARRA LATERAL (ITINERARIO COMPLETO) ====================
niveles_list = list(CURRICULO.keys())
indice_actual = niveles_list.index(st.session_state.nivel_actual)

with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    st.metric("📊 Progreso General", f"{int((indice_actual/len(CURRICULO))*100)}%")
    st.divider()
    st.subheader("🗺️ Itinerario Completo")
    # Este bucle ahora muestra TODAS las secciones generadas arriba
    for k in niveles_list:
        if k == st.session_state.nivel_actual: st.info(f"🎯 {k}: {CURRICULO[k]['tema']}")
        elif niveles_list.index(k) < indice_actual: st.success(f"✅ {k}: {CURRICULO[k]['tema']}")
        else: st.caption(f"🔒 {k}: {CURRICULO[k]['tema']}")
    
    if st.button("🗑️ Reiniciar Sesión"):
        user = st.session_state.usuario_activo
        st.session_state.clear(); st.session_state.usuario_activo = user
        inicializar_estado(); st.rerun()

# ==================== 6. INTERFAZ DE CLASE ====================
st.title("🦅 Nexus Pro v5.2")
config = CURRICULO[st.session_state.nivel_actual]
st.markdown(f"## {st.session_state.nivel_actual}: {config['tema']}")

# --- FASE 1: EXPLICACIÓN ---
if st.session_state.fase == "explicacion":
    st.subheader("👨‍🏫 Clase Magistral")
    st.write(config['clase'])
    if st.button("✅ Comenzar Práctica", type="primary"):
        st.session_state.fase = "practica"; st.rerun()

# --- FASE 2: PRÁCTICA ---
elif st.session_state.fase == "practica":
    total_f = len(config['frases'])
    if total_f == 0: st.warning("Contenido en desarrollo."); st.stop()
    
    frase_obj = config['frases'][st.session_state.frase_actual]
    st.progress(st.session_state.frase_actual / total_f)
    st.subheader(f"Frase {st.session_state.frase_actual + 1}/{total_f}")
    
    st.info(f"📝 **Inglés:** {frase_obj['ingles']} \n\n 🇪🇸 **Español:** {frase_obj['español']} \n\n 🔊 **Pronunciación:** {frase_obj['fonetica']}")
    
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
                with st.expander("👨‍🏫 IA Mentor: ¿En qué fallaste?"):
                    st.write(mentor_ia_explicar(frase_obj['ingles'], res['texto']))
            if st.button("➡️ SIGUIENTE FRASE"):
                if st.session_state.frase_actual < total_f - 1: st.session_state.frase_actual += 1
                else: st.session_state.fase = "examen"; st.session_state.pregunta_actual = 0
                del st.session_state.res_practica; st.rerun()
        else: st.error(f"❌ Precisión insuficiente ({res['prec']}%)")

# --- FASE 3: EXAMEN ---
elif st.session_state.fase == "examen":
    # Lógica de examen para avanzar de nivel...
    st.success("Examen superado (Simulación).")
    if st.button("Ir al Siguiente Nivel"):
        if indice_actual < len(niveles_list) - 1:
            st.session_state.nivel_actual = niveles_list[indice_actual + 1]
            st.session_state.fase = "explicacion"
            st.session_state.frase_actual = 0; st.rerun()
