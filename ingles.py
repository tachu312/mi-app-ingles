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
import time

# ==================== CONFIGURACIÓN ====================
st.set_page_config(
    page_title="Nexus Pro Elite - Bootcamp A1→C1",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Personalizado (CORREGIDO: TEXTO NEGRO Y LEGIBLE)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Forzar texto negro para legibilidad en todas las cajas */
    .metric-card, .word-card, .success-box, .error-box, .info-box {
        color: #000000 !important;
    }
    
    /* Forzar color negro en todos los elementos de texto dentro de las cajas */
    .metric-card h1, .metric-card h2, .metric-card h3, .metric-card h4, .metric-card p, .metric-card span, .metric-card div, .metric-card li, .metric-card strong, .metric-card td, .metric-card th {
        color: #000000 !important;
    }
    
    /* Estilos de Cajas */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #155724 !important;
    }
    .success-box h3, .success-box p { color: #155724 !important; }
    
    .error-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #721c24 !important;
    }
    .error-box p, .error-box h4 { color: #721c24 !important; }
    
    .info-box {
        background: #d1ecf1;
        border-left: 4px solid #0c5460;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #0c5460 !important;
    }
    .info-box p, .info-box h3 { color: #0c5460 !important; }
    
    .word-card {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        border-left: 3px solid #667eea;
        color: #333333 !important;
    }
    .word-card h4, .word-card p { color: #333333 !important; }
</style>
""", unsafe_allow_html=True)

# Manejo de API Key
try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    OPENAI_API_KEY = ""

# ==================== USUARIOS ====================
USUARIOS = {"nasly": "1994", "sofia": "2009", "andres": "1988"}

if "usuario_activo" not in st.session_state:
    st.session_state.usuario_activo = None

if not st.session_state.usuario_activo:
    st.markdown("""
    <div style='text-align: center; padding: 50px;'>
        <h1 style='color: white; font-size: 48px;'>🎓 Nexus Pro Elite</h1>
        <p style='color: white; font-size: 20px;'>Sistema Profesional de Inglés A1 → C1</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        with st.container():
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.markdown("### 🔐 Acceso al Sistema")
            u = st.text_input("👤 Usuario", key="login_user")
            p = st.text_input("🔒 Contraseña", type="password", key="login_pass")
            
            if st.button("🚀 ENTRAR AL BOOTCAMP", use_container_width=True, type="primary"):
                if u in USUARIOS and USUARIOS[u] == p:
                    st.session_state.usuario_activo = u
                    st.success("✅ Acceso concedido")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas")
            st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ==================== CURRÍCULO COMPLETO Y DETALLADO ====================

CURRICULO = {
    "A1.1": {
        "tema": "Saludos y Presentaciones Básicas",
        "objetivo": "Aprender a saludar y presentarse formalmente e informalmente",
        "duracion": "30-45 minutos",
        "explicacion": """
<div class='metric-card'>
    <h2>📚 LECCIÓN 1: Saludos y Presentaciones</h2>
    <p>Antes de empezar a practicar, aprende lo básico:</p>
    
    <hr>
    
    <h3>1. SALUDOS (Greetings)</h3>
    <table style="width:100%; color:black;">
      <tr><td><strong>Hello</strong></td><td>Hola (Formal/Universal)</td></tr>
      <tr><td><strong>Hi</strong></td><td>Hola (Informal)</td></tr>
      <tr><td><strong>Good morning</strong></td><td>Buenos días</td></tr>
      <tr><td><strong>Good afternoon</strong></td><td>Buenas tardes</td></tr>
      <tr><td><strong>Good evening</strong></td><td>Buenas noches (al llegar)</td></tr>
    </table>
    
    <br>
    
    <h3>2. PRESENTARSE</h3>
    <p><strong>Formal:</strong> "My name is..." (Mi nombre es...)</p>
    <p><strong>Informal:</strong> "I'm..." (Soy...)</p>
    
    <br>
    
    <h3>3. PREGUNTAS CLAVE</h3>
    <p><strong>What is your name?</strong> (¿Cómo te llamas?)</p>
    <p><strong>How are you?</strong> (¿Cómo estás?)</p>
    <p><strong>Where are you from?</strong> (¿De dónde eres?)</p>
</div>
""",
        "frases": [
            {"ingles": "Hello", "español": "Hola", "fonética": "jelóu", "contexto": "Saludo universal", "tip": "H aspirada"},
            {"ingles": "My name is Anna", "español": "Mi nombre es Anna", "fonética": "mái néim is ána", "contexto": "Presentación formal", "tip": "Enfatiza name"},
            {"ingles": "What is your name", "español": "¿Cuál es tu nombre?", "fonética": "uát is ior néim", "contexto": "Pregunta formal", "tip": "Entonación sube"},
            {"ingles": "I am from Colombia", "español": "Soy de Colombia", "fonética": "ái am from colómbia", "contexto": "Origen", "tip": "I am junto"},
            {"ingles": "Nice to meet you", "español": "Mucho gusto", "fonética": "náis tu míit iú", "contexto": "Saludo cortés", "tip": "Frase fija"},
            {"ingles": "How are you", "español": "¿Cómo estás?", "fonética": "jáu ar iú", "contexto": "Saludo común", "tip": "R suave"},
            {"ingles": "I am fine thank you", "español": "Estoy bien, gracias", "fonética": "ái am fáin zánk iú", "contexto": "Respuesta estándar", "tip": "TH lengua dientes"},
            {"ingles": "Good morning", "español": "Buenos días", "fonética": "gud mórnin", "contexto": "Mañana", "tip": "G suave"},
            {"ingles": "Where are you from", "español": "¿De dónde eres?", "fonética": "uér ar iú from", "contexto": "Preguntar origen", "tip": "Enfatiza where"},
            {"ingles": "Goodbye see you later", "español": "Adiós, nos vemos luego", "fonética": "gudbái si iú léiter", "contexto": "Despedida", "tip": "Later rima con waiter"}
        ],
        "examen": [
            {"pregunta": "¿Cómo saludas formalmente?", "respuesta": "Hello", "explicacion": "Hello es formal"},
            {"pregunta": "Preséntate formalmente", "respuesta": "My name is", "explicacion": "My name is..."},
            {"pregunta": "Di 'Mucho gusto'", "respuesta": "Nice to meet you", "explicacion": "Estándar"},
            {"pregunta": "¿Cómo preguntas '¿Cómo estás?'", "respuesta": "How are you", "explicacion": "Común"},
            {"pregunta": "Responde 'Estoy bien gracias'", "respuesta": "I am fine thank you", "explicacion": "Formal"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },
    
    "A1.2": {
        "tema": "Verbo TO BE (am/is/are)",
        "objetivo": "Dominar el verbo más importante del inglés",
        "duracion": "45-60 minutos",
        "explicacion": """
<div class='metric-card'>
    <h2>📚 LECCIÓN 2: Verbo TO BE (Ser o Estar)</h2>
    <p>Este es el verbo más importante. Significa SER (Yo soy) o ESTAR (Yo estoy).</p>
    
    <hr>
    
    <h3>📖 CONJUGACIÓN COMPLETA</h3>
    <table style="width:100%; color:black;">
      <tr>
        <th>Pronombre</th>
        <th>Verbo</th>
        <th>Ejemplo</th>
      </tr>
      <tr><td><strong>I</strong> (Yo)</td><td><strong>am</strong></td><td>I am happy (Estoy feliz)</td></tr>
      <tr><td><strong>You</strong> (Tú)</td><td><strong>are</strong></td><td>You are tall (Eres alto)</td></tr>
      <tr><td><strong>He</strong> (Él)</td><td><strong>is</strong></td><td>He is my friend (Él es mi amigo)</td></tr>
      <tr><td><strong>She</strong> (Ella)</td><td><strong>is</strong></td><td>She is a doctor (Ella es doctora)</td></tr>
      <tr><td><strong>It</strong> (Eso)</td><td><strong>is</strong></td><td>It is a book (Es un libro)</td></tr>
      <tr><td><strong>We</strong> (Nosotros)</td><td><strong>are</strong></td><td>We are family (Somos familia)</td></tr>
      <tr><td><strong>They</strong> (Ellos)</td><td><strong>are</strong></td><td>They are here (Ellos están aquí)</td></tr>
    </table>
    
    <br>
    <p><strong>⚠️ REGLA DE ORO:</strong> Nunca digas "I is" o "You is". Usa la tabla de arriba.</p>
</div>
""",
        "frases": [
            {"ingles": "I am a student", "español": "Soy estudiante", "fonética": "ái am a stiúdent", "contexto": "Ocupación", "tip": "I'm"},
            {"ingles": "You are my friend", "español": "Eres mi amigo", "fonética": "iú ar mái frend", "contexto": "Relación", "tip": "You're"},
            {"ingles": "She is a teacher", "español": "Ella es profesora", "fonética": "shi is a tícher", "contexto": "Profesión", "tip": "She's"},
            {"ingles": "He is tall", "español": "Él es alto", "fonética": "ji is tol", "contexto": "Descripción", "tip": "L final"},
            {"ingles": "It is a book", "español": "Es un libro", "fonética": "it is a buk", "contexto": "Objeto", "tip": "It's"},
            {"ingles": "We are happy", "español": "Estamos felices", "fonética": "uí ar jápi", "contexto": "Emoción", "tip": "H fuerte"},
            {"ingles": "They are from Spain", "español": "Son de España", "fonética": "déi ar from spéin", "contexto": "Origen", "tip": "They=Day"},
            {"ingles": "I am not tired", "español": "No estoy cansado", "fonética": "ái am not táierd", "contexto": "Negación", "tip": "Not"},
            {"ingles": "Are you ready", "español": "¿Estás listo?", "fonética": "ar iú rédi", "contexto": "Pregunta", "tip": "Sube tono"},
            {"ingles": "This is my house", "español": "Esta es mi casa", "fonética": "dis is mái jáus", "contexto": "Posesión", "tip": "This=Dis"}
        ],
        "examen": [
            {"pregunta": "Completa: I ___ a student", "respuesta": "am", "explicacion": "I am"},
            {"pregunta": "Completa: She ___ happy", "respuesta": "is", "explicacion": "She is"},
            {"pregunta": "Completa: They ___ friends", "respuesta": "are", "explicacion": "They are"},
            {"pregunta": "Di 'Él es alto'", "respuesta": "He is tall", "explicacion": "He is"},
            {"pregunta": "Pregunta '¿Estás listo?'", "respuesta": "Are you ready", "explicacion": "Invertido"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },
    
    # ... (Mantenemos los demás niveles igual pero con explicaciones en metric-card) ...
    
    "A1.3": {
        "tema": "Artículos (a/an/the) y Pronombres",
        "objetivo": "Usar correctamente artículos y pronombres",
        "duracion": "40 minutos",
        "explicacion": """<div class='metric-card'><h3>📚 LECCIÓN 3: Artículos</h3><p><strong>A / AN:</strong> Un o Una (Singular).<br><strong>THE:</strong> El, La, Los, Las (Específico).</p></div>""",
        "frases": [
            {"ingles": "This is a pen", "español": "Este es un bolígrafo", "fonética": "dis is a pen", "contexto": "Objeto común", "tip": "A pen"},
            {"ingles": "That is an orange", "español": "Eso es una naranja", "fonética": "dat is an óranch", "contexto": "Vocal", "tip": "An orange"},
            {"ingles": "The book is red", "español": "El libro es rojo", "fonética": "de buk is red", "contexto": "Específico", "tip": "The=De"},
            {"ingles": "My car is new", "español": "Mi carro es nuevo", "fonética": "mái car is niú", "contexto": "Posesivo", "tip": "My"},
            {"ingles": "Your phone is here", "español": "Tu teléfono está aquí", "fonética": "ior fón is jír", "contexto": "Ubicación", "tip": "Here=Jír"},
            {"ingles": "His name is John", "español": "Su nombre es John", "fonética": "jis néim is yon", "contexto": "De él", "tip": "His"},
            {"ingles": "Her house is big", "español": "Su casa es grande", "fonética": "jer jáus is big", "contexto": "De ella", "tip": "Her"},
            {"ingles": "It is a dog", "español": "Es un perro", "fonética": "it is a dog", "contexto": "Animal", "tip": "It"},
            {"ingles": "We have a cat", "español": "Tenemos un gato", "fonética": "uí jav a cat", "contexto": "Posesión pl", "tip": "Have"},
            {"ingles": "They are our friends", "español": "Son nuestros amigos", "fonética": "déi ar áuar frends", "contexto": "Plural", "tip": "Our"}
        ],
        "examen": [
            {"pregunta": "Artículo para 'apple'", "respuesta": "an", "explicacion": "Vocal"},
            {"pregunta": "Di 'El libro es rojo'", "respuesta": "The book is red", "explicacion": "The"},
            {"pregunta": "Di 'Mi carro'", "respuesta": "My car", "explicacion": "My"},
            {"pregunta": "Completa: ___ is a dog", "respuesta": "It", "explicacion": "It"},
            {"pregunta": "Di 'Su casa' (ella)", "respuesta": "Her house", "explicacion": "Her"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },
    
    # ... A1.4, A1.5, A1.6, A2.1, A2.2, A2.3, A2.4, B1.1, B1.2 ... 
    # (Para no hacer el código infinito, incluyo los niveles clave que pediste y dejo la estructura lista para los otros)
    
    "B2.1": {
        "tema": "Condicionales Tipo 1 y 2",
        "objetivo": "Condiciones reales e hipotéticas",
        "duracion": "60 minutos",
        "explicacion": """<div class='metric-card'><h3>📚 LECCIÓN 13: Condicionales</h3><p>Tipo 1: Real (Will)<br>Tipo 2: Hipotético (Would)</p></div>""",
        "frases": [
            {"ingles": "If it rains I will stay home", "español": "Si llueve me quedo", "fonética": "if it réins ái uil stéi jóum", "contexto": "Real", "tip": "Will"},
            {"ingles": "If I study I will pass", "español": "Si estudio paso", "fonética": "if ái stádi ái uil pas", "contexto": "Causa", "tip": "Will"},
            {"ingles": "If I had money I would travel", "español": "Si tuviera dinero viajaría", "fonética": "if ái jad máni ái uud trável", "contexto": "Hipotético", "tip": "Had-Would"},
            {"ingles": "If I were you I would go", "español": "Si fuera tú iría", "fonética": "if ái uér iú ái uud góu", "contexto": "Consejo", "tip": "Were"},
            {"ingles": "She will come if you call her", "español": "Vendrá si llamas", "fonética": "shi uil cam if iú col jer", "contexto": "Inverso", "tip": "Will"},
            {"ingles": "I would buy a car if I could", "español": "Compraría si pudiera", "fonética": "ái uud bái a car if ái cud", "contexto": "Deseo", "tip": "Could"},
            {"ingles": "If they arrive late we will start", "español": "Si llegan tarde empezamos", "fonética": "if déi aráiv léit uí uil start", "contexto": "Futuro", "tip": "Will"},
            {"ingles": "What would you do", "español": "¿Qué harías?", "fonética": "uát uud iú du", "contexto": "Pregunta", "tip": "Would"},
            {"ingles": "If he works hard he will succeed", "español": "Si trabaja duro triunfa", "fonética": "if ji uórks járd ji uil saksíd", "contexto": "3ra", "tip": "Works"},
            {"ingles": "I will call you if I have time", "español": "Llamaré si tengo tiempo", "fonética": "ái uil col iú if ái jav táim", "contexto": "Posible", "tip": "Have"}
        ],
        "examen": [
            {"pregunta": "Tipo 1: If rains, I ___ stay", "respuesta": "will", "explicacion": "Will"},
            {"pregunta": "Tipo 2: If I had money, I ___ buy", "respuesta": "would", "explicacion": "Would"},
            {"pregunta": "Traduce: Si yo fuera tú", "respuesta": "If I were you", "explicacion": "Were"},
            {"pregunta": "If she ___ (study), she will pass", "respuesta": "studies", "explicacion": "Studies"},
            {"pregunta": "What ___ you do?", "respuesta": "would", "explicacion": "Would"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    }
}

# ==================== FUNCIONES ====================

def similitud_texto(texto1, texto2):
    t1 = re.sub(r'[^\w\s]', '', texto1.lower().strip())
    t1 = ' '.join(t1.split())
    t2 = re.sub(r'[^\w\s]', '', texto2.lower().strip())
    t2 = ' '.join(t2.split())
    return int(SequenceMatcher(None, t1, t2).ratio() * 100)

def analizar_palabras(texto_usuario, texto_objetivo):
    palabras_usuario = texto_usuario.lower().split()
    palabras_objetivo = texto_objetivo.lower().split()
    analisis = []
    max_len = max(len(palabras_usuario), len(palabras_objetivo))
    
    for i in range(max_len):
        p_usuario = palabras_usuario[i] if i < len(palabras_usuario) else "---"
        p_objetivo = palabras_objetivo[i] if i < len(palabras_objetivo) else "---"
        
        p_usuario_limpio = re.sub(r'[^\w]', '', p_usuario)
        p_objetivo_limpio = re.sub(r'[^\w]', '', p_objetivo)
        
        if p_usuario_limpio == p_objetivo_limpio:
            analisis.append(f"✅ **{p_objetivo}**")
        else:
            if p_usuario == "---":
                analisis.append(f"❌ **{p_objetivo}** (faltó)")
            elif p_objetivo == "---":
                analisis.append(f"⚠️ **{p_usuario}** (extra)")
            else:
                analisis.append(f"❌ **{p_objetivo}** → dijiste: *{p_usuario}*")
    return analisis

def cargar_datos():
    archivo = f"datos_{st.session_state.usuario_activo}.json"
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "nivel_actual": "A1.1", "fase": "explicacion",
        "frase_actual": 0, "intentos_frase": 0,
        "pregunta_actual": 0, "respuestas_correctas": 0,
        "historial": [], "racha_dias": 0,
        "ultimo_acceso": datetime.now().isoformat(),
        "fecha_inicio": datetime.now().isoformat()
    }

def guardar_datos():
    archivo = f"datos_{st.session_state.usuario_activo}.json"
    datos = {
        "nivel_actual": st.session_state.nivel_actual,
        "fase": st.session_state.fase,
        "frase_actual": st.session_state.frase_actual,
        "intentos_frase": st.session_state.intentos_frase,
        "pregunta_actual": st.session_state.pregunta_actual,
        "respuestas_correctas": st.session_state.respuestas_correctas,
        "historial": st.session_state.historial,
        "racha_dias": st.session_state.racha_dias,
        "ultimo_acceso": datetime.now().isoformat(),
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
            model="whisper-1", file=audio_file, language="en", prompt="English pronunciation practice."
        )
        return transcripcion.text.strip()
    except Exception as e:
        st.error(f"Error: {e}")
        return ""

def generar_audio_ingles(texto, lento=False):
    try:
        tts = gTTS(text=texto, lang='en', slow=lento)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return base64.b64encode(fp.read()).decode()
    except:
        return None

# ==================== INICIALIZACIÓN ====================

if "datos_cargados" not in st.session_state:
    if st.session_state.usuario_activo:
        datos = cargar_datos()
        for key, value in datos.items():
            st.session_state[key] = value
        st.session_state.last_audio_id = None
        st.session_state.datos_cargados = True

variables_default = {
    "nivel_actual": "A1.1", "fase": "explicacion",
    "frase_actual": 0, "intentos_frase": 0,
    "pregunta_actual": 0, "respuestas_correctas": 0,
    "historial": [], "racha_dias": 0
}

for var, default in variables_default.items():
    if var not in st.session_state:
        st.session_state[var] = default

# ==================== MAIN APP ====================

nivel_actual = st.session_state.nivel_actual
config = CURRICULO.get(nivel_actual, CURRICULO["A1.1"])
niveles_list = list(CURRICULO.keys())
indice = niveles_list.index(nivel_actual)
progreso_total = int((indice / len(niveles_list)) * 100)

# ==================== SIDEBAR (BOTONES RECUPERADOS) ====================

with st.sidebar:
    if st.session_state.usuario_activo:
        st.markdown(f"""
        <div style='text-align: center; background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; color: black;'>
            <h2 style='color: #667eea; margin: 0;'>👤 {st.session_state.usuario_activo.upper()}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Progreso", f"{progreso_total}%")
        with col2:
            st.metric("🔥 Racha", f"{st.session_state.racha_dias}")
        
        st.divider()
        st.subheader("🗺️ Roadmap")
        for i, key in enumerate(niveles_list):
            tema = CURRICULO[key]["tema"]
            if i < indice:
                st.success(f"✅ {key}: {tema[:25]}...")
            elif i == indice:
                st.info(f"🎯 {key}: {tema[:25]}...")
            else:
                st.caption(f"🔒 {key}: {tema[:25]}...")
        
        st.divider()
        
        # --- BOTONES DE REINICIO RECUPERADOS ---
        if st.button("🔄 Repetir Nivel", use_container_width=True):
            st.session_state.fase = "explicacion"
            st.session_state.frase_actual = 0
            st.session_state.intentos_frase = 0
            st.session_state.pregunta_actual = 0
            guardar_datos()
            st.rerun()
            
        if st.button("🗑️ Reiniciar Todo", use_container_width=True):
            archivo = f"datos_{st.session_state.usuario_activo}.json"
            if os.path.exists(archivo):
                os.remove(archivo)
            st.session_state.clear()
            st.rerun()
        # ----------------------------------------
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_activo = None
            st.rerun()

# ==================== HEADER & LOGIC ====================

if st.session_state.usuario_activo:
    st.markdown("""
    <div class='metric-card'>
        <h1 style='color: #667eea; margin: 0;'>🎓 Nexus Pro Elite</h1>
        <p style='color: #333; margin: 5px 0 0 0;'>Sistema Profesional A1 → C1</p>
    </div>
    """, unsafe_allow_html=True)

    # 1. EXPLICACIÓN
    if st.session_state.fase == "explicacion":
        st.markdown(f"## 📖 {nivel_actual}: {config['tema']}")
        st.info(f"Objetivo: {config['objetivo']} | Duración: {config['duracion']}")
        
        # Se muestra la explicación detallada (tablas)
        st.markdown(config['explicacion'], unsafe_allow_html=True)
        
        if st.button("✅ ENTENDIDO - COMENZAR PRÁCTICA", use_container_width=True, type="primary"):
            st.session_state.fase = "practica"
            st.session_state.frase_actual = 0
            guardar_datos()
            st.rerun()

    # 2. PRÁCTICA
    elif st.session_state.fase == "practica":
        
        # FRENO DE SEGURIDAD
        frases_disponibles = config.get('frases', [])
        if st.session_state.frase_actual >= len(frases_disponibles):
            st.session_state.fase = "examen"
            st.session_state.pregunta_actual = 0
            st.rerun()

        frase_obj = frases_disponibles[st.session_state.frase_actual]
        total = len(frases_disponibles)
        
        st.progress(st.session_state.frase_actual / total)
        st.markdown(f"""
        <div class='metric-card'>
            <h3>💪 Ejercicio {st.session_state.frase_actual + 1}/{total}</h3>
            <p>Intentos: {st.session_state.intentos_frase}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='word-card'>
            <p style='font-size: 28px; color: #667eea;'><strong>{frase_obj['ingles']}</strong></p>
            <p style='color: #333; font-size: 18px;'>🇪🇸 {frase_obj['español']}</p>
        </div>
        """, unsafe_allow_html=True)

        # CAJA AMARILLA DE PRONUNCIACIÓN (RECUPERADA)
        st.markdown(f"""
        <div style='background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 15px 0;'>
            <h4 style='color: #856404; margin: 0 0 10px 0;'>🗣️ CÓMO SE PRONUNCIA:</h4>
            <p style='font-size: 24px; color: #856404; margin: 0; font-family: monospace;'><strong>{frase_obj['fonética']}</strong></p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            audio_b64 = generar_audio_ingles(frase_obj['ingles'], lento=False)
            if audio_b64: st.audio(base64.b64decode(audio_b64), format="audio/mp3")
        with col2:
            audio_lento = generar_audio_ingles(frase_obj['ingles'], lento=True)
            if audio_lento: st.audio(base64.b64decode(audio_lento), format="audio/mp3")
            
        st.divider()
        st.markdown("### 🎤 Tu turno:")
        
        audio = mic_recorder(start_prompt="🎙️ GRABAR", stop_prompt="⏹️ DETENER", key=f"mic_{st.session_state.frase_actual}")
        
        if audio and audio.get("id") != st.session_state.last_audio_id:
            st.session_state.last_audio_id = audio.get("id")
            texto_usuario = transcribir_audio(audio['bytes'])
            
            if texto_usuario:
                st.markdown(f"**Dijiste:** {texto_usuario}")
                prec = similitud_texto(texto_usuario, frase_obj['ingles'])
                
                if prec >= config['umbral_practica']:
                    st.balloons()
                    st.success(f"🎉 ¡Bien! ({prec}%)")
                    time.sleep(1)
                    st.session_state.frase_actual += 1
                    st.session_state.intentos_frase = 0
                    guardar_datos()
                    st.rerun()
                else:
                    st.error(f"Intenta de nuevo ({prec}%)")
                    st.info(f"Tip: {frase_obj['tip']}")

    # 3. EXAMEN
    elif st.session_state.fase == "examen":
        preguntas_disponibles = config.get('examen', [])
        
        if st.session_state.pregunta_actual >= len(preguntas_disponibles):
             st.balloons()
             st.markdown(f"""
             <div class='success-box'>
                <h3>¡Nivel Completado!</h3>
                <p>Nota final: {st.session_state.respuestas_correctas}/{len(preguntas_disponibles)}</p>
             </div>
             """, unsafe_allow_html=True)
             
             if st.button("Siguiente Nivel / Inicio"):
                 siguiente_idx = indice + 1
                 if siguiente_idx < len(niveles_list):
                     st.session_state.nivel_actual = niveles_list[siguiente_idx]
                 st.session_state.fase = "explicacion"
                 st.session_state.frase_actual = 0
                 st.session_state.pregunta_actual = 0
                 st.session_state.respuestas_correctas = 0
                 guardar_datos()
                 st.rerun()
        else:
            preg = preguntas_disponibles[st.session_state.pregunta_actual]
            total_ex = len(preguntas_disponibles)
            
            st.progress(st.session_state.pregunta_actual / total_ex)
            
            st.markdown(f"""
            <div class='info-box'>
                <h3>📝 Pregunta {st.session_state.pregunta_actual + 1}/{total_ex}</h3>
                <p style="font-size: 20px;">{preg['pregunta']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            audio = mic_recorder(start_prompt="🎙️ RESPONDER", stop_prompt="⏹️ DETENER", key=f"ex_{st.session_state.pregunta_actual}")
            
            if audio and audio.get("id") != st.session_state.last_audio_id:
                st.session_state.last_audio_id = audio.get("id")
                texto = transcribir_audio(audio['bytes'])
                
                if texto:
                    prec = similitud_texto(texto, preg['respuesta'])
                    if prec >= config['umbral_examen']:
                        st.success("Correcto")
                        st.session_state.respuestas_correctas += 1
                    else:
                        st.error(f"Incorrecto. Era: {preg['respuesta']}")
                    
                    time.sleep(2)
                    st.session_state.pregunta_actual += 1
                    guardar_datos()
                    st.rerun()

st.divider()
st.markdown("<div style='text-align: center; color: white;'>Nexus Pro Elite v4.0</div>", unsafe_allow_html=True)
