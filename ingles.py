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
    page_title="Nexus Pro v4.0: A1→C1 Bootcamp",
    page_icon="🦅",
    layout="wide"
)

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# ==================== USUARIOS ====================
USUARIOS = {"nasly": "1994", "sofia": "2009", "andres": "1988"}

if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.title("🦅 Nexus Pro v4.0")
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        u = st.text_input("👤 Usuario")
        p = st.text_input("🔒 Contraseña", type="password")
        if st.button("🚀 Entrar", use_container_width=True):
            if u in USUARIOS and USUARIOS[u] == p:
                st.session_state.usuario_activo = u
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas")
    st.stop()

# ==================== CONTENIDO PEDAGÓGICO ESTRUCTURADO ====================
CURRICULO = {
    "A1.1": {
        "tema": "Saludos y Presentaciones",
        "explicacion": """**📚 LECCIÓN: Saludos y Presentaciones**

En esta lección aprenderás las formas básicas de saludar y presentarte en inglés.

**GRAMÁTICA CLAVE:**
- Saludos formales: Good morning, Good afternoon, Good evening
- Saludos informales: Hi, Hello, Hey
- Estructura: "My name is + [nombre]" o "I am + [nombre]"
- Pregunta común: "What is your name?" (¿Cómo te llamas?)

**VOCABULARIO:**
- Hello = Hola
- My = Mi
- Name = Nombre
- I am = Yo soy
- Nice to meet you = Mucho gusto""",
        "frases": [
            {"ingles": "Hello", "español": "Hola", "fonética": "jelóu"},
            {"ingles": "My name is Anna", "español": "Mi nombre es Anna", "fonética": "mai néim is ána"},
            {"ingles": "I am from Colombia", "español": "Soy de Colombia", "fonética": "ái am from colómbia"},
            {"ingles": "Nice to meet you", "español": "Mucho gusto", "fonética": "náis tu míit iu"},
            {"ingles": "How are you", "español": "¿Cómo estás?", "fonética": "jáu ar iu"},
            {"ingles": "I am fine thank you", "español": "Estoy bien gracias", "fonética": "ái am fáin zank iu"},
            {"ingles": "Good morning", "español": "Buenos días", "fonética": "gud mórnin"},
            {"ingles": "What is your name", "español": "¿Cuál es tu nombre?", "fonética": "uát is ior néim"},
            {"ingles": "Where are you from", "español": "¿De dónde eres?", "fonética": "uér ar iu from"},
            {"ingles": "Goodbye see you later", "español": "Adiós nos vemos luego", "fonética": "gudbái si iu léiter"}
        ],
        "examen": [
            {"pregunta": "¿Cómo dices 'Hola' en inglés?", "respuesta": "Hello"},
            {"pregunta": "¿Cómo te presentas diciendo tu nombre?", "respuesta": "My name is"},
            {"pregunta": "Di 'Mucho gusto' en inglés", "respuesta": "Nice to meet you"},
            {"pregunta": "Pregunta '¿Cómo estás?' en inglés", "respuesta": "How are you"},
            {"pregunta": "Responde 'Estoy bien gracias' en inglés", "respuesta": "I am fine thank you"}
        ]
    },
    
    "A1.2": {
        "tema": "Verbo To Be (am/is/are)",
        "explicacion": """**📚 LECCIÓN: Verbo TO BE**

El verbo "to be" es el más importante en inglés. Significa SER o ESTAR.

**GRAMÁTICA:**
- I am = Yo soy/estoy
- You are = Tú eres/estás
- He is = Él es/está
- She is = Ella es/está
- It is = Eso es/está
- We are = Nosotros somos/estamos
- They are = Ellos son/están

**FORMAS CONTRAÍDAS:**
- I am = I'm
- You are = You're
- He is = He's
- She is = She's

**USOS:**
1. Identidad: I am a student (Soy estudiante)
2. Ubicación: She is in Colombia (Ella está en Colombia)
3. Estado: They are happy (Ellos están felices)""",
        "frases": [
            {"ingles": "I am a student", "español": "Soy un estudiante", "fonética": "ái am a stiúdent"},
            {"ingles": "You are my friend", "español": "Eres mi amigo", "fonética": "iú ar mai frend"},
            {"ingles": "She is a teacher", "español": "Ella es una profesora", "fonética": "shi is a tícher"},
            {"ingles": "He is tall", "español": "Él es alto", "fonética": "ji is tol"},
            {"ingles": "It is a book", "español": "Es un libro", "fonética": "it is a buk"},
            {"ingles": "We are happy", "español": "Estamos felices", "fonética": "ui ar jápi"},
            {"ingles": "They are from Spain", "español": "Ellos son de España", "fonética": "déi ar from spéin"},
            {"ingles": "I am not tired", "español": "No estoy cansado", "fonética": "ái am not táired"},
            {"ingles": "Are you ready", "español": "¿Estás listo?", "fonética": "ar iú rédi"},
            {"ingles": "This is my house", "español": "Esta es mi casa", "fonética": "dis is mai jáus"}
        ],
        "examen": [
            {"pregunta": "Completa: I ___ a student", "respuesta": "am"},
            {"pregunta": "Completa: She ___ happy", "respuesta": "is"},
            {"pregunta": "Completa: They ___ friends", "respuesta": "are"},
            {"pregunta": "Di 'Él es alto' en inglés", "respuesta": "He is tall"},
            {"pregunta": "Pregunta '¿Estás listo?' en inglés", "respuesta": "Are you ready"}
        ]
    },
    
    "A1.3": {
        "tema": "Artículos y Pronombres",
        "explicacion": """**📚 LECCIÓN: Artículos y Pronombres**

**ARTÍCULOS:**
- A / An = Un, Una (indefinido)
  - Usa "A" antes de consonante: a cat, a dog
  - Usa "An" antes de vocal: an apple, an egg
- The = El, La, Los, Las (definido)

**PRONOMBRES PERSONALES:**
- I (ái) = Yo
- You (iú) = Tú/Usted
- He (ji) = Él
- She (shi) = Ella
- It (it) = Eso (cosas/animales)
- We (uí) = Nosotros
- They (déi) = Ellos/Ellas

**PRONOMBRES POSESIVOS:**
- My = Mi
- Your = Tu
- His = Su (de él)
- Her = Su (de ella)""",
        "frases": [
            {"ingles": "This is a pen", "español": "Este es un bolígrafo", "fonética": "dis is a pen"},
            {"ingles": "That is an orange", "español": "Eso es una naranja", "fonética": "dat is an óranch"},
            {"ingles": "The book is red", "español": "El libro es rojo", "fonética": "de buk is red"},
            {"ingles": "My car is new", "español": "Mi carro es nuevo", "fonética": "mai car is niú"},
            {"ingles": "Your phone is here", "español": "Tu teléfono está aquí", "fonética": "ior fón is jír"},
            {"ingles": "His name is John", "español": "Su nombre es John", "fonética": "jis néim is yon"},
            {"ingles": "Her house is big", "español": "Su casa es grande", "fonética": "jer jáus is big"},
            {"ingles": "It is a dog", "español": "Es un perro", "fonética": "it is a dog"},
            {"ingles": "We have a cat", "español": "Tenemos un gato", "fonética": "uí jav a cat"},
            {"ingles": "They are our friends", "español": "Ellos son nuestros amigos", "fonética": "déi ar áuar frends"}
        ],
        "examen": [
            {"pregunta": "¿Qué artículo va antes de 'apple'? (a o an)", "respuesta": "an"},
            {"pregunta": "Di 'El libro es rojo' en inglés", "respuesta": "The book is red"},
            {"pregunta": "¿Cómo se dice 'Mi carro'?", "respuesta": "My car"},
            {"pregunta": "Completa: ___ is a dog (It/The)", "respuesta": "It"},
            {"pregunta": "Di 'Su casa' (de ella) en inglés", "respuesta": "Her house"}
        ]
    }
}

# ==================== FUNCIONES AUXILIARES ====================

def similitud_texto(texto1, texto2):
    """Calcula similitud IGNORANDO puntuación y mayúsculas"""
    t1 = re.sub(r'[^\w\s]', '', texto1.lower().strip())
    t1 = ' '.join(t1.split())
    t2 = re.sub(r'[^\w\s]', '', texto2.lower().strip())
    t2 = ' '.join(t2.split())
    return int(SequenceMatcher(None, t1, t2).ratio() * 100)

def cargar_datos():
    archivo = f"datos_{st.session_state.usuario_activo}.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "nivel_actual": "A1.1",
        "fase": "explicacion",  # explicacion, practica, examen
        "frase_actual": 0,
        "pregunta_actual": 0,
        "respuestas_correctas": 0,
        "historial": [],
        "fecha_inicio": datetime.now().isoformat()
    }

def guardar_datos():
    archivo = f"datos_{st.session_state.usuario_activo}.json"
    datos = {
        "nivel_actual": st.session_state.nivel_actual,
        "fase": st.session_state.fase,
        "frase_actual": st.session_state.frase_actual,
        "pregunta_actual": st.session_state.pregunta_actual,
        "respuestas_correctas": st.session_state.respuestas_correctas,
        "historial": st.session_state.historial,
        "fecha_inicio": st.session_state.fecha_inicio
    }
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def transcribir_audio(audio_bytes):
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = "audio.wav"
        transcripcion = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="en",
            prompt="English pronunciation practice."
        )
        return transcripcion.text.strip()
    except Exception as e:
        st.error(f"Error: {e}")
        return ""

def generar_audio_ingles(texto):
    try:
        tts = gTTS(text=texto, lang='en', slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode()
    except:
        return None

# ==================== INICIALIZACIÓN ====================

if "datos_cargados" not in st.session_state:
    datos = cargar_datos()
    for key, value in datos.items():
        st.session_state[key] = value
    st.session_state.last_audio_id = None
    st.session_state.datos_cargados = True

# Asegurar variables
for var in ["nivel_actual", "fase", "frase_actual", "pregunta_actual", "respuestas_correctas", "historial"]:
    if var not in st.session_state:
        if var == "nivel_actual":
            st.session_state[var] = "A1.1"
        elif var == "fase":
            st.session_state[var] = "explicacion"
        elif var == "historial":
            st.session_state[var] = []
        else:
            st.session_state[var] = 0

# ==================== VARIABLES ====================

nivel_actual = st.session_state.nivel_actual
config = CURRICULO.get(nivel_actual, CURRICULO["A1.1"])
niveles_list = list(CURRICULO.keys())
indice = niveles_list.index(nivel_actual)
progreso_total = int((indice / len(niveles_list)) * 100)

# ==================== BARRA LATERAL ====================

with st.sidebar:
    st.title(f"👤 {st.session_state.usuario_activo.upper()}")
    
    dias = (datetime.now() - datetime.fromisoformat(st.session_state.fecha_inicio)).days
    st.metric("📊 Progreso", f"{progreso_total}%")
    st.metric("📅 Días", dias)
    st.metric("🎯 Nivel", nivel_actual)
    
    st.divider()
    st.subheader("🗺️ Roadmap")
    
    for i, key in enumerate(niveles_list):
        tema = CURRICULO[key]["tema"]
        if i < indice:
            st.success(f"✅ {key}: {tema}")
        elif i == indice:
            st.info(f"🎯 {key}: {tema}")
        else:
            st.caption(f"🔒 {key}: {tema}")
    
    st.divider()
    
    if st.session_state.historial:
        st.subheader("📜 Logros")
        for logro in st.session_state.historial[-3:]:
            st.caption(f"✅ {logro['nivel']}: {logro['nota']:.0f}%")
    
    st.divider()
    
    if st.button("🗑️ Reiniciar", use_container_width=True):
        archivo = f"datos_{st.session_state.usuario_activo}.json"
        if os.path.exists(archivo):
            os.remove(archivo)
        st.session_state.clear()
        st.rerun()

# ==================== INTERFAZ PRINCIPAL ====================

st.title("🦅 Nexus Pro v4.0")
st.markdown(f"### {nivel_actual}: {config['tema']}")

# ==================== FASE: EXPLICACIÓN ====================

if st.session_state.fase == "explicacion":
    st.markdown(config['explicacion'])
    
    st.divider()
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("✅ Entendí, vamos a practicar", use_container_width=True, type="primary"):
            st.session_state.fase = "practica"
            st.session_state.frase_actual = 0
            guardar_datos()
            st.rerun()

# ==================== FASE: PRÁCTICA ====================

elif st.session_state.fase == "practica":
    frase_obj = config['frases'][st.session_state.frase_actual]
    total_frases = len(config['frases'])
    
    st.progress(st.session_state.frase_actual / total_frases)
    st.markdown(f"**Frase {st.session_state.frase_actual + 1}/{total_frases}**")
    
    st.info(f"""**📝 Inglés:** {frase_obj['ingles']}  
**🇪🇸 Español:** {frase_obj['español']}  
**🔊 Pronunciación:** {frase_obj['fonética']}""")
    
    audio_b64 = generar_audio_ingles(frase_obj['ingles'])
    if audio_b64:
        st.markdown("🔊 **Escucha la pronunciación:**")
        st.audio(base64.b64decode(audio_b64), format="audio/mp3")
    
    st.divider()
    st.markdown("🎤 **Ahora repite la frase con tu micrófono:**")
    
    audio = mic_recorder(start_prompt="🎙️ Grabar", stop_prompt="⏹️ Detener", key=f"mic_{st.session_state.frase_actual}")
    
    if audio and audio.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio.get("id")
        
        with st.spinner("🎧 Analizando..."):
            texto_usuario = transcribir_audio(audio['bytes'])
        
        if texto_usuario:
            precision = similitud_texto(texto_usuario, frase_obj['ingles'])
            
            if precision >= 75:
                st.success(f"✅ ¡CORRECTO! Precisión: {precision}%")
                st.balloons()
                
                if st.session_state.frase_actual < total_frases - 1:
                    if st.button("➡️ Siguiente frase", type="primary"):
                        st.session_state.frase_actual += 1
                        guardar_datos()
                        st.rerun()
                else:
                    if st.button("🔥 Ir al Examen Final", type="primary"):
                        st.session_state.fase = "examen"
                        st.session_state.pregunta_actual = 0
                        st.session_state.respuestas_correctas = 0
                        guardar_datos()
                        st.rerun()
            else:
                st.error(f"❌ Precisión: {precision}% (Necesitas ≥75%)")
                st.warning(f"**Objetivo:** {frase_obj['ingles']}\n**Dijiste:** {texto_usuario}")
                st.info("💡 Escucha el audio de nuevo y repite más claro")

# ==================== FASE: EXAMEN ====================

elif st.session_state.fase == "examen":
    pregunta_obj = config['examen'][st.session_state.pregunta_actual]
    total_preguntas = len(config['examen'])
    
    st.progress(st.session_state.pregunta_actual / total_preguntas)
    st.markdown(f"### 📝 Examen - Pregunta {st.session_state.pregunta_actual + 1}/{total_preguntas}")
    
    st.info(f"**{pregunta_obj['pregunta']}**")
    st.markdown("🎤 **Responde en inglés con tu micrófono:**")
    
    audio = mic_recorder(start_prompt="🎙️", stop_prompt="⏹️", key=f"exam_{st.session_state.pregunta_actual}")
    
    if audio and audio.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio.get("id")
        
        with st.spinner("🎧 Evaluando..."):
            texto_usuario = transcribir_audio(audio['bytes'])
        
        if texto_usuario:
            precision = similitud_texto(texto_usuario, pregunta_obj['respuesta'])
            
            if precision >= 70:
                st.success(f"✅ CORRECTO ({precision}%)")
                st.session_state.respuestas_correctas += 1
            else:
                st.error(f"❌ INCORRECTA ({precision}%)")
                st.warning(f"**Esperaba:** {pregunta_obj['respuesta']}\n**Dijiste:** {texto_usuario}")
            
            if st.session_state.pregunta_actual < total_preguntas - 1:
                if st.button("➡️ Siguiente pregunta", type="primary"):
                    st.session_state.pregunta_actual += 1
                    guardar_datos()
                    st.rerun()
            else:
                # RESULTADO FINAL
                nota = (st.session_state.respuestas_correctas / total_preguntas) * 100
                
                st.divider()
                st.markdown(f"## 📊 Resultado: {nota:.0f}%")
                st.markdown(f"**Correctas:** {st.session_state.respuestas_correctas}/{total_preguntas}")
                
                if st.session_state.respuestas_correctas == total_preguntas:
                    st.success("🎊 ¡EXAMEN APROBADO!")
                    
                    siguiente_idx = indice + 1
                    if siguiente_idx < len(niveles_list):
                        siguiente = niveles_list[siguiente_idx]
                        st.markdown(f"🚀 **Avanzando a {siguiente}**")
                        
                        st.session_state.historial.append({
                            "nivel": nivel_actual,
                            "nota": nota,
                            "fecha": datetime.now().isoformat()
                        })
                        
                        if st.button("➡️ Comenzar siguiente nivel", type="primary"):
                            st.session_state.nivel_actual = siguiente
                            st.session_state.fase = "explicacion"
                            st.session_state.frase_actual = 0
                            st.session_state.pregunta_actual = 0
                            st.session_state.respuestas_correctas = 0
                            guardar_datos()
                            st.rerun()
                    else:
                        st.success("🏆 ¡Completaste todo el curso!")
                else:
                    st.error("😔 Examen reprobado")
                    st.info(f"Necesitabas {total_preguntas}/{total_preguntas} para avanzar")
                    
                    if st.button("🔄 Repetir nivel", type="primary"):
                        st.session_state.fase = "explicacion"
                        st.session_state.frase_actual = 0
                        st.session_state.pregunta_actual = 0
                        st.session_state.respuestas_correctas = 0
                        guardar_datos()
                        st.rerun()
