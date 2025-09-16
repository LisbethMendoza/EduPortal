import google.generativeai as genai
from django.conf import settings
from chats.models import Documento

genai.configure(api_key=settings.GEMINI_API_KEY)

PREGUNTAS_GENERALES = {
    "hola": "¡Hola! 😊 ¿En qué puedo ayudarte hoy?",
    "como estás": "¡Estoy genial! Gracias por preguntar 😄",
    "buenos días": "¡Buenos días! Espero que tengas un excelente día ☀️",
    "buenas tardes": "¡Buenas tardes! ¿Cómo te va?",
    "gracias": "¡De nada! 😁",
    "adiós": "¡Hasta luego! Cuídate mucho 👋",
    "que puedes hacer": "Puedo ayudarte a responder preguntas sobre la inscripcion y reinscripcion. ¿En qué te gustaría que te ayude?",
    "que es hace portal": "Este portal está diseñado para facilitar la gestión de inscripciones y reinscripciones de estudiantes, así como para mantenerlos informados sobre avisos importantes.",
    "que puede hacer este portal": "Este portal está diseñado para facilitar la gestión de inscripciones y reinscripciones de estudiantes, así como para mantenerlos informados sobre avisos importantes.",
    "como me inscribo": "Para inscribirte, solo debes dirígete a <a href='/inscripcion/'>Inscripción</a>",
    "como me reinscribo": "Para reinscribirte, solo debes dirígete a <a href='/reinscripcion/'>Reinscripción</a>",
    "como puedo inscribirme": "Para inscribirte, solo debes dirígete a <a href='/inscripcion/'>Inscripción</a>",
    "como puedo reinscribirme": "Para reinscribirte, solo debes dirígete a <a href='/reinscripcion/'>Reinscripción</a>",
    
}

def obtener_documentos_activos():
    return [doc.contenido for doc in Documento.objects.filter(estado="Activo")]

def responder_con_gemini(pregunta):
    pregunta_lower = pregunta.lower()

    # Revisamos primero si es una frase general
    for clave, respuesta_general in PREGUNTAS_GENERALES.items():
        if clave in pregunta_lower:
            return respuesta_general

    # Si no es general, usamos Gemini con documentos
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
