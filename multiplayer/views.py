from django.shortcuts import render
import json
from django.http import JsonResponse
from utils.ai import MODEL, usar_api

# Create your views here.
def init(request):
    #success, respuesta = generar_preguntas()
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
    return success, respuesta
