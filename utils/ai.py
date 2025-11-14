import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
MODEL = genai.GenerativeModel('gemini-2.5-flash')

"""
Función: Realiza llamada a la API de Gemini para obtener respuesta de la IA
Parámetros: prompt -> string con el prompt completo para enviar a la IA
           modelo -> objeto del modelo GenerativeModel de Gemini
Retorna: tuple -> (bool éxito, string respuesta) o (False, string error)
"""
def usar_api(prompt, modelo):
    try:
        respuesta =  modelo.generate_content(prompt)
        ai_response = respuesta.text.strip() #Limpia la cadena
        return (True, ai_response)
    except Exception as e:
        return (False, str(e))
