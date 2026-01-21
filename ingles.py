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

# ==================== CONFIGURACIÓN INICIAL ====================
st.set_page_config(
    page_title="Nexus Pro Elite - Bootcamp A1→C1",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CSS (ESTILOS VISUALES) ====================
# Forzamos texto negro (#000000) para evitar que se vea blanco sobre blanco
st.markdown("""
<style>
    /* Fondo degradado de la aplicación */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Regla Maestra: Texto negro en todas las cajas de contenido */
    .metric-card, .word-card, .success-box, .error-box, .info-box, .explanation-box {
        color: #000000 !important;
    }
    
    /* Forzar color en etiquetas específicas */
    .metric-card h1, .metric-card h2, .metric-card h3, .metric-card h4, .metric-card p, .metric-card li, .metric-card td, .metric-card th {
        color: #000000 !important;
    }
    
    /* Caja Blanca Principal */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    /* Caja de Explicación (Para las tablas y teoría) */
    .explanation-box {
        background: white;
        padding: 25px;
        border-radius: 10px;
        color: #000000 !important;
        margin-bottom: 20px;
        border-left: 5px solid #667eea;
    }
    .explanation-box table {
        width: 100%;
        border-collapse: collapse;
        color: #000000 !important;
    }
    .explanation-box td, .explanation-box th {
        border: 1px solid #ddd;
        padding: 8px;
        color: #000000 !important;
    }
    .explanation-box tr:nth-child(even){background-color: #f2f2f2;}

    /* Caja de Éxito (Verde) */
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #155724 !important;
    }
    .success-box h3, .success-box p { color: #155724 !important; }
    
    /* Caja de Error (Rojo) */
    .error-box {
        background: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #721c24 !important;
    }
    .error-box p, .error-box h4 { color: #721c24 !important; }
    
    /* Caja de Información (Azul) */
    .info-box {
        background: #d1ecf1;
        border-left: 4px solid #0c5460;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
        color: #0c5460 !important;
    }
    .info-box p, .info-box h3 { color: #0c5460 !important; }
    
    /* Tarjeta de la Palabra (Gris Claro) */
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

# ==================== USUARIOS Y LOGIN ====================
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

# ==================== CURRÍCULO COMPLETO (CONTENIDO EDUCATIVO) ====================

CURRICULO = {
    "A1.1": {
        "tema": "Saludos y Presentaciones Básicas",
        "objetivo": "Aprender a saludar y presentarse",
        "duracion": "30-45 minutos",
        "explicacion": """
<div class='explanation-box'>
    <h2>📚 LECCIÓN 1: Saludos y Presentaciones</h2>
    <p>Antes de practicar, revisemos lo básico:</p>
    <hr>
    <h3>1. SALUDOS (Greetings)</h3>
    <ul>
        <li><strong>Hello</strong>: Hola (Formal/Universal)</li>
        <li><strong>Hi</strong>: Hola (Informal)</li>
        <li><strong>Good morning</strong>: Buenos días</li>
        <li><strong>Good afternoon</strong>: Buenas tardes</li>
        <li><strong>Good evening</strong>: Buenas noches (al llegar)</li>
    </ul>
    <br>
    <h3>2. PRESENTARSE</h3>
    <p>Formal: <strong>"My name is..."</strong> (Mi nombre es...)</p>
    <p>Informal: <strong>"I'm..."</strong> (Soy...)</p>
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
<div class='explanation-box'>
    <h2>📚 LECCIÓN 2: Verbo TO BE (Ser o Estar)</h2>
    <p>Este verbo es fundamental. Significa SER (Yo soy) o ESTAR (Yo estoy).</p>
    <hr>
    <h3>📖 CONJUGACIÓN</h3>
    <table border="1">
      <tr><th>Pronombre</th><th>Verbo</th><th>Ejemplo</th></tr>
      <tr><td>I (Yo)</td><td><strong>am</strong></td><td>I am happy</td></tr>
      <tr><td>You (Tú)</td><td><strong>are</strong></td><td>You are tall</td></tr>
      <tr><td>He/She/It</td><td><strong>is</strong></td><td>She is a doctor</td></tr>
      <tr><td>We/They</td><td><strong>are</strong></td><td>We are friends</td></tr>
    </table>
    <br>
    <p>⚠️ <strong>REGLA:</strong> Nunca digas "I is" o "You is".</p>
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

    "A1.3": {
        "tema": "Artículos (a/an/the) y Pronombres",
        "objetivo": "Usar correctamente artículos y pronombres",
        "duracion": "40 minutos",
        "explicacion": """
<div class='explanation-box'>
    <h2>📚 LECCIÓN 3: Artículos y Pronombres</h2>
    <h3>Artículos</h3>
    <ul>
        <li><strong>A</strong>: Un/Una (antes de consonante). Ej: A cat.</li>
        <li><strong>AN</strong>: Un/Una (antes de vocal). Ej: An apple.</li>
        <li><strong>THE</strong>: El/La/Los (Específico). Ej: The book.</li>
    </ul>
</div>
""",
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

    "A1.4": {
        "tema": "Números, Cantidades y Fechas",
        "objetivo": "Contar y decir cantidades",
        "duracion": "40 minutos",
        "explicacion": """<div class='explanation-box'><h3>📚 LECCIÓN 4: Números</h3><p>One, two, three... How much? How many?</p></div>""",
        "frases": [
            {"ingles": "I am twenty five years old", "español": "Tengo 25 años", "fonética": "ái am tuénti fáiv yírs old", "contexto": "Edad", "tip": "Years old"},
            {"ingles": "There are ten people", "español": "Hay diez personas", "fonética": "der ar ten pípol", "contexto": "Cantidad", "tip": "There are"},
            {"ingles": "I have three cats", "español": "Tengo tres gatos", "fonética": "ái jav zrí cats", "contexto": "Mascotas", "tip": "Three=Zrí"},
            {"ingles": "The price is fifteen dollars", "español": "Son quince dólares", "fonética": "de práis is fiftín dólars", "contexto": "Precio", "tip": "Fifteen"},
            {"ingles": "She has two brothers", "español": "Tiene dos hermanos", "fonética": "shi jas tu bróders", "contexto": "Familia", "tip": "Two"},
            {"ingles": "We need five chairs", "español": "Necesitamos 5 sillas", "fonética": "uí níd fáiv chérs", "contexto": "Necesidad", "tip": "Five"},
            {"ingles": "It costs twenty dollars", "español": "Cuesta 20 dólares", "fonética": "it costs tuénti dólars", "contexto": "Costo", "tip": "Twenty"},
            {"ingles": "I work eight hours", "español": "Trabajo 8 horas", "fonética": "ái uórk éit áuers", "contexto": "Tiempo", "tip": "Eight=Eit"},
            {"ingles": "There are seven days", "español": "Hay 7 días", "fonética": "der ar séven déis", "contexto": "Semana", "tip": "Seven"},
            {"ingles": "I have one hundred dollars", "español": "Tengo 100 dólares", "fonética": "ái jav uan jándred dólars", "contexto": "Dinero", "tip": "Hundred"}
        ],
        "examen": [
            {"pregunta": "Di 'cinco'", "respuesta": "five", "explicacion": "5"},
            {"pregunta": "Di 'Tengo 20 años'", "respuesta": "I am twenty years old", "explicacion": "Age"},
            {"pregunta": "Di 'Tres gatos'", "respuesta": "three cats", "explicacion": "3"},
            {"pregunta": "Di 'diez'", "respuesta": "ten", "explicacion": "10"},
            {"pregunta": "Completa: It costs ___ dollars (15)", "respuesta": "fifteen", "explicacion": "15"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },

    "A1.5": {
        "tema": "Días, Meses y Horarios",
        "objetivo": "Decir la fecha y la hora",
        "duracion": "40 minutos",
        "explicacion": """<div class='explanation-box'><h3>📚 LECCIÓN 5: Tiempo</h3><p>Monday, Tuesday... January, February... What time is it?</p></div>""",
        "frases": [
            {"ingles": "Today is Monday", "español": "Hoy es lunes", "fonética": "tudéi is mándei", "contexto": "Día", "tip": "Monday"},
            {"ingles": "My birthday is in May", "español": "Mi cumple es en mayo", "fonética": "mái bérzdei is in méi", "contexto": "Mes", "tip": "In May"},
            {"ingles": "What time is it", "español": "¿Qué hora es?", "fonética": "uát táim is it", "contexto": "Pregunta", "tip": "Time"},
            {"ingles": "It is three o clock", "español": "Son las 3 en punto", "fonética": "it is zrí o clok", "contexto": "Hora", "tip": "O'clock"},
            {"ingles": "I wake up at six", "español": "Me despierto a las 6", "fonética": "ái uéik ap at siks", "contexto": "Rutina", "tip": "At six"},
            {"ingles": "The class starts at nine", "español": "La clase empieza a las 9", "fonética": "de clas starts at náin", "contexto": "Horario", "tip": "Nine"},
            {"ingles": "We work from Monday to Friday", "español": "Trabajamos lun a vie", "fonética": "uí uórk from mándei tu fráidei", "contexto": "Rango", "tip": "From-To"},
            {"ingles": "Christmas is in December", "español": "Navidad es en diciembre", "fonética": "crísmas is in disémber", "contexto": "Festivo", "tip": "December"},
            {"ingles": "See you on Saturday", "español": "Nos vemos el sábado", "fonética": "si iú on sáterdei", "contexto": "Cita", "tip": "On Saturday"},
            {"ingles": "The meeting is at two thirty", "español": "La reunión es 2:30", "fonética": "de mítin is at tu zérti", "contexto": "Reunión", "tip": "Thirty"}
        ],
        "examen": [
            {"pregunta": "Di 'lunes'", "respuesta": "Monday", "explicacion": "Día"},
            {"pregunta": "Pregunta la hora", "respuesta": "What time is it", "explicacion": "Hora"},
            {"pregunta": "Di 'Son las 3'", "respuesta": "It is three o clock", "explicacion": "3:00"},
            {"pregunta": "Di 'mayo'", "respuesta": "May", "explicacion": "Mes"},
            {"pregunta": "Completa: at ___ (6)", "respuesta": "six", "explicacion": "6"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },

    "A1.6": {
        "tema": "Familia y Relaciones",
        "objetivo": "Hablar de la familia",
        "duracion": "40 minutos",
        "explicacion": """<div class='explanation-box'><h3>📚 LECCIÓN 6: Familia</h3><p>Father, Mother, Brother, Sister, Son, Daughter.</p></div>""",
        "frases": [
            {"ingles": "This is my father", "español": "Este es mi padre", "fonética": "dis is mái fáder", "contexto": "Presentación", "tip": "Father"},
            {"ingles": "I have two brothers", "español": "Tengo 2 hermanos", "fonética": "ái jav tu bróders", "contexto": "Cantidad", "tip": "Brothers"},
            {"ingles": "My sister is a doctor", "español": "Mi hermana es doctora", "fonética": "mái síster is a dóctor", "contexto": "Profesión", "tip": "Sister"},
            {"ingles": "Her husband is tall", "español": "Su esposo es alto", "fonética": "jer jásband is tol", "contexto": "Esposo", "tip": "Husband"},
            {"ingles": "My mother cooks well", "español": "Mi madre cocina bien", "fonética": "mái máder cuks uél", "contexto": "Madre", "tip": "Mother"},
            {"ingles": "I love my family", "español": "Amo a mi familia", "fonética": "ái lav mái fámili", "contexto": "Sentimiento", "tip": "Family"},
            {"ingles": "My parents live in Colombia", "español": "Mis padres viven en Colombia", "fonética": "mái pérents liv in colómbia", "contexto": "Padres", "tip": "Parents"},
            {"ingles": "She has one daughter", "español": "Tiene una hija", "fonética": "shi jas uan dóter", "contexto": "Hija", "tip": "Daughter"},
            {"ingles": "We are a big family", "español": "Somos familia grande", "fonética": "uí ar a big fámili", "contexto": "Descripción", "tip": "Big"},
            {"ingles": "My grandparents are old", "español": "Mis abuelos son viejos", "fonética": "mái grándpérents ar old", "contexto": "Abuelos", "tip": "Grandparents"}
        ],
        "examen": [
            {"pregunta": "Di 'padre'", "respuesta": "father", "explicacion": "Papá"},
            {"pregunta": "Di 'Tengo 2 hermanos'", "respuesta": "I have two brothers", "explicacion": "Hermanos"},
            {"pregunta": "Di 'hermana'", "respuesta": "sister", "explicacion": "Sister"},
            {"pregunta": "Completa: My ___ (madre)", "respuesta": "mother", "explicacion": "Mamá"},
            {"pregunta": "Di 'Mi familia'", "respuesta": "My family", "explicacion": "Familia"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },

    "A2.1": {
        "tema": "Presente Simple - Rutinas",
        "objetivo": "Hablar de hábitos",
        "duracion": "50 minutos",
        "explicacion": """<div class='explanation-box'><h3>📚 LECCIÓN 7: Rutinas</h3><p>I work, She works (add S), I don't work, Do you work?</p></div>""",
        "frases": [
            {"ingles": "I wake up at seven", "español": "Despierto a las 7", "fonética": "ái uéik ap at séven", "contexto": "Rutina", "tip": "Wake up"},
            {"ingles": "She drinks coffee every day", "español": "Ella toma café diario", "fonética": "shi drinks cófi évri déi", "contexto": "Hábito 3ra", "tip": "Drinks"},
            {"ingles": "We go to work by bus", "español": "Vamos en bus", "fonética": "uí góu tu uórk bái bas", "contexto": "Transporte", "tip": "Go"},
            {"ingles": "He plays soccer on weekends", "español": "Juega fútbol findes", "fonética": "ji pléis sóker on uíkends", "contexto": "Deporte", "tip": "Plays"},
            {"ingles": "They study English", "español": "Estudian inglés", "fonética": "déi stádi ínglish", "contexto": "Estudio", "tip": "Study"},
            {"ingles": "I do not like vegetables", "español": "No me gustan verduras", "fonética": "ái du not láik véyetabols", "contexto": "Gustos neg", "tip": "Don't"},
            {"ingles": "She does not work here", "español": "No trabaja aquí", "fonética": "shi das not uórk jír", "contexto": "Neg 3ra", "tip": "Doesn't"},
            {"ingles": "Do you speak Spanish", "español": "¿Hablas español?", "fonética": "du iú spík spánish", "contexto": "Pregunta", "tip": "Do"},
            {"ingles": "Does he live in Madrid", "español": "¿Vive en Madrid?", "fonética": "das ji liv in mádrid", "contexto": "Pregunta 3ra", "tip": "Does"},
            {"ingles": "We always eat breakfast", "español": "Siempre desayunamos", "fonética": "uí ólueis ít brékfast", "contexto": "Frecuencia", "tip": "Always"}
        ],
        "examen": [
            {"pregunta": "Completa: She ___ coffee (drink)", "respuesta": "drinks", "explicacion": "+S"},
            {"pregunta": "Negativo: I ___ like", "respuesta": "do not", "explicacion": "Don't"},
            {"pregunta": "Pregunta: ___ you speak?", "respuesta": "Do", "explicacion": "Do"},
            {"pregunta": "Di 'Ella trabaja aquí'", "respuesta": "She works here", "explicacion": "Works"},
            {"pregunta": "Negativo: He ___ work", "respuesta": "doesn't", "explicacion": "Doesn't"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },

    "A2.2": {
        "tema": "Pasado Simple Regular",
        "objetivo": "Verbos con ED",
        "duracion": "50 minutos",
        "explicacion": """<div class='explanation-box'><h3>📚 LECCIÓN 8: Pasado Regular</h3><p>Work -> Worked, Play -> Played. Did you work? I didn't work.</p></div>""",
        "frases": [
            {"ingles": "I worked yesterday", "español": "Trabajé ayer", "fonética": "ái uórkt yésterdei", "contexto": "Trabajo", "tip": "Worked"},
            {"ingles": "She studied English", "español": "Estudió inglés", "fonética": "shi stádid ínglish", "contexto": "Estudio", "tip": "Studied"},
            {"ingles": "We played soccer", "español": "Jugamos fútbol", "fonética": "uí pléid sóker", "contexto": "Juego", "tip": "Played"},
            {"ingles": "They visited Paris", "español": "Visitaron París", "fonética": "déi vísited páris", "contexto": "Viaje", "tip": "Visited"},
            {"ingles": "I watched a movie", "español": "Vi una película", "fonética": "ái uócht a múvi", "contexto": "TV", "tip": "Watched"},
            {"ingles": "He cooked dinner", "español": "Cocinó cena", "fonética": "ji cukt díner", "contexto": "Cocina", "tip": "Cooked"},
            {"ingles": "I did not work", "español": "No trabajé", "fonética": "ái did not uórk", "contexto": "Negativo", "tip": "Didn't"},
            {"ingles": "Did you study", "español": "¿Estudiaste?", "fonética": "did iú stádi", "contexto": "Pregunta", "tip": "Did"},
            {"ingles": "We lived in Spain", "español": "Vivimos en España", "fonética": "uí livd in spéin", "contexto": "Vivir", "tip": "Lived"},
            {"ingles": "She called me yesterday", "español": "Me llamó ayer", "fonética": "shi cold mi yésterdei", "contexto": "Llamada", "tip": "Called"}
        ],
        "examen": [
            {"pregunta": "Pasado de work", "respuesta": "worked", "explicacion": "ED"},
            {"pregunta": "Di 'Trabajé ayer'", "respuesta": "I worked yesterday", "explicacion": "Pasado"},
            {"pregunta": "Negativo: I ___ work", "respuesta": "didn't", "explicacion": "Didn't"},
            {"pregunta": "Pregunta: ___ you study?", "respuesta": "Did", "explicacion": "Did"},
            {"pregunta": "Pasado de play", "respuesta": "played", "explicacion": "ED"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },

    "A2.3": {
        "tema": "Pasado Simple Irregular",
        "objetivo": "Verbos que cambian",
        "duracion": "50 minutos",
        "explicacion": """<div class='explanation-box'><h3>📚 LECCIÓN 9: Pasado Irregular</h3><p>Go->Went, Have->Had, Do->Did, See->Saw.</p></div>""",
        "frases": [
            {"ingles": "I went to the park", "español": "Fui al parque", "fonética": "ái uent tu de park", "contexto": "Ir", "tip": "Went"},
            {"ingles": "She had breakfast", "español": "Ella desayunó", "fonética": "shi jad brékfast", "contexto": "Tener", "tip": "Had"},
            {"ingles": "We saw a movie", "español": "Vimos película", "fonética": "uí so a múvi", "contexto": "Ver", "tip": "Saw"},
            {"ingles": "They ate pizza", "español": "Comieron pizza", "fonética": "déi éit pítsa", "contexto": "Comer", "tip": "Ate"},
            {"ingles": "I drank water", "español": "Bebí agua", "fonética": "ái drank uóter", "contexto": "Beber", "tip": "Drank"},
            {"ingles": "He came home late", "español": "Llegó tarde", "fonética": "ji kéim jóum léit", "contexto": "Venir", "tip": "Came"},
            {"ingles": "She said yes", "español": "Dijo sí", "fonética": "shi sed yes", "contexto": "Decir", "tip": "Said"},
            {"ingles": "I made a cake", "español": "Hice pastel", "fonética": "ái méid a kéik", "contexto": "Hacer", "tip": "Made"},
            {"ingles": "We got a gift", "español": "Recibimos regalo", "fonética": "uí got a gift", "contexto": "Obtener", "tip": "Got"},
            {"ingles": "They did homework", "español": "Hicieron tarea", "fonética": "déi did jómuork", "contexto": "Hacer", "tip": "Did"}
        ],
        "examen": [
            {"pregunta": "Pasado de Go", "respuesta": "went", "explicacion": "Went"},
            {"pregunta": "Di 'Fui al parque'", "respuesta": "I went to the park", "explicacion": "Went"},
            {"pregunta": "Pasado de Eat", "respuesta": "ate", "explicacion": "Ate"},
            {"pregunta": "Pasado de See", "respuesta": "saw", "explicacion": "Saw"},
            {"pregunta": "Di 'Ella tuvo suerte' (had)", "respuesta": "She had luck", "explicacion": "Had"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },

    "A2.4": {
        "tema": "Futuro (Will / Going to)",
        "objetivo": "Planes y predicciones",
        "duracion": "50 minutos",
        "explicacion": """<div class='explanation-box'><h3>📚 LECCIÓN 10: Futuro</h3><p>Will (espontáneo), Going to (plan). I will help, I am going to travel.</p></div>""",
        "frases": [
            {"ingles": "I will help you", "español": "Te ayudaré", "fonética": "ái uil jelp iú", "contexto": "Ayuda", "tip": "Will"},
            {"ingles": "She is going to travel", "español": "Va a viajar", "fonética": "shi is góin tu trável", "contexto": "Plan", "tip": "Going to"},
            {"ingles": "It will rain tomorrow", "español": "Lloverá mañana", "fonética": "it uil réin tumórou", "contexto": "Clima", "tip": "Will"},
            {"ingles": "We are going to study", "español": "Vamos a estudiar", "fonética": "uí ar góin tu stádi", "contexto": "Plan", "tip": "Going to"},
            {"ingles": "They will arrive soon", "español": "Llegarán pronto", "fonética": "déi uil aráiv sun", "contexto": "Llegada", "tip": "Will"},
            {"ingles": "I am going to buy a car", "español": "Voy a comprar carro", "fonética": "ái am góin tu bái a car", "contexto": "Compra", "tip": "Going to"},
            {"ingles": "He will call you", "español": "Te llamará", "fonética": "ji uil col iú", "contexto": "Promesa", "tip": "Will"},
            {"ingles": "We will not go", "español": "No iremos", "fonética": "uí uil not góu", "contexto": "Negativo", "tip": "Won't"},
            {"ingles": "Are you going to come", "español": "¿Vas a venir?", "fonética": "ar iú góin tu cam", "contexto": "Pregunta", "tip": "Going to"},
            {"ingles": "It is going to snow", "español": "Va a nevar", "fonética": "it is góin tu snóu", "contexto": "Predicción", "tip": "Going to"}
        ],
        "examen": [
            {"pregunta": "Completa: I ___ help you", "respuesta": "will", "explicacion": "Will"},
            {"pregunta": "Di 'Voy a estudiar'", "respuesta": "I am going to study", "explicacion": "Going to"},
            {"pregunta": "Futuro de rain (will)", "respuesta": "will rain", "explicacion": "Will"},
            {"pregunta": "Negativo: We ___ not go", "respuesta": "will", "explicacion": "Will"},
            {"pregunta": "Pregunta: ___ you going to?", "respuesta": "Are", "explicacion": "Are"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },

    "B1.1": {
        "tema": "Presente Perfecto",
        "objetivo": "Experiencias (Have/Has + Participio)",
        "duracion": "60 minutos",
        "explicacion": """<div class='explanation-box'><h3>📚 LECCIÓN 11: Presente Perfecto</h3><p>I have worked, She has eaten. Ever, Never, Just, Yet.</p></div>""",
        "frases": [
            {"ingles": "I have been to Paris", "español": "He estado en París", "fonética": "ái jav bin tu páris", "contexto": "Experiencia", "tip": "Have been"},
            {"ingles": "She has just arrived", "español": "Acaba de llegar", "fonética": "shi jas yast aráivd", "contexto": "Reciente", "tip": "Has just"},
            {"ingles": "Have you ever tried sushi", "español": "¿Alguna vez sushi?", "fonética": "jav iú éver tráid súshi", "contexto": "Pregunta", "tip": "Ever"},
            {"ingles": "I have never seen snow", "español": "Nunca vi nieve", "fonética": "ái jav néver sin snóu", "contexto": "Nunca", "tip": "Never"},
            {"ingles": "We have lived here for five years", "español": "Vivimos aquí 5 años", "fonética": "uí jav livd jir for fáiv yírs", "contexto": "Duración", "tip": "For"},
            {"ingles": "He has worked since Monday", "español": "Trabaja desde el lunes", "fonética": "ji jas uórkt sins mándei", "contexto": "Inicio", "tip": "Since"},
            {"ingles": "They have already eaten", "español": "Ya comieron", "fonética": "déi jav olrédi íten", "contexto": "Ya", "tip": "Already"},
            {"ingles": "I have not finished yet", "español": "No terminé aún", "fonética": "ái jav not fínisht yet", "contexto": "Aún", "tip": "Yet"},
            {"ingles": "She has lost her keys", "español": "Perdió llaves", "fonética": "shi jas lost jer kíis", "contexto": "Efecto", "tip": "Lost"},
            {"ingles": "Have they arrived yet", "español": "¿Ya llegaron?", "fonética": "jav déi aráivd yet", "contexto": "Pregunta", "tip": "Yet"}
        ],
        "examen": [
            {"pregunta": "Completa: I ___ been", "respuesta": "have", "explicacion": "Have"},
            {"pregunta": "Completa: She ___ just", "respuesta": "has", "explicacion": "Has"},
            {"pregunta": "Di 'He estado en París'", "respuesta": "I have been to Paris", "explicacion": "Have been"},
            {"pregunta": "Completa: lived ___ 5 years", "respuesta": "for", "explicacion": "For"},
            {"pregunta": "Pregunta: ___ you ever?", "respuesta": "Have", "explicacion": "Have"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },

    "B1.2": {
        "tema": "Modales (Can, Could, Should, Must)",
        "objetivo": "Poder, deber, consejo",
        "duracion": "60 minutos",
        "explicacion": """<div class='explanation-box'><h3>📚 LECCIÓN 12: Modales</h3><p>Can (poder), Could (podría), Should (consejo), Must (obligación).</p></div>""",
        "frases": [
            {"ingles": "I can speak English", "español": "Puedo hablar inglés", "fonética": "ái can spík ínglish", "contexto": "Habilidad", "tip": "Can"},
            {"ingles": "She could help you", "español": "Podría ayudarte", "fonética": "shi cud jelp iú", "contexto": "Posibilidad", "tip": "Could"},
            {"ingles": "You should study more", "español": "Deberías estudiar", "fonética": "iú shud stádi mor", "contexto": "Consejo", "tip": "Should"},
            {"ingles": "I must go now", "español": "Debo irme", "fonética": "ái mast góu náu", "contexto": "Obligación", "tip": "Must"},
            {"ingles": "Can you swim", "español": "¿Puedes nadar?", "fonética": "can iú suím", "contexto": "Pregunta", "tip": "Can"},
            {"ingles": "I cannot drive", "español": "No puedo conducir", "fonética": "ái cánot dráiv", "contexto": "Negativo", "tip": "Cannot"},
            {"ingles": "We should not lie", "español": "No deberíamos mentir", "fonética": "uí shúdnt lái", "contexto": "Consejo neg", "tip": "Shouldn't"},
            {"ingles": "Could I ask a question", "español": "¿Podría preguntar?", "fonética": "cud ái ask a cuéschen", "contexto": "Permiso", "tip": "Could"},
            {"ingles": "You must wear a seatbelt", "español": "Debes usar cinturón", "fonética": "iú mast uér a sítbelt", "contexto": "Ley", "tip": "Must"},
            {"ingles": "She can play the piano", "español": "Puede tocar piano", "fonética": "shi can pléi de piáno", "contexto": "Habilidad", "tip": "Can"}
        ],
        "examen": [
            {"pregunta": "Completa: I ___ speak (habilidad)", "respuesta": "can", "explicacion": "Can"},
            {"pregunta": "Consejo: You ___ study", "respuesta": "should", "explicacion": "Should"},
            {"pregunta": "Obligación: I ___ go", "respuesta": "must", "explicacion": "Must"},
            {"pregunta": "Posibilidad: I ___ help", "respuesta": "could", "explicacion": "Could"},
            {"pregunta": "Negativo de can", "respuesta": "cannot", "explicacion": "Cannot"}
        ],
        "umbral_practica": 85, "umbral_examen": 80
    },

    "B2.1": {
        "tema": "Condicionales Tipo 1 y 2",
        "objetivo": "Condiciones reales e hipotéticas",
        "duracion": "60 minutos",
        "explicacion": """<div class='explanation-box'><h3>📚 LECCIÓN 13: Condicionales</h3><p>Tipo 1: If + Presente, Will. Tipo 2: If + Pasado, Would.</p></div>""",
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

# ==================== FUNCIONES (LÓGICA DEL APP) ====================

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

# ==================== ESTADO DE LA SESIÓN ====================

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

# ==================== BARRA LATERAL (SIDEBAR) ====================

nivel_actual = st.session_state.nivel_actual
config = CURRICULO.get(nivel_actual, CURRICULO["A1.1"])
niveles_list = list(CURRICULO.keys())
indice = niveles_list.index(nivel_actual)
progreso_total = int((indice / len(niveles_list)) * 100)

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
        st.markdown(f"""
        <div class='metric-card'>
            <h4>🎯 Nivel Actual</h4>
            <p style='font-size: 18px; margin: 0;'><strong>{nivel_actual}</strong></p>
            <p style='font-size: 14px; margin: 5px 0 0 0;'>{config['tema']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("🗺️ Roadmap")
        for i, key in enumerate(niveles_list):
            tema = CURRICULO[key]["tema"]
            if i < indice:
                st.success(f"✅ {key}: {tema[:20]}...")
            elif i == indice:
                st.info(f"🎯 {key}: {tema[:20]}...")
            else:
                st.caption(f"🔒 {key}: {tema[:20]}...")
        
        st.divider()
        
        # --- BOTONES DE REINICIO ---
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
        # ---------------------------
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.usuario_activo = None
            st.rerun()

# ==================== LÓGICA PRINCIPAL DEL APP ====================

if st.session_state.usuario_activo:
    st.markdown("""
    <div class='metric-card'>
        <h1 style='color: #667eea; margin: 0;'>🎓 Nexus Pro Elite</h1>
        <p style='color: #333; margin: 5px 0 0 0;'>Sistema Profesional A1 → C1</p>
    </div>
    """, unsafe_allow_html=True)

    # --- FASE 1: EXPLICACIÓN (Tablas y Teoría) ---
    if st.session_state.fase == "explicacion":
        st.markdown(f"## 📖 {nivel_actual}: {config['tema']}")
        
        col1, col2 = st.columns(2)
        with col1: st.info(f"**Objetivo:** {config['objetivo']}")
        with col2: st.info(f"**Duración:** {config['duracion']}")
        
        # Renderizar explicación HTML (Tablas, etc.)
        st.markdown(config['explicacion'], unsafe_allow_html=True)
        
        if st.button("✅ ENTENDIDO - COMENZAR PRÁCTICA", use_container_width=True, type="primary"):
            st.session_state.fase = "practica"
            st.session_state.frase_actual = 0
            guardar_datos()
            st.rerun()

    # --- FASE 2: PRÁCTICA (Grabación) ---
    elif st.session_state.fase == "practica":
        
        # Freno de seguridad (Evita IndexError)
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

        # Caja Amarilla de Pronunciación
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

    # --- FASE 3: EXAMEN ---
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
             
             if st.button("➡️ Siguiente Nivel / Inicio", type="primary"):
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
