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

# CSS Personalizado
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
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
    }
    .error-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .info-box {
        background: #d1ecf1;
        border-left: 4px solid #0c5460;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .word-card {
        background: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
        border-left: 3px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

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
            
            st.info("""
            **📚 Características del Sistema:**
            - ✅ Explicaciones detalladas con gramática
            - ✅ 10 ejercicios variados por nivel
            - ✅ Pronunciación nativa con audio
            - ✅ Sistema de repetición hasta dominar (85%+)
            - ✅ Análisis palabra por palabra
            - ✅ Exámenes rigurosos
            - ✅ Seguimiento de racha diaria
            - ✅ Certificación progresiva
            """)
    st.stop()

# ==================== CURRÍCULO PROFESIONAL COMPLETO ====================

CURRICULO = {
    "A1.1": {
        "tema": "Saludos y Presentaciones Básicas",
        "objetivo": "Aprender a saludar y presentarse formalmente e informalmente",
        "duracion": "30-45 minutos",
        "explicacion": """
## 📚 LECCIÓN 1: Saludos y Presentaciones

### 🎯 OBJETIVO DE LA LECCIÓN
Al finalizar esta lección podrás:
- ✅ Saludar en diferentes contextos (formal/informal)
- ✅ Presentarte diciendo tu nombre
- ✅ Preguntar el nombre de otras personas
- ✅ Despedirte apropiadamente

---

### 📖 GRAMÁTICA FUNDAMENTAL

#### 1. ESTRUCTURA DE PRESENTACIÓN
```
Formal:   "My name is [nombre]"
Informal: "I'm [nombre]"
```

**Ejemplos:**
- My name is María → Mi nombre es María
- I'm John → Soy John

#### 2. PREGUNTAR EL NOMBRE
```
Formal:   "What is your name?"
Informal: "What's your name?"
```

#### 3. SALUDOS POR HORARIO
- **Good morning** → Buenos días (hasta las 12pm)
- **Good afternoon** → Buenas tardes (12pm - 6pm)
- **Good evening** → Buenas noches (después de 6pm)
- **Hello / Hi** → Hola (cualquier momento)

---

### 📝 VOCABULARIO CLAVE

| Inglés | Español | Pronunciación |
|--------|---------|---------------|
| Hello | Hola | jelóu |
| Hi | Hola (informal) | jái |
| My | Mi/mis | mái |
| Name | Nombre | néim |
| I am | Yo soy/estoy | ái am |
| You | Tú/usted | iú |
| From | De/desde | from |
| Nice | Agradable/lindo | náis |
| Meet | Conocer/encontrar | míit |
| Goodbye | Adiós | gudbái |

---

### 💡 CONSEJOS DE PRONUNCIACIÓN

1. **La "H" siempre se pronuncia** (como aspirada)
   - Hello = JEH-loh (no "elo")
   - Hi = JAI (no "i")

2. **La "R" es suave**, no fuerte como en español
   - Are = ar (suave, no "arre")

3. **Las vocales son diferentes**
   - "I" suena como "ai" → Nice = náis
   - "E" puede sonar como "i" → Meet = míit

---

### 🎭 SITUACIONES REALES

**Situación 1: Conocer a alguien nuevo**
```
A: Hello! My name is Anna.
B: Hi Anna! I'm Carlos. Nice to meet you.
A: Nice to meet you too!
```

**Situación 2: Presentación formal**
```
A: Good morning. What is your name?
B: Good morning. My name is Sofia Martinez.
A: Where are you from?
B: I am from Colombia.
```

---

### ⚠️ ERRORES COMUNES A EVITAR

❌ "My name Anna" → ✅ "My name IS Anna"  
❌ "I from Colombia" → ✅ "I AM from Colombia"  
❌ "Nice meet you" → ✅ "Nice TO meet you"  

---

### 📊 CRITERIOS DE EVALUACIÓN

Para pasar al siguiente ejercicio necesitas:
- ✅ Pronunciación ≥85% de precisión
- ✅ Entonación natural
- ✅ Fluidez sin pausas largas

**¡Prepárate para practicar!** 💪
""",
        "frases": [
            {
                "ingles": "Hello",
                "español": "Hola",
                "fonética": "jelóu",
                "contexto": "Saludo universal - úsalo en cualquier situación",
                "tip": "La H se pronuncia con aire, como si empañaras un vidrio"
            },
            {
                "ingles": "My name is Anna",
                "español": "Mi nombre es Anna",
                "fonética": "mái néim is ána",
                "contexto": "Presentación formal - úsalo en contextos profesionales",
                "tip": "Enfatiza 'name' y 'Anna', son las palabras más importantes"
            },
            {
                "ingles": "What is your name",
                "español": "¿Cuál es tu nombre?",
                "fonética": "uát is ior néim",
                "contexto": "Para preguntar el nombre de alguien formalmente",
                "tip": "La entonación sube al final porque es pregunta"
            },
            {
                "ingles": "I am from Colombia",
                "español": "Soy de Colombia",
                "fonética": "ái am from colómbia",
                "contexto": "Para indicar tu país de origen",
                "tip": "Practica 'I am' como una sola palabra: áiam"
            },
            {
                "ingles": "Nice to meet you",
                "español": "Mucho gusto / Encantado de conocerte",
                "fonética": "náis tu míit iú",
                "contexto": "Respuesta educada al conocer a alguien",
                "tip": "Es una frase fija, memorízala completa"
            },
            {
                "ingles": "How are you",
                "español": "¿Cómo estás?",
                "fonética": "jáu ar iú",
                "contexto": "Pregunta común para iniciar conversación",
                "tip": "La 'r' en 'are' es muy suave, casi no se escucha"
            },
            {
                "ingles": "I am fine thank you",
                "español": "Estoy bien, gracias",
                "fonética": "ái am fáin zánk iú",
                "contexto": "Respuesta estándar a 'How are you?'",
                "tip": "'Thank' lleva TH, saca un poco la lengua entre los dientes"
            },
            {
                "ingles": "Good morning",
                "español": "Buenos días",
                "fonética": "gud mórnin",
                "contexto": "Saludo antes del mediodía",
                "tip": "La 'g' de 'good' es suave, no como 'gato'"
            },
            {
                "ingles": "Where are you from",
                "español": "¿De dónde eres?",
                "fonética": "uér ar iú from",
                "contexto": "Para preguntar el origen de alguien",
                "tip": "Enfatiza 'where' y 'from'"
            },
            {
                "ingles": "Goodbye see you later",
                "español": "Adiós, nos vemos luego",
                "fonética": "gudbái si iú léiter",
                "contexto": "Despedida informal con expectativa de verse pronto",
                "tip": "'Later' rima con 'waiter' (mesero)"
            }
        ],
        "examen": [
            {
                "pregunta": "¿Cómo saludas formalmente en inglés?",
                "respuesta": "Hello",
                "explicacion": "Hello es el saludo más formal y universal"
            },
            {
                "pregunta": "¿Cómo te presentas diciendo tu nombre formalmente?",
                "respuesta": "My name is",
                "explicacion": "My name is [nombre] es la forma más formal de presentarse"
            },
            {
                "pregunta": "Di 'Mucho gusto' en inglés",
                "respuesta": "Nice to meet you",
                "explicacion": "Nice to meet you es la expresión estándar"
            },
            {
                "pregunta": "¿Cómo preguntas '¿Cómo estás?' en inglés?",
                "respuesta": "How are you",
                "explicacion": "How are you es la forma más común y neutral"
            },
            {
                "pregunta": "Responde 'Estoy bien, gracias' en inglés",
                "respuesta": "I am fine thank you",
                "explicacion": "I am fine thank you es la respuesta formal estándar"
            }
        ],
        "umbral_practica": 85,
        "umbral_examen": 80
    },
    
    "A1.2": {
        "tema": "Verbo TO BE (am/is/are)",
        "objetivo": "Dominar el verbo más importante del inglés",
        "duracion": "45-60 minutos",
        "explicacion": """
## 📚 LECCIÓN 2: Verbo TO BE

### 🎯 OBJETIVO DE LA LECCIÓN
Al finalizar podrás:
- ✅ Usar correctamente I am, You are, He/She is
- ✅ Formar oraciones afirmativas y negativas
- ✅ Hacer preguntas con el verbo to be
- ✅ Describir personas, lugares y estados

---

### 📖 CONJUGACIÓN COMPLETA

| Sujeto | Verbo | Contracción | Negativo |
|--------|-------|-------------|----------|
| I | am | I'm | I'm not |
| You | are | You're | You aren't |
| He | is | He's | He isn't |
| She | is | She's | She isn't |
| It | is | It's | It isn't |
| We | are | We're | We aren't |
| They | are | They're | They aren't |

---

### 🎯 USOS DEL VERBO TO BE

**A) IDENTIDAD** (quién eres)
- I am a student → Soy estudiante

**B) UBICACIÓN** (dónde estás)
- I am in Colombia → Estoy en Colombia

**C) ESTADO** (cómo estás)
- I am happy → Estoy feliz

**D) DESCRIPCIÓN** (características)
- She is tall → Ella es alta

---

### 💡 DIFERENCIAS CON EL ESPAÑOL

1. **En inglés SIEMPRE necesitas el verbo**
   - ❌ I student → ✅ I AM a student

2. **"Estar" y "Ser" = TO BE**
   - Soy alto → I AM tall
   - Estoy cansado → I AM tired

3. **El sujeto es OBLIGATORIO**
   - ❌ Am a student → ✅ I AM a student

---

### ⚠️ ERRORES COMUNES

❌ They is students → ✅ They ARE students  
❌ He am tall → ✅ He IS tall  
❌ She happy → ✅ She IS happy

---

### 📊 CRITERIOS DE DOMINIO

Precisión ≥85% para avanzar
""",
        "frases": [
            {
                "ingles": "I am a student",
                "español": "Soy un estudiante",
                "fonética": "ái am a stiúdent",
                "contexto": "Para identificar tu ocupación",
                "tip": "Contracción natural: I'm a student"
            },
            {
                "ingles": "You are my friend",
                "español": "Eres mi amigo",
                "fonética": "iú ar mái frend",
                "contexto": "Expresar relación con otra persona",
                "tip": "You're my friend suena más natural"
            },
            {
                "ingles": "She is a teacher",
                "español": "Ella es una profesora",
                "fonética": "shi is a tícher",
                "contexto": "Describir profesión (mujer)",
                "tip": "She's a teacher en conversación"
            },
            {
                "ingles": "He is tall",
                "español": "Él es alto",
                "fonética": "ji is tol",
                "contexto": "Describir características físicas",
                "tip": "La 'l' final es importante"
            },
            {
                "ingles": "It is a book",
                "español": "Es un libro",
                "fonética": "it is a buk",
                "contexto": "Identificar objetos",
                "tip": "It's a book - muy común"
            },
            {
                "ingles": "We are happy",
                "español": "Estamos felices",
                "fonética": "uí ar jápi",
                "contexto": "Expresar estados emocionales",
                "tip": "La 'pp' en happy con fuerza"
            },
            {
                "ingles": "They are from Spain",
                "español": "Ellos son de España",
                "fonética": "déi ar from spéin",
                "contexto": "Indicar origen de varias personas",
                "tip": "'They' suena como 'day'"
            },
            {
                "ingles": "I am not tired",
                "español": "No estoy cansado",
                "fonética": "ái am not táierd",
                "contexto": "Negar un estado",
                "tip": "I'm not tired - más natural"
            },
            {
                "ingles": "Are you ready",
                "español": "¿Estás listo?",
                "fonética": "ar iú rédi",
                "contexto": "Pregunta sobre preparación",
                "tip": "La entonación sube al final"
            },
            {
                "ingles": "This is my house",
                "español": "Esta es mi casa",
                "fonética": "dis is mái jáus",
                "contexto": "Presentar algo que te pertenece",
                "tip": "'This' con 'th' - lengua entre dientes"
            }
        ],
        "examen": [
            {
                "pregunta": "Completa: I ___ a student",
                "respuesta": "am",
                "explicacion": "Con 'I' siempre usamos 'am'"
            },
            {
                "pregunta": "Completa: She ___ happy",
                "respuesta": "is",
                "explicacion": "Con She/He/It usamos 'is'"
            },
            {
                "pregunta": "Completa: They ___ friends",
                "respuesta": "are",
                "explicacion": "Con They/We/You usamos 'are'"
            },
            {
                "pregunta": "Di 'Él es alto' en inglés",
                "respuesta": "He is tall",
                "explicacion": "He is tall - describir altura"
            },
            {
                "pregunta": "Pregunta '¿Estás listo?' en inglés",
                "respuesta": "Are you ready",
                "explicacion": "Orden invertido para pregunta"
            }
        ],
        "umbral_practica": 85,
        "umbral_examen": 80
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
        "nivel_actual": "A1.1",
        "fase": "explicacion",
        "frase_actual": 0,
        "intentos_frase": 0,
        "pregunta_actual": 0,
        "respuestas_correctas": 0,
        "historial": [],
        "racha_dias": 0,
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
            model="whisper-1",
            file=audio_file,
            language="en",
            prompt="English pronunciation practice."
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
    datos = cargar_datos()
    for key, value in datos.items():
        st.session_state[key] = value
    st.session_state.last_audio_id = None
    st.session_state.datos_cargados = True

variables_default = {
    "nivel_actual": "A1.1",
    "fase": "explicacion",
    "frase_actual": 0,
    "intentos_frase": 0,
    "pregunta_actual": 0,
    "respuestas_correctas": 0,
    "historial": [],
    "racha_dias": 0
}

for var, default in variables_default.items():
    if var not in st.session_state:
        st.session_state[var] = default

# ==================== VARIABLES ====================

nivel_actual = st.session_state.nivel_actual
config = CURRICULO.get(nivel_actual, CURRICULO["A1.1"])
niveles_list = list(CURRICULO.keys())
indice = niveles_list.index(nivel_actual)
progreso_total = int((indice / len(niveles_list)) * 100)

# ==================== SIDEBAR ====================

with st.sidebar:
    st.markdown(f"""
    <div style='text-align: center; background: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #667eea;'>👤 {st.session_state.usuario_activo.upper()}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("📊 Progreso", f"{progreso_total}%")
        dias = (datetime.now() - datetime.fromisoformat(st.session_state.fecha_inicio)).days
        st.metric("📅 Días", dias)
    with col2:
        st.metric("🔥 Racha", f"{st.session_state.racha_dias}")
        st.metric("💪 Intentos", st.session_state.intentos_frase)
    
    st.divider()
    
    st.markdown(f"""
    <div style='background: #667eea; color: white; padding: 15px; border-radius: 10px; margin-bottom: 15px;'>
        <h4>🎯 Nivel Actual</h4>
        <p style='font-size: 18px; margin: 0;'><strong>{nivel_actual}</strong></p>
        <p style='font-size: 14px; margin: 5px 0 0 0;'>{config['tema']}</p>
    </div>
    """, unsafe_allow_html=True)
    
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
    
    if st.session_state.historial:
        st.subheader("📈 Estadísticas")
        total = len(st.session_state.historial)
        promedio = sum(h['nota'] for h in st.session_state.historial) / total
        st.metric("Niveles Completados", total)
        st.metric("Promedio", f"{promedio:.1f}%")
    
    st.divider()
    
    if st.button("🔄 Repetir Nivel", use_container_width=True):
        st.session_state.fase = "explicacion"
        st.session_state.frase_actual = 0
        st.session_state.intentos_frase = 0
        guardar_datos()
        st.rerun()
    
    if st.button("🗑️ Reiniciar Todo", use_container_width=True):
        archivo = f"datos_{st.session_state.usuario_activo}.json"
        if os.path.exists(archivo):
            os.remove(archivo)
        st.session_state.clear()
        st.rerun()
    
    if st.button("🚪 Cerrar Sesión", use_container_width=True):
        st.session_state.usuario_activo = None
        st.rerun()

# ==================== HEADER ====================

st.markdown("""
<div style='background: white; padding: 20px; border-radius: 15px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
    <h1 style='color: #667eea; margin: 0;'>🎓 Nexus Pro Elite</h1>
    <p style='color: #666; margin: 5px 0 0 0;'>Sistema Profesional A1 → C1</p>
</div>
""", unsafe_allow_html=True)

# ==================== EXPLICACIÓN ====================

if st.session_state.fase == "explicacion":
    st.markdown(f"## 📖 {nivel_actual}: {config['tema']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**🎯 Objetivo:** {config['objetivo']}")
    with col2:
        st.info(f"**⏱️ Duración:** {config['duracion']}")
    with col3:
        st.info(f"**📊 Umbral:** {config['umbral_practica']}%")
    
    st.divider()
    
    st.markdown(config['explicacion'])
    
    st.divider()
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("✅ ENTENDÍ - COMENZAR PRÁCTICA", use_container_width=True, type="primary"):
            st.session_state.fase = "practica"
            st.session_state.frase_actual = 0
            st.session_state.intentos_frase = 0
            guardar_datos()
            st.rerun()

# ==================== PRÁCTICA ====================

elif st.session_state.fase == "practica":
    frase_obj = config['frases'][st.session_state.frase_actual]
    total_frases = len(config['frases'])
    umbral = config['umbral_practica']
    
    # Progreso
    progreso = st.session_state.frase_actual / total_frases
    st.progress(progreso)
    
    st.markdown(f"""
    <div class='metric-card'>
        <h3>💪 Ejercicio {st.session_state.frase_actual + 1}/{total_frases}</h3>
        <p><strong>Necesitas ≥{umbral}% para avanzar</strong></p>
        <p>Intentos en esta frase: {st.session_state.intentos_frase}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Frase del día
    st.markdown(f"""
    <div class='word-card'>
        <h4>🎯 FRASE DEL EJERCICIO</h4>
        <p style='font-size: 28px; color: #667eea; margin: 10px 0;'><strong>{frase_obj['ingles']}</strong></p>
        <p style='font-size: 18px;'><strong>🇪🇸 Español:</strong> {frase_obj['español']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 15px 0;'>
        <h4 style='color: #856404; margin: 0 0 10px 0;'>🗣️ CÓMO SE PRONUNCIA:</h4>
        <p style='font-size: 24px; color: #856404; margin: 0; font-family: monospace;'><strong>{frase_obj['fonética']}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"""
    **📝 Contexto de uso:** {frase_obj['contexto']}
    
    **💡 Tip de pronunciación:** {frase_obj['tip']}
    """)
    
    # Audio
    st.markdown("### 🔊 Escucha cómo se pronuncia:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        audio_b64 = generar_audio_ingles(frase_obj['ingles'], lento=False)
        if audio_b64:
            st.markdown("**Velocidad Normal:**")
            st.audio(base64.b64decode(audio_b64), format="audio/mp3")
    
    with col2:
        audio_lento = generar_audio_ingles(frase_obj['ingles'], lento=True)
        if audio_lento:
            st.markdown("**Velocidad Lenta (para aprender):**")
            st.audio(base64.b64decode(audio_lento), format="audio/mp3")
    
    st.divider()
    st.markdown("### 🎤 Ahora repite con tu micrófono:")
    st.warning("⚠️ **IMPORTANTE:** Debes alcanzar mínimo 85% de precisión para avanzar. ¡Puedes intentar las veces que necesites!")
    
    # Micrófono
    audio = mic_recorder(
        start_prompt="🎙️ GRABAR",
        stop_prompt="⏹️ DETENER",
        key=f"mic_p_{st.session_state.frase_actual}_{st.session_state.intentos_frase}"
    )
    
    if audio and audio.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio.get("id")
        st.session_state.intentos_frase += 1
        
        # Mostrar audio del usuario
        st.markdown("### 🎤 Tu Audio:")
        st.audio(audio['bytes'], format="audio/wav")
        
        with st.spinner("🎧 Analizando tu pronunciación..."):
            texto_usuario = transcribir_audio(audio['bytes'])
        
        if texto_usuario:
            st.markdown(f"**📝 Transcripción:** {texto_usuario}")
            precision = similitud_texto(texto_usuario, frase_obj['ingles'])
            
            # APROBADO
            if precision >= umbral:
                st.balloons()
                st.success(f"🎉 ¡EXCELENTE! Precisión: {precision}%")
                
                analisis = analizar_palabras(texto_usuario, frase_obj['ingles'])
                with st.expander("📊 Ver análisis detallado"):
                    for palabra in analisis:
                        st.markdown(palabra)
                
                st.divider()
                
                # ¿Última frase?
                if st.session_state.frase_actual >= total_frases - 1:
                    st.markdown("### 🔥 ¡COMPLETASTE TODAS LAS FRASES!")
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        if st.button("🎯 IR AL EXAMEN FINAL", use_container_width=True, type="primary"):
                            st.session_state.fase = "examen"
                            st.session_state.pregunta_actual = 0
                            st.session_state.respuestas_correctas = 0
                            guardar_datos()
                            st.rerun()
                else:
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        if st.button("➡️ SIGUIENTE FRASE", use_container_width=True, type="primary"):
                            st.session_state.frase_actual += 1
                            st.session_state.intentos_frase = 0
                            guardar_datos()
                            st.rerun()
            
            # REPROBADO
            else:
                st.error(f"❌ Precisión: {precision}% - Necesitas ≥{umbral}%")
                
                st.markdown(f"""
                <div class='error-box'>
                    <h4>📊 Análisis de tu pronunciación:</h4>
                    <p><strong>🎯 Objetivo:</strong> {frase_obj['ingles']}</p>
                    <p><strong>🎤 Dijiste:</strong> {texto_usuario}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 📝 Análisis Palabra por Palabra:")
                analisis = analizar_palabras(texto_usuario, frase_obj['ingles'])
                for palabra in analisis:
                    st.markdown(palabra)
                
                st.info(f"""
                💡 **Consejos para mejorar:**
                1. {frase_obj['tip']}
                2. Escucha el audio de arriba varias veces
                3. Repite despacio primero, luego más rápido
                4. Graba de nuevo cuando estés listo
                
                **Llevas {st.session_state.intentos_frase} intentos - ¡No te rindas!**
                """)

# ==================== EXAMEN ====================

# Busca la línea: elif st.session_state.fase == "practica":
# Y reemplaza EL BLOQUE COMPLETO de esa sección por esto:

elif st.session_state.fase == "practica":
    # --- AQUÍ ESTÁ EL ARREGLO (SEGURO ANTI-ERROR) ---
    # Si el número de frase es mayor al total, forzamos ir al examen para que no se rompa
    frases_disponibles = config.get('frases', [])
    if st.session_state.frase_actual >= len(frases_disponibles):
        st.session_state.fase = "examen"
        st.session_state.pregunta_actual = 0
        st.rerun()
    # ------------------------------------------------

    frase_obj = frases_disponibles[st.session_state.frase_actual]
    total_frases = len(frases_disponibles)
    umbral = config['umbral_practica']
    
    # Progreso
    progreso = st.session_state.frase_actual / total_frases
    st.progress(progreso)
    
    st.markdown(f"""
    <div class='metric-card'>
        <h3>💪 Ejercicio {st.session_state.frase_actual + 1}/{total_frases}</h3>
        <p><strong>Necesitas ≥{umbral}% para avanzar</strong></p>
        <p>Intentos en esta frase: {st.session_state.intentos_frase}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Frase del día
    st.markdown(f"""
    <div class='word-card'>
        <h4>🎯 FRASE DEL EJERCICIO</h4>
        <p style='font-size: 28px; color: #667eea; margin: 10px 0;'><strong>{frase_obj['ingles']}</strong></p>
        <p style='font-size: 18px;'><strong>🇪🇸 Español:</strong> {frase_obj['español']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div style='background: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 5px; margin: 15px 0;'>
        <h4 style='color: #856404; margin: 0 0 10px 0;'>🗣️ CÓMO SE PRONUNCIA:</h4>
        <p style='font-size: 24px; color: #856404; margin: 0; font-family: monospace;'><strong>{frase_obj['fonética']}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.info(f"""
    **📝 Contexto de uso:** {frase_obj['contexto']}
    
    **💡 Tip de pronunciación:** {frase_obj['tip']}
    """)
    
    # Audio
    st.markdown("### 🔊 Escucha cómo se pronuncia:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        audio_b64 = generar_audio_ingles(frase_obj['ingles'], lento=False)
        if audio_b64:
            st.markdown("**Velocidad Normal:**")
            st.audio(base64.b64decode(audio_b64), format="audio/mp3")
    
    with col2:
        audio_lento = generar_audio_ingles(frase_obj['ingles'], lento=True)
        if audio_lento:
            st.markdown("**Velocidad Lenta (para aprender):**")
            st.audio(base64.b64decode(audio_lento), format="audio/mp3")
    
    st.divider()
    st.markdown("### 🎤 Ahora repite con tu micrófono:")
    st.warning("⚠️ **IMPORTANTE:** Debes alcanzar mínimo 85% de precisión para avanzar. ¡Puedes intentar las veces que necesites!")
    
    # Micrófono
    audio = mic_recorder(
        start_prompt="🎙️ GRABAR",
        stop_prompt="⏹️ DETENER",
        key=f"mic_p_{st.session_state.frase_actual}_{st.session_state.intentos_frase}"
    )
    
    if audio and audio.get("id") != st.session_state.last_audio_id:
        st.session_state.last_audio_id = audio.get("id")
        st.session_state.intentos_frase += 1
        
        # Mostrar audio del usuario
        st.markdown("### 🎤 Tu Audio:")
        st.audio(audio['bytes'], format="audio/wav")
        
        with st.spinner("🎧 Analizando tu pronunciación..."):
            texto_usuario = transcribir_audio(audio['bytes'])
        
        if texto_usuario:
            st.markdown(f"**📝 Transcripción:** {texto_usuario}")
            precision = similitud_texto(texto_usuario, frase_obj['ingles'])
            
            # APROBADO
            if precision >= umbral:
                st.balloons()
                st.success(f"🎉 ¡EXCELENTE! Precisión: {precision}%")
                
                analisis = analizar_palabras(texto_usuario, frase_obj['ingles'])
                with st.expander("📊 Ver análisis detallado"):
                    for palabra in analisis:
                        st.markdown(palabra)
                
                st.divider()
                
                # ¿Última frase?
                if st.session_state.frase_actual >= total_frases - 1:
                    st.markdown("### 🔥 ¡COMPLETASTE TODAS LAS FRASES!")
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        if st.button("🎯 IR AL EXAMEN FINAL", use_container_width=True, type="primary"):
                            st.session_state.fase = "examen"
                            st.session_state.pregunta_actual = 0
                            st.session_state.respuestas_correctas = 0
                            guardar_datos()
                            st.rerun()
                else:
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        if st.button("➡️ SIGUIENTE FRASE", use_container_width=True, type="primary"):
                            st.session_state.frase_actual += 1
                            st.session_state.intentos_frase = 0
                            guardar_datos()
                            st.rerun()
            
            # REPROBADO
            else:
                st.error(f"❌ Precisión: {precision}% - Necesitas ≥{umbral}%")
                
                st.markdown(f"""
                <div class='error-box'>
                    <h4>📊 Análisis de tu pronunciación:</h4>
                    <p><strong>🎯 Objetivo:</strong> {frase_obj['ingles']}</p>
                    <p><strong>🎤 Dijiste:</strong> {texto_usuario}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("### 📝 Análisis Palabra por Palabra:")
                analisis = analizar_palabras(texto_usuario, frase_obj['ingles'])
                for palabra in analisis:
                    st.markdown(palabra)
                
                st.info(f"""
                💡 **Consejos para mejorar:**
                1. {frase_obj['tip']}
                2. Escucha el audio de arriba varias veces
                3. Repite despacio primero, luego más rápido
                4. Graba de nuevo cuando estés listo
                
                **Llevas {st.session_state.intentos_frase} intentos - ¡No te rindas!**
                """)

# ==================== FOOTER ====================

st.divider()
st.markdown("""
<div style='text-align: center; color: white; padding: 20px;'>
    <p>🎓 Nexus Pro Elite v4.0 | Sistema Profesional de Inglés A1→C1</p>
    <p>Desarrollado con ❤️ para tu éxito</p>
</div>
""", unsafe_allow_html=True)

