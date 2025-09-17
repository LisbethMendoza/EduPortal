import google.generativeai as genai
from django.conf import settings
from chats.models import Documento
from unidecode import unidecode
import difflib

genai.configure(api_key=settings.GEMINI_API_KEY)

PREGUNTAS_GENERALES = {
    "hola": "¡Hola! 😊 ¿En qué puedo ayudarte hoy?",
    "como estas": "¡Estoy genial! Gracias por preguntar 😄",
    "buenos dias": "¡Buenos días! Espero que tengas un excelente día ☀️",
    "buenas tardes": "¡Buenas tardes! ¿Cómo te va?",
    "gracias": "¡De nada! 😁",
    "adios": "¡Hasta luego! Cuídate mucho 👋",
    "que puedes hacer": "Puedo ayudarte a responder preguntas sobre la inscripción y reinscripción. ¿En qué te gustaría que te ayude?",
    "que hace el portal": "Este portal está diseñado para facilitar la gestión de inscripciones y reinscripciones de estudiantes, así como para mantenerlos informados sobre avisos importantes.",
    "que puede hacer este portal": "Este portal está diseñado para facilitar la gestión de inscripciones y reinscripciones de estudiantes, así como para mantenerlos informados sobre avisos importantes.",
    "como me inscribo": "Para inscribirte, solo debes dirigirte a <a href='/inscripcion/'>Inscripción</a>",
    "como me reinscribo": "Para reinscribirte, solo debes dirigirte a <a href='/reinscripcion/'>Reinscripción</a>",
    "como puedo inscribirme": "Para inscribirte, solo debes dirigirte a <a href='/inscripcion/'>Inscripción</a>",
    "como puedo reinscribirme": "Para reinscribirte, solo debes dirigirte a <a href='/reinscripcion/'>Reinscripción</a>",
    "como puedo inscribir a mi hijo": "Para inscribir a tu hijo, solo debes dirigirte a <a href='/inscripcion/'>Inscripción</a>",
    "como puedo reinscribir a mi hijo": "Para reinscribir a tu hijo, solo debes dirigirte a <a href='/reinscripcion/'>Reinscripción</a>",
    "cual es el horario de atencion": "Nuestro horario de atención es de lunes a viernes, de 8:00 a.m. a 4:00 p.m. 🕔",
    "donde estan ubicados": "Estamos ubicados en la dirección: [aquí colocas la dirección]. 📍",
    "numero de contacto": "Puedes comunicarte con nosotros al teléfono: 000-000-0000. ☎️",
}

def obtener_documentos_activos():
    return [doc.contenido for doc in Documento.objects.filter(estado="Activo")]

def normalizar_texto(texto):
    return unidecode(texto.lower().strip())

def responder_con_gemini(pregunta):
    pregunta_normalizada = normalizar_texto(pregunta)

    # Intentar coincidencia exacta o parcial
    for clave, respuesta_general in PREGUNTAS_GENERALES.items():
        if clave in pregunta_normalizada:
            return respuesta_general

    # Buscar coincidencia aproximada (ej: "holaaa" ≈ "hola")
    clave_cercana = difflib.get_close_matches(
        pregunta_normalizada,
        PREGUNTAS_GENERALES.keys(),
        n=1,
        cutoff=0.75
    )
    if clave_cercana:
        return PREGUNTAS_GENERALES[clave_cercana[0]]

    documentos = obtener_documentos_activos()
    contexto = "\n\n".join(documentos)

    prompt = f"""
    Responde la siguiente pregunta SOLO con base en este contexto.
    Si no hay información suficiente, responde:
    "Lo siento, no tengo esa información. Comuníquese al 000-000-0000."

    Contexto:
    {contexto}

    Pregunta:
    {pregunta}
    """

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    return response.text
