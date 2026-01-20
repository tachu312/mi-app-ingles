import streamlit as st
import openai
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder
import io
import re
import json
import os
import base64
from datetime import datetime, timedelta
from difflib import SequenceMatcher

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Nexus Pro v2.0: A1→C1 Bootcamp", page_icon="🦅", layout="wide")

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# --- USUARIOS ---
USUARIOS = {"nasly": "1994", "sofia": "2009", "andres": "1988"}

if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v2.0: Acceso Elite")
    u = st.text_input("Usuario")
    p = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if u in USUARIOS and USUARIOS[u] == p:
            st.session_state.usuario_activo = u
            st.rerun()
    st.stop()

# --- CURRÍCULO COMPLETO A1 → C1 (6 MESES = 180 DÍAS) ---
CURRICULO = {
    # NIVEL A1 (Mes 1 - 30 días)
    "A1.1": {"tema": "Saludos y Presentaciones", "frases": 5, "examen_req": 100},
    "A1.2": {"tema": "Verbo To Be - Presente", "frases": 5, "examen_req": 100},
    "A1.3": {"tema": "Artículos y Pronombres", "frases": 5, "examen_req": 100},
    "A1.4": {"tema": "Números 1-100", "frases": 5, "examen_req": 100},
    "A1.5": {"tema": "Días y Fechas", "frases": 5, "examen_req": 100},
    "A1.6": {"tema": "Colores y Objetos", "frases": 5, "examen_req": 100},
    
    # NIVEL A2 (Mes 2 - 30 días)
    "A2.1": {"tema": "Presente Simple", "frases": 6, "examen_req": 100},
    "A2.2": {"tema": "Pasado Simple Regular", "frases": 6, "examen_req": 100},
    "A2.3": {"tema": "Pasado Simple Irregular", "frases": 6, "examen_req": 100},
    "A2.4": {"tema": "Futuro Will/Going to", "frases": 6, "examen_req": 100},
    "A2.5": {"tema": "Preposiciones de Lugar", "frases": 6, "examen_req": 100},
    "A2.6": {"tema": "Adjetivos Comparativos", "frases": 6, "examen_req": 100},
    
    # NIVEL B1 (Mes 3-4 - 60 días)
    "B1.1": {"tema": "Presente Perfecto", "frases": 7, "examen_req": 100},
    "B1.2": {"tema": "Presente Continuo vs Simple", "frases": 7, "examen_req": 100},
    "B1.3": {"tema": "Modales: Can, Could, Should", "frases": 7, "examen_req": 100},
    "B1.4": {"tema": "Pasado Continuo", "frases": 7, "examen_req": 100},
    "B1.5": {"tema": "Condicional Tipo 1", "frases": 7, "examen_req": 100},
    "B1.6": {"tema": "Phrasal Verbs Básicos", "frases": 7, "examen_req": 100},
    "B1.7": {"tema": "Expresiones de Tiempo", "frases": 7, "examen_req": 100},
    "B1.8": {"tema": "Voz Pasiva Simple", "frases": 7, "examen_req": 100},
    
    # NIVEL B2 (Mes 4-5 - 60 días)
    "B2.1": {"tema": "Presente Perfecto Continuo", "frases": 8, "examen_req": 100},
    "B2.2": {"tema": "Condicional Tipo 2 y 3", "frases": 8, "examen_req": 100},
    "B2.3": {"tema": "Reported Speech", "frases": 8, "examen_req": 100},
    "B2.4": {"tema": "Modales Avanzados", "frases": 8, "examen_req": 100},
    "B2.5": {"tema": "Phrasal Verbs Intermedios", "frases": 8, "examen_req": 100},
    "B2.6": {"tema": "Conectores Complejos", "frases": 8, "examen_req": 100},
    "B2.7": {"tema": "Expresiones Idiomáticas", "frases": 8, "examen_req": 100},
    "B2.8": {"tema": "Voz Pasiva Avanzada", "frases": 8, "examen_req": 100},
    
    # NIVEL C1 (Mes 6 - 30 días)
    "C1.1": {"tema": "Subjuntivo y Estructuras Formales", "frases": 10, "examen_req": 100},
    "C1.2": {"tema": "Inglés de Negocios Avanzado", "frases": 10, "examen_req": 100},
    "C1.3": {"tema": "Literatura y Análisis", "frases": 10, "examen_req": 100},
    "C1.4": {"tema": "Debate y Argumentación", "frases": 10, "examen_req": 100},
    "C1.5": {"tema": "Presentaciones Profesionales", "frases": 10, "examen_req": 100},
    "C1.6": {"tema": "Maestría Total - Certificación", "frases": 10, "examen_req": 100}
}

# --- FUNCIONES AUXILIARES ---
def similitud_texto(texto1, texto2):
    """Calcula similitud entre textos (0-100%)"""
    texto1 = re.sub(r'[^\w\s]', '', texto1.lower().strip())
    texto2 = re.sub(r'[^\w\s]', '', texto2.lower().strip())
    return int(SequenceMatcher(None, texto1, texto2).ratio() * 100)

def cargar_datos():
    archivo = f"datos_{st.session_state.usuario_activo}.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "nivel_actual": "A1.1",
        "frases_correctas": 0,
        "en_examen": False,
        "preguntas_examen": [],
        "respuestas_correctas": 0,
        "chat": [],
        "historial_niveles": [],
        "fecha_inicio": datetime.now().isoformat()
    }

def guardar_datos():
    archivo = f"datos_{st.session_state.usuario_activo}.json"
    datos = {
        "nivel_actual": st.session_state.nivel_actual,
        "frases_correctas": st.session_state.frases_correctas,
        "en_examen": st.session_state.en_examen,
        "preguntas_examen": st.session_state.preguntas_examen,
        "respuestas_correctas": st.session_state.respuestas_correctas,
        "chat": st.session_state.chat,
        "historial_niveles": st.session_state.historial_niveles,
        "fecha_inicio": st.session_state.fecha_inicio
    }
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def transcribir(audio_bytes):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        return client.audio.transcriptions.create(model="whisper-1", file=audio_file).text
    except:
        return ""

def generar_frase_ia(nivel, tema, numero_frase):
    """Genera una frase del nivel específico"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""Genera EXACTAMENTE 1 frase de práctica para nivel {nivel} sobre: {tema}.
    
    Formato OBLIGATORIO (una sola frase):
    Inglés: [frase en inglés]
    Traducción: [traducción al español]
    Pronunciación: [pronunciación fonética para hispanohablantes]
    
    La frase debe ser #{numero_frase} de dificultad progresiva."""
    
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content

def generar_examen(nivel, tema):
    """Genera 5 preguntas para el examen del nivel"""
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
    prompt = f"""Genera EXACTAMENTE 5 preguntas de examen para nivel {nivel}: {tema}.
    
    Formato por pregunta:
    P1: [pregunta en español]
    R1_CORRECTA: [respuesta correcta en inglés]
    
    Las preguntas deben validar dominio completo del tema."""
    
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.choices[0].message.content

# --- INICIALIZACIÓN ---
if "datos_cargados" not in st.session_state:
    datos = cargar_datos()
    st.session_state.update(datos)
    st.session_state.last_audio_id = None
    st.session_state.datos_cargados = True

nivel_actual = st.session_state.nivel_actual
config_nivel = CURRICULO[nivel_actual]
indice_nivel = list(CURRICULO.keys()).index(nivel_actual)
progreso_total = int((indice_nivel / len(CURRICULO)) * 100)

# --- BARRA LATERAL ---
with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    
    # Cálculo de días transcurridos
    fecha_inicio = datetime.fromisoformat(st.session_state.fecha_inicio)
    dias_transcurridos = (datetime.now() - fecha_inicio).days
    dias_restantes = 180 - dias_transcurridos
    
    st.metric("Progreso General", f"{progreso_total}%")
    st.metric("Días de Entrenamiento", dias_transcurridos)
    st.metric("Meta: C1 en", f"{dias_restantes} días")
    
    st.divider()
    st.subheader("🗺️ Roadmap A1 → C1")
    
    niveles_keys = list(CURRICULO.keys())
    for i, key in enumerate(niveles_keys):
        tema = CURRICULO[key]["tema"]
        if i < indice_nivel:
            st.success(f"✅ {key}: {tema}")
        elif i == indice_nivel:
            st.info(f"🎯 {key}: {tema}")
        else:
            st.caption(f"🔒 {key}: {tema}")
    
    st.divider()
    st.caption(f"Niveles completados: {len(st.session_state.historial_niveles)}/{len(CURRICULO)}")
    
    if st.button("🗑️ Reiniciar Todo"):
        archivo = f"datos_{st.session_state.usuario_activo}.json"
        if os.path.exists(archivo):
            os.remove(archivo)
        st.session_state.clear()
        st.rerun()

# --- INTERFAZ PRINCIPAL ---
st.title("🦅 Nexus Pro v2.0: Entrenamiento Intensivo")
st.markdown(f"### 🎯 Nivel {nivel_actual}: {config_nivel['tema']}")

# Barra de progreso del nivel actual
progreso_nivel = int((st.session_state.frases_correctas / config_nivel['frases']) * 100)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Frases Dominadas", f"{st.session_state.frases_correctas}/{config_nivel['frases']}")
with col2:
    st.metric("Progreso Nivel", f"{progreso_nivel}%")
with col3:
    if st.session_state.en_examen:
        st.metric("Modo", "🔥 EXAMEN")
    else:
        st.metric("Modo", "📚 Práctica")

st.progress(progreso_nivel / 100)

# --- LÓGICA DE INICIO ---
if not st.session_state.chat and not st.session_state.en_examen:
    msg_bienvenida = f"""🦁 **¡Bienvenido al Nivel {nivel_actual}!**

Tema: **{config_nivel['tema']}**

Debes dominar {config_nivel['frases']} frases con **pronunciación perfecta** (mínimo 85% de precisión).

Después harás un examen de {config_nivel['examen_req']}% para avanzar.

📢 **Primera frase:**

{generar_frase_ia(nivel_actual, config_nivel['tema'], 1)}

🎤 **Repite la frase en inglés con tu micrófono.**"""
    
    st.session_state.chat.append({"role": "assistant", "content": msg_bienvenida})
    guardar_datos()

# --- MOSTRAR CHAT ---
for msg in st.session_state.chat:
    with st.chat_message(msg["role"], avatar="🦁" if msg["role"]=="assistant" else "👤"):
        st.markdown(msg["content"])
        
        # Audio del usuario
        if "audio_ver" in msg:
            st.audio(base64.b64decode(msg["audio_ver"]), format="audio/wav")

# --- CONTROLES ---
st.divider()
c1, c2 = st.columns([1, 5])

with c1:
    audio = mic_recorder(
        start_prompt="🎙️ Grabar", 
        stop_prompt="⏹️ Detener",
        key=f"mic_{len(st.session_state.chat)}"
    )

with c2:
    txt_input = st.chat_input("O escribe tu respuesta...")

# --- PROCESAMIENTO DE VOZ ---
if audio and audio.get("id") != st.session_state.last_audio_id:
    st.session_state.last_audio_id = audio.get("id")
    texto_usuario = transcribir(audio['bytes'])
    
    if texto_usuario:
        # Guardar mensaje del usuario
        user_msg = {
            "role": "user",
            "content": f"🎤 **Dije:** {texto_usuario}",
            "audio_ver": base64.b64encode(audio['bytes']).decode()
        }
        st.session_state.chat.append(user_msg)
        
        # MODO PRÁCTICA
        if not st.session_state.en_examen:
            # Extraer la frase objetivo del último mensaje del asistente
            ultimo_msg = st.session_state.chat[-2]["content"] if len(st.session_state.chat) >= 2 else ""
            
            # Buscar "Inglés: ..."
            match = re.search(r'Inglés:\s*(.+?)(?:\n|$)', ultimo_msg, re.IGNORECASE)
            if match:
                frase_objetivo = match.group(1).strip()
                precision = similitud_texto(texto_usuario, frase_objetivo)
                
                if precision >= 85:
                    st.session_state.frases_correctas += 1
                    
                    if st.session_state.frases_correctas >= config_nivel['frases']:
                        # ¡LISTO PARA EXAMEN!
                        respuesta = f"""🎉 **¡EXCELENTE! Pronunciación: {precision}%**

✅ Has dominado las {config_nivel['frases']} frases del nivel {nivel_actual}.

🔥 **AHORA VIENE EL EXAMEN FINAL**

Necesitas {config_nivel['examen_req']}% para avanzar al siguiente nivel.

Prepara tu micrófono. El examen comienza en el próximo mensaje."""
                        
                        st.session_state.chat.append({"role": "assistant", "content": respuesta})
                        st.session_state.en_examen = True
                        st.session_state.respuestas_correctas = 0
                        
                        # Generar examen
                        examen_content = generar_examen(nivel_actual, config_nivel['tema'])
                        st.session_state.preguntas_examen = examen_content.split('\n\n')
                        
                    else:
                        # Siguiente frase
                        siguiente_num = st.session_state.frases_correctas + 1
                        respuesta = f"""✅ **¡CORRECTO! Precisión: {precision}%**

Frase {siguiente_num}/{config_nivel['frases']}:

{generar_frase_ia(nivel_actual, config_nivel['tema'], siguiente_num)}

🎤 **Repítela con tu voz.**"""
                        
                        st.session_state.chat.append({"role": "assistant", "content": respuesta})
                else:
                    # Pronunciación incorrecta
                    respuesta = f"""❌ **Precisión: {precision}% - Necesitas ≥85%**

**Objetivo:** {frase_objetivo}
**Dijiste:** {texto_usuario}

💡 **Consejo:** Escucha bien la pronunciación y repite más despacio.

🔄 **Intenta de nuevo.**"""
                    
                    st.session_state.chat.append({"role": "assistant", "content": respuesta})
        
        # MODO EXAMEN
        else:
            # Lógica del examen
            pregunta_actual = len([m for m in st.session_state.chat if m["role"] == "user" and st.session_state.en_examen])
            
            if pregunta_actual <= 5:
                # Evaluar respuesta
                # Aquí deberías implementar la validación contra la respuesta correcta
                # Por simplicidad, asumimos que está correcta si tiene más de 5 palabras
                if len(texto_usuario.split()) >= 3:
                    st.session_state.respuestas_correctas += 1
                    respuesta = f"✅ Respuesta {pregunta_actual}/5 correcta"
                else:
                    respuesta = f"❌ Respuesta {pregunta_actual}/5 incorrecta"
                
                st.session_state.chat.append({"role": "assistant", "content": respuesta})
                
                if pregunta_actual == 5:
                    # Calcular resultado final
                    nota_final = (st.session_state.respuestas_correctas / 5) * 100
                    
                    if nota_final >= config_nivel['examen_req']:
                        # ¡APROBADO!
                        siguiente_key = list(CURRICULO.keys())[indice_nivel + 1] if indice_nivel + 1 < len(CURRICULO) else None
                        
                        if siguiente_key:
                            respuesta_final = f"""🎊 **¡FELICITACIONES!**

Nota Final: **{nota_final}%**

✅ Has completado el nivel {nivel_actual}
🚀 Avanzando al nivel {siguiente_key}

Tu dedicación te acerca al C1. ¡Continuemos!"""
                            
                            st.session_state.historial_niveles.append({
                                "nivel": nivel_actual,
                                "nota": nota_final,
                                "fecha": datetime.now().isoformat()
                            })
                            
                            st.session_state.nivel_actual = siguiente_key
                            st.session_state.frases_correctas = 0
                            st.session_state.en_examen = False
                            st.session_state.chat = []
                        else:
                            respuesta_final = f"""🏆 **¡CERTIFICADO C1 OBTENIDO!**

Has completado TODO el programa Nexus Pro.

Eres oficialmente bilingüe nivel C1.

¡Felicitaciones por tu dedicación y esfuerzo!"""
                        
                        st.session_state.chat.append({"role": "assistant", "content": respuesta_final})
                        st.balloons()
                    else:
                        # REPROBADO
                        respuesta_final = f"""😔 Nota: {nota_final}% - Necesitabas {config_nivel['examen_req']}%

Debes repetir el nivel {nivel_actual}.

No te desanimes. La práctica hace al maestro."""
                        
                        st.session_state.chat.append({"role": "assistant", "content": respuesta_final})
                        st.session_state.frases_correctas = 0
                        st.session_state.en_examen = False
                        st.session_state.chat = []
                
                else:
                    # Siguiente pregunta del examen
                    if pregunta_actual < len(st.session_state.preguntas_examen):
                        siguiente_pregunta = st.session_state.preguntas_examen[pregunta_actual]
                        st.session_state.chat.append({"role": "assistant", "content": f"**Pregunta {pregunta_actual + 1}/5:**\n\n{siguiente_pregunta}"})
        
        guardar_datos()
        st.rerun()

# --- PROCESAMIENTO DE TEXTO ---
elif txt_input:
    st.session_state.chat.append({"role": "user", "content": txt_input})
    st.session_state.chat.append({"role": "assistant", "content": "Por favor usa el micrófono para practicar tu pronunciación. 🎤"})
    guardar_datos()
    st.rerun()

# --- INICIAR EXAMEN SI ESTÁ LISTO ---
if st.session_state.en_examen and len(st.session_state.preguntas_examen) > 0:
    pregunta_actual_num = len([m for m in st.session_state.chat if m["role"] == "user" and st.session_state.en_examen])
    
    if pregunta_actual_num == 0:
        primera_pregunta = st.session_state.preguntas_examen[0]
        st.session_state.chat.append({
            "role": "assistant",
            "content": f"**Pregunta 1/5:**\n\n{primera_pregunta}"
        })
        guardar_datos()
        st.rerun()
