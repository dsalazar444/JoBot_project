from django.shortcuts import render
import json
from django.http import JsonResponse
from utils.ai import MODEL, usar_api

success = None
respuesta = None
# Create your views here.
def init(request):
    global success, respuesta
    generar_preguntas()
    """
    success = True
    respuesta = {
"preguntas": [
"1. Cuéntame sobre una ocasión en la que tuviste que comunicar una idea compleja a alguien con poca experiencia en el tema. ¿Cómo te aseguraste de que te entendiera?",
"2. Describe una situación en la que tuviste que trabajar con un compañero difícil. ¿Qué hiciste para mantener una buena colaboración?",
"3. Háblame de una ocasión en la que tuviste que adaptarte rápidamente a un cambio inesperado en el trabajo o en un proyecto. ¿Cómo lo manejaste?",
"4. Cuéntame sobre un conflicto en equipo que hayas tenido que resolver. ¿Qué pasos seguiste y cuál fue el resultado?",
"5. Menciona un ejemplo en el que hayas tenido que tomar una decisión bajo presión. ¿Cómo te aseguraste de que fuera la mejor posible?",
"6. Describe una situación en la que tuviste que liderar a un grupo hacia un objetivo difícil. ¿Cómo motivaste a los demás y qué aprendiste de la experiencia?"
],
"respuestas": [
"Durante una práctica universitaria, debía explicar un modelo estadístico a compañeros de otras carreras. Dividí la explicación en pasos sencillos y usé ejemplos cotidianos para relacionar cada concepto. Pedí retroalimentación constante para confirmar comprensión y ajusté mi lenguaje según sus dudas. Finalmente, todos lograron aplicar el modelo correctamente, lo cual confirmó la efectividad de mi comunicación.",
"En un proyecto académico, un compañero no cumplía plazos y generaba tensión en el grupo. En lugar de confrontarlo, lo abordé en privado para entender su situación y descubrí que tenía dificultades personales. Reasigné tareas según sus fortalezas y establecimos recordatorios compartidos. Logramos terminar el proyecto a tiempo y el ambiente del equipo mejoró notablemente.",
"En mi pasantía, el cliente cambió los requerimientos del sistema a mitad del desarrollo. Analicé rápidamente qué módulos debían modificarse y propuse un cronograma ajustado. Organicé una reunión para reasignar tareas y mantener la moral del equipo. Gracias a esa reacción, entregamos el producto dentro del nuevo plazo y con buena retroalimentación del cliente.",
"En un trabajo grupal, dos integrantes tenían desacuerdos constantes sobre la metodología. Organicé una reunión neutral donde cada uno expuso su punto de vista sin interrupciones. Luego buscamos una solución intermedia que aprovechara las fortalezas de ambos enfoques. El resultado fue un trabajo más sólido y una mejor relación entre los miembros.",
"En un hackathon, el servidor falló minutos antes de la presentación final. Mantuve la calma, prioricé las tareas críticas y coordiné al equipo para usar una copia local del proyecto. Mientras uno corregía errores, otro ajustaba la demo. Conseguimos presentar a tiempo y obtuvimos una mención especial por resiliencia y trabajo bajo presión.",
"En un proyecto de investigación, fui líder de un equipo multidisciplinario. Al notar que algunos se desmotivaban por la carga de trabajo, organicé reuniones breves de seguimiento, celebré los avances y ajusté metas para mantener el equilibrio. La comunicación abierta y la empatía ayudaron a que todos se sintieran valorados, logrando un resultado sobresaliente y una experiencia de liderazgo muy enriquecedora."
]
}
"""
    return render(request, "multijugador.html")

"""Función que genera las 6 preguntas que aparecerán en la partida, esto
llamando al modelo para que las genere
Retorna: tupla con -> success: Booleano que indica si el contacto con el modelo fue posible
                      respuesta: json con estructura especifica, que contiene respuesta de ia"""
def generar_preguntas():
    prompt = """Objetivo:
    Generar exactamente 6 preguntas sobre habilidades blandas comúnmente evaluadas en entrevistas laborales.

    Instrucciones detalladas:

    1. Crea 6 preguntas únicas, cada una relacionada con una habilidad blanda distinta (por ejemplo: comunicación, liderazgo, adaptabilidad, resolución de conflictos, pensamiento crítico, trabajo en equipo, etc.).

    2. Las preguntas deben estar ordenadas por dificultad, desde media (pregunta 1) hasta alta (pregunta 6).

    3. Para cada pregunta, genera una respuesta ideal que obtendría una puntuación 10/10, demostrando reflexión, dominio y ejemplos concretos.

    4. Devuelve el resultado en formato JSON válido, siguiendo exactamente esta estructura:

    {
    "preguntas": [
    "Pregunta 1...",
    "Pregunta 2...",
    "Pregunta 3...",
    "Pregunta 4...",
    "Pregunta 5...",
    "Pregunta 6..."
    ],
    "respuestas": [
    "Respuesta ideal para la pregunta 1...",
    "Respuesta ideal para la pregunta 2...",
    "Respuesta ideal para la pregunta 3...",
    "Respuesta ideal para la pregunta 4...",
    "Respuesta ideal para la pregunta 5...",
    "Respuesta ideal para la pregunta 6..."
    ]
    }

    5. Asegúrate de que los índices coincidan entre ambas listas: la posición 0 en "preguntas" corresponde a la posición 0 en "respuestas", y así sucesivamente.

    Prohibiciones estrictas:

    - No agregues explicaciones, descripciones ni texto fuera del JSON.

    - No uses bloques de código, delimitadores ni etiquetas como json, ni ningún formato adicional.

    - No incluyas comentarios, notas o aclaraciones.

    - No inventes términos, fuentes o datos no verificables.

    - No alteres la estructura del JSON ni agregues claves distintas a "preguntas" y "respuestas".

    - Responde SIEMPRE en JSON plano, cumpliendo exactamente la estructura solicitada, SIN usar ```json ni ``` ni ningún delimitador de bloque. No agregues comentarios ni texto externo."""
    
    success, respuesta = usar_api(prompt, MODEL)
    print("succes: ",success)
    print("respuest: ", respuesta)
    # return success, respuesta

#Breakpoint para obtener preguntas desde JS
def enviar_preguntas(request):
    if request.method == 'GET':      
        return JsonResponse({
            'success': success,
            'respuesta': respuesta, 
        })
    
    # Si no es GET, retornar error
    return JsonResponse({"error": "Método no permitido"}, status=405)
    
#Breakpoint para enviar respuesta a modelo, y devolver lo que este nos retorne
def procesar_respuesta(request):
    
    if request.method == 'POST':

        data = json.loads(request.body)
        pregunta = data.get("pregunta")
        respuesta_ia = data.get("respuesa_perf")
        respuesta_user = data.get("mensaje")

        prompt = armar_prompt_evaluacion(pregunta, respuesta_ia, respuesta_user)
        success_evaluacion, respuesta_evaluacion = usar_api(prompt, MODEL)

        print("success evaluacion", success_evaluacion)
        print("respuesta evaluacion", respuesta_evaluacion)

        return JsonResponse({
            'success': success_evaluacion,
            'respuesta': respuesta_evaluacion, 
        })
    # Si no es GET, retornar error
    return JsonResponse({"error": "Método no permitido"}, status=405)
    
def armar_prompt_evaluacion(pregunta, respuesta_perf, respuesta_user):
    contexto = {
        'pregunta': pregunta,
        'respuesta_perfecta': respuesta_perf,
        'respuesta_user': respuesta_user,
    }
    prompt = f"""
    Objetivo:
    Evaluar una respuesta dada por el usuario comparándola con una respuesta perfecta, ambas proporcionadas dentro de un diccionario llamado contexto.

    Estructura del diccionario de entrada llamado 'contexto' (que yo te proporcionaré):
    {{
    "pregunta": "...",
    "respuesta_perfecta": "...",
    "respuesta_user": "..."
    }}

    Instrucciones detalladas:

    1. Analiza la pregunta, la respuesta perfecta y la respuesta del usuario contenidas en el diccionario contexto.

    2. Evalúa la calidad de la respuesta del usuario comparándola con la respuesta perfecta.

    3. Retorna un JSON con las siguientes claves obligatorias:

    {{
    "puntuacion": 0,
    "a_mejorar": ["aspecto 1...", "aspecto 2..."],
    "aciertos": ["aspecto 1...", "aspecto 2..."]
    }}

    - La clave "puntuacion" debe ser un número entero del 1 al 10 que refleje qué tan completa, coherente y sólida es la respuesta del usuario respecto a la respuesta perfecta.

    - La lista "a_mejorar" debe incluir puntos específicos, concretos y accionables sobre lo que le faltó al usuario para alcanzar la respuesta perfecta.

    - La lista "aciertos" debe destacar las partes bien logradas, fortalezas o aspectos positivos de la respuesta del usuario.

    - No incluyas ni repitas el contenido original de las respuestas en el resultado; solo genera la evaluación según el análisis.

    Prohibiciones estrictas:

    - No agregues explicaciones, texto fuera del JSON, ni comentarios.

    - No uses bloques de código, delimitadores ni etiquetas como json, ni ningún formato adicional.

    - No inventes términos, fuentes o datos no verificables.

    - No alteres la estructura del JSON ni agregues claves distintas a "puntuacion", "a_mejorar" y "aciertos".

    - Responde SIEMPRE en JSON plano, cumpliendo exactamente la estructura solicitada, SIN usar ```json ni ``` ni ningún delimitador de bloque. No agregues comentarios ni texto externo.

    Este es el json CONTEXTO {contexto}
    """

    return prompt