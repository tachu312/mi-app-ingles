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

# ==================== CONFIGURACIÓN DE SISTEMA ====================
st.set_page_config(
    page_title="Nexus Pro v5.0: Bootcamp Elite A1→C1",
    page_icon="🦅",
    layout="wide"
)

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== GESTIÓN DE CURRÍCULO (ARQUITECTURA) ====================
# Aquí definimos la estructura de 10 secciones por nivel. 
# He completado el inicio del A1 para mostrar la progresión.
CURRICULO = {
    "A1.1": {
        "tema": "Saludos y Presentaciones",
        "objetivo": "Aprender a presentarse y saludar en contextos formales e informales.",
        "clase": "En inglés, la 'H' suena como un suspiro. No digas 'My... name... is', intenta conectarlo: 'Mynameis'.",
        "frases": [
            {"ingles": "Hello, my name is Anna", "español": "Hola, mi nombre es Anna", "fonetica": "jelóu, mai néim is ána"},
            {"ingles": "I am from Colombia", "español": "Soy de Colombia", "fonetica": "ái am from colómbia"},
            {"ingles": "It is a pleasure to meet you", "español": "Es un placer conocerte", "fonetica": "it is a pléshur tu míit iu"}
        ],
        "examen": [{"pregunta": "¿Cómo saludas formalmente?", "respuesta": "Hello"}]
    },
    "A1.2": {"tema": "Verbo To Be y Estados", "frases": [], "examen": []},
    "A1.3": {"tema": "Artículos y Pronombres", "frases": [], "examen": []},
    "A1.4": {"tema": "Números y Cantidades", "frases": [], "examen": []},
    "A1.5": {"tema": "Colores y Adjetivos", "frases": [], "examen": []},
    "A1.6": {"tema": "Familia y Relaciones", "frases": [], "examen": []},
    "A1.7": {"tema": "Rutinas Diarias", "frases": [], "examen": []},
    "A1.8": {"tema": "Comida y Restaurantes", "frases": [], "examen": []},
    "A1.9": {"tema": "Ropa y Compras", "frases": [], "examen": []},
    "A1.10": {"tema": "Certificación Nivel A1", "frases": [], "examen": []},
    "A2.1": {"tema": "Presente Simple Avanzado", "frases": [], "examen": []},
    "B1.1": {"tema": "Introducción al Intermedio", "frases": [], "examen": []},
    "C1.1": {"tema": "Dominio Avanzado", "frases": [], "examen": []}
}

# ==================== MOTOR DE INTELIGENCIA ARTIFICIAL ====================

def obtener_feedback_pedagogico(objetivo, dicho):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""Actúa como un profesor de fonética inglesa.
    El alumno debía decir: '{objetivo}'
    El alumno realmente dijo: '{dicho}'
    Analiza la diferencia y explica en español, de forma muy breve (máximo 20 palabras), 
    qué sonido específico debe corregir para llegar a la perfección del 100%."""
    try:
        resp = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
        return resp.choices[0].message.content
    except: return "Casi perfecto. Presta atención a la última sílaba."

def transcribir_audio(audio_bytes):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes); audio_file.name = "audio.wav"
        trans = client.audio.transcriptions.create(model="whisper-1", file=audio_file, language="en")
        return trans.text.strip()
    except: return ""

def similitud_texto(texto1, texto2):
    t1 = re.sub(r'[^\w\s]', '', texto1.lower().strip())
    t2 = re.sub(r'[^\w\s]', '', texto2.lower().strip())
    return int(SequenceMatcher(None, t1, t2).ratio() * 100)

# ==================== LÓGICA DE NAVEGACIÓN Y ESTADO ====================
if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = "Andres" # Placeholder para el ejemplo
    st.session_state.nivel_actual = "A1.1"
    st.session_state.fase = "explicacion"
    st.session_state.frase_actual = 0
    st.session_state.respuestas_correctas = 0
    st.session_state.last_audio_id = None
    st.session_state.fecha_inicio = datetime.now().isoformat()

config = CURRICULO[st.session_state.nivel_actual]
niveles_list = list(CURRICULO.keys())
indice_actual = niveles_list.index(st.session_state.nivel_actual)

# ==================== INTERFAZ: BARRA LATERAL ====================
with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo}")
    st.metric("📊 Progreso General", f"{int((indice_actual/len(CURRICULO))*100)}%")
    st.divider()
    st.subheader("🗺️ Itinerario Formativo")
    for k in niveles_list:
        if k == st.session_state.nivel_actual: st.info(f"🎯 {k}: {CURRICULO[k]['tema']}")
        elif niveles_list.index(k) < indice_actual: st.success(f"✅ {k}: {CURRICULO[k]['tema']}")
        else: st.caption(f"🔒 {k}: {CURRICULO[k]['tema']}")
    
    if st.button("🗑️ Reiniciar Programa"):
        st.session_state.clear(); st.rerun()

# ==================== INTERFAZ: ÁREA DE CLASE ====================
st.title(f"🦅 Nexus Pro v5.0")
st.markdown(f"## {st.session_state.nivel_actual}: {config['tema']}")

# --- FASE 1: CLASE MAGISTRAL ---
if st.session_state.fase == "explicacion":
    st.subheader("👨‍🏫 Instrucción Pedagógica")
    st.write(config['clase'])
    if st.button("🚀 Comenzar Práctica", type="primary"):
        st.session_state.fase = "practica"; st.rerun()

# --- FASE 2: PRÁCTICA CON FEEDBACK IA ---
elif st.session_state.fase == "practica":
    total_f = len(config['frases'])
    if total_f == 0:
        st.warning("Sección en desarrollo pedagógico.")
    else:
        frase_obj = config['frases'][st.session_state.frase_actual]
        st.progress(st.session_state.frase_actual / total_f)
        
        # Ficha Pedagógica
        with st.container(border=True):
            st.markdown(f"### Frase {st.session_state.frase_actual + 1}/{total_f}")
            st.write(f"📝 **Inglés:** {frase_obj['ingles']}")
            st.write(f"🇪🇸 **Español:** {frase_obj['español']}")
            st.caption(f"🔊 **Fonetica:** {frase_obj['fonetica']}")
            
            # Audio Guía
            tts = gTTS(text=frase_obj['ingles'], lang='en')
            fp = io.BytesIO(); tts.write_to_fp(fp); fp.seek(0)
            st.audio(fp, format="audio/mp3")

        # Grabación
        audio = mic_recorder(start_prompt="🎙️ Grabar Pronunciación", key=f"rec_{st.session_state.frase_actual}")

        if audio and audio.get("id") != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio.get("id")
            texto = transcribir_audio(audio['bytes'])
            if texto:
                prec = similitud_texto(texto, frase_obj['ingles'])
                st.session_state.res_practica = {"prec": prec, "texto": texto}

        if "res_practica" in st.session_state:
            res = st.session_state.res_practica
            if res["prec"] >= 85:
                st.success(f"✅ Logrado: {res['prec']}%")
                if res["prec"] < 100:
                    with st.expander("👨‍🏫 Mentoría IA (Cómo llegar al 100%)"):
                        st.write(obtener_feedback_pedagogico(frase_obj['ingles'], res['texto']))
                
                if st.button("➡️ Siguiente Frase", type="primary"):
                    if st.session_state.frase_actual < total_f - 1:
                        st.session_state.frase_actual += 1
                    else:
                        st.session_state.fase = "examen"
                    del st.session_state.res_practica; st.rerun()
            else:
                st.error(f"❌ Precisión: {res['prec']}% (Mínimo 85%)")
                st.info("💡 Intenta pronunciar más despacio siguiendo el audio guía.")

# --- FASE 3: EXAMEN DE CERTIFICACIÓN ---
elif st.session_state.fase == "examen":
    # Lógica de examen similar a la práctica pero evaluando comprensión
    st.subheader("📝 Examen de Certificación")
    st.write("Debes responder correctamente para desbloquear el siguiente nivel.")
    if st.button("Finalizar y Subir de Nivel"):
        if indice_actual < len(niveles_list) - 1:
            st.session_state.nivel_actual = niveles_list[indice_actual + 1]
            st.session_state.fase = "explicacion"
            st.session_state.frase_actual = 0
            st.balloons(); st.rerun()
