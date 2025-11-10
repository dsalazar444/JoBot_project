from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
from .models import Progreso, Nivel, Pregunta, Chat, Mensaje
from user.models import Usuario
from django.conf import settings


NUM_PREGUNTAS_POR_NIVEL = 6
# Configurar Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
# Se crea solo una vez al importar el archivo, y lo podemos usar en todo el codigo.
MODEL = genai.GenerativeModel('gemini-2.5-flash')

#  --------------------- funciones principales ----------------------------------------------

# Funcion que carga los niveles y los pasa a html, no lo hace desde la bd
"""
Función: Vista principal del modo juego que renderiza la página con los niveles disponibles
Parámetros: request -> objeto HttpRequest de Django
Retorna: HttpResponse -> respuesta renderizada con template modo_juego.html y lista de niveles
"""
def init(request):
    niveles_lista = get_niveles()
    return render(request, "modo_juego.html", {"niveles": niveles_lista})

"""
Función: Procesa las solicitudes POST para manejar mensajes del chat en modo juego
Parámetros: request -> objeto HttpRequest de Django con datos JSON del mensaje
Retorna: JsonResponse -> respuesta JSON con éxito/error y contenido de la respuesta de IA
"""
def procesar_request_bd(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            respuesta_ia = guardar_mensaje_bd(data)
            respuesta_ia_json = json.loads(respuesta_ia)
            # DEBUG: inspeccionar payload y respuesta IA antes de actualizar progreso
            print("DEBUG procesar_request_bd - data payload:", data)
            print("DEBUG procesar_request_bd - respuesta_ia_json:", respuesta_ia_json)

            if respuesta_ia_json["avanza"]:
                nivel_acabo = respuesta_ia_json["nivel_acabo"]
                usuario_obj = request.user
                print("DEBUG procesar_request_bd - va a actualizar progreso para usuario (raw):", usuario_obj, "type:", type(usuario_obj))
                actualizar_progreso(nivel_acabo, usuario_obj) #Actualizamos progreso en bd
            
            retorno = JsonResponse({"success": True, "contenido": respuesta_ia_json})
            # print("JSON string:", json.dumps(retorno, indent=2))
            return retorno
        except Exception as e:
            print("error en procesas_request_bd", str(e))
            return JsonResponse({"success": False, "contenido":str(e)})

     # Si no es POST, retornamos error
    return JsonResponse({"error": "Método no permitido"}, status=405)

"""
Función: Obtiene el historial de mensajes de un nivel específico para mostrar chats anteriores
Parámetros: request -> objeto HttpRequest de Django con datos JSON del nivel seleccionado
Retorna: JsonResponse -> respuesta JSON con éxito/error y historial de mensajes del nivel
"""
def obtener_chats_pasados_request(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        nivelSeleccionado = data.get("nivel")
        
        usuario_obj = request.user #Nos da un objato User
        mensajes_nivel = get_mensajes_nivel_con_usuario(usuario_obj, nivelSeleccionado)
        historial = generar_historial(mensajes_nivel)

        if (historial): #Si la lista tiene elementos
            return JsonResponse({
                "success": True,
                "historial": historial
            })

        return JsonResponse({
            "success": False,
            "historial": []
        })

#  --------------------- flujo de IA ----------------------------------------------
"""
Función: Construye el prompt contextualizado para enviar a la IA con información del usuario y nivel
Parámetros: usuario_obj -> objeto Usuario del usuario actual
           nivelSeleccionado -> int del nivel seleccionado por el usuario  
           respuesta_usuario -> string con la respuesta del usuario a evaluar
Retorna: tuple -> (bool éxito, string prompt) o (False, None) si hay error de validación
"""
def armar_prompt(usuario_obj, nivelSeleccionado, respuesta_usuario):
    
    progreso_usuario_obj = get_progreso_obj(usuario_obj)
    nivel_actual = progreso_usuario_obj.nivel_actual
    nivel_actual = int(str(nivel_actual).strip())
    num_pregunta_actual = progreso_usuario_obj.pregunta_actual
    nivelSeleccionado = int(str(nivelSeleccionado).strip())
    

    if (nivel_actual != nivelSeleccionado):
        print("entré a !=, nivel actual: ",nivel_actual, " != nivelSeleccionado: ",nivelSeleccionado)
        return (False, None)
    
    # if (num_pregunta_actual+1) > num_preguntas_por_nivel: #es porque ya respondió la ultima pregunta (la 6ta) y se acaba el nivel
    #     preg_siguiente=""
    print("no entré al !=")
    preg_actual = get_pregunta_nivel(nivel_actual, num_pregunta_actual).texto
    print("pregAct", preg_actual)
    chat_obj = get_or_create_chat_for_user(usuario_obj)
    #preg_sig = obtener_sig_pregunta(num_pregunta_actual, nivel_actual)
    #num_preg_siguiente = num_pregunta_actual+1
    #preg_siguiente = Pregunta.object.filter(nivel=nivel_actual,
    #num_pregunta=num_preg_siguiente).texto
    
    contexto = armar_contexto(chat_obj, nivel_actual, usuario_obj, preg_actual, respuesta_usuario, num_pregunta_actual)
    print("contexto: ",contexto)
    prompt = obtener_prompt_con_contexto(contexto) 
    print("prompt final: ", prompt)
    
    return (True, prompt)

"""
Función: Construye el diccionario de contexto necesario para la IA con información del nivel y usuario
Parámetros: chat_obj -> objeto Chat del usuario
           nivel_actual -> int del nivel actual del usuario
           usuario_obj -> objeto Usuario actual
           preg_actual -> string con la pregunta actual 
           respuesta_usuario -> string con la respuesta del usuario
           num_pregunta_actual -> int número de la pregunta actual
Retorna: dict -> diccionario con contexto completo para la IA
"""
def armar_contexto(chat_obj, nivel_actual, usuario_obj, preg_actual, respuesta_usuario, num_pregunta_actual):

    nivel_actual = str(nivel_actual)
    print("entre a armar contexto")
    print("resumen_nivel", chat_obj.resumen[nivel_actual])
    print("ultimo_mensaje_usuario", obtener_ult_respuesta_usuario(usuario_obj))
    print("tipo_entrevistador",get_nivel_obj(nivel_actual).tipo_entrevistador)
    print("pregunta_actual", preg_actual)
    print("sig_pregunta: ",obtener_sig_pregunta(num_pregunta_actual,nivel_actual))
    print("respuesta_usuario", respuesta_usuario)
    contexto = {
        "resumen_nivel": chat_obj.resumen[nivel_actual],
        "ultimo_mensaje_usuario": obtener_ult_respuesta_usuario(usuario_obj),
        "tipo_entrevistador":get_nivel_obj(nivel_actual).tipo_entrevistador,
        "siguiente_pregunta":obtener_sig_pregunta(num_pregunta_actual,nivel_actual),
        "pregunta_actual": preg_actual,
        "respuesta_usuario": respuesta_usuario
    }

    return contexto

"""
Función: Genera el prompt completo con instrucciones detalladas para la IA usando el contexto proporcionado
Parámetros: contexto -> dict con información del nivel, usuario, preguntas y respuestas
Retorna: string -> prompt formateado con instrucciones completas para la IA
"""
def obtener_prompt_con_contexto(contexto):
    prompt = f"""
    Eres un coach de habilidades blandas que interpreta el rol de un entrevistador específico. Siempre debes generar DOS respuestas separadas dentro de un JSON, siguiendo exactamente las reglas que se describen a continuación.

    CONTEXTO RECIBIDO:
    Se te enviará un diccionario llamado "contexto" que contiene:
    - "resumen_nivel": resumen breve del chat anterior (puede estar vacío), utilízalo para tener más contexto de la conversación.
    - "ultimo_mensaje_usuario": texto con la última respuesta del usuario.
    - "tipo_entrevistador": personalidad que debes interpretar (serio, crítico, amable, etc.).
    - "siguiente_pregunta": la próxima pregunta que corresponde.
    - "pregunta_actual": número de la pregunta.
    - "respuesta_usuario": respuesta a la pregunta actual, y es la que debes evaluar.

    TU TAREA:
    Con base en el contexto y la respuesta del usuario:

    1. Evalúa la respuesta del usuario con una puntuación del 1 al 5:
    - 1 a 2: respuesta insuficiente → NO avanza.
    - 3 a 5: respuesta aceptable → SÍ avanza.

    2. Genera dos respuestas separadas:
    A) "respuesta_entrevistador": mensaje que diría el entrevistador actuando según su personalidad.
    B) "feedback_instructor": mensaje analítico y constructivo con consejos de mejora.
        - Si la puntuación es menor a 3, explica qué estuvo mal.

    3. Si el usuario NO avanza, se mantiene la misma pregunta.
    4. Si el usuario SÍ avanza, se usa la siguiente pregunta del contexto.
    5. Si "siguiente_pregunta" es un string vacío, significa que el nivel acabó.
    6. Si el nivel acabó, genera un mensaje de despedida cálido, mencionando fortalezas del usuario con base en el resumen.
    7. NUNCA inventes preguntas nuevas ni cambies el orden.
    8. Si deseas resaltar una parte del texto en negrilla dentro de tu
       respuesta, coloca ese fragmento entre dos asteriscos al inicio y dos al
       final. Ejemplo **Texto en negrilla**
    

    FORMATO DE RESPUESTA OBLIGATORIO:
    Responde SIEMPRE estrictamente como te indico, sin texto adicional. Usa esta estructura:

    {{
    "respuesta_entrevistador": "Texto que dirás al usuario según la personalidad",
    "feedback_instructor": "Consejos, evaluación y explicación del puntaje",
    "puntaje": (entero del 1 al 5),
    "avanza": (true o false),
    "nivel_acabo": (true o false),
    "siguiente_pregunta": "Texto de la próxima pregunta o la misma si no avanza",
    "mensaje_despedida": "Texto solo si el nivel terminó; en caso contrario, string vacío"
    }}

    PROHIBICIONES:
    - No escribas nada fuera del JSON.
    - No inventes preguntas, niveles ni entrevistadores.
    - No cambies la estructura ni los nombres de las claves.
    - No agregues comentarios ni explicaciones externas.
    - Responde SIEMPRE en JSON plano, SIN usar ```json ni ``` ni ningún delimitador de bloque. No agregues comentarios ni texto externo.


    A continuación se te enviará el JSON llamado "contexto". Úsalo estrictamente para generar tu respuesta.

    Este es el json CONTEXTO {contexto}
    """ 
    return prompt

"""
Función: Obtiene respuesta de la IA generando resumen, armando prompt y consultando API
Parámetros: usuario_obj -> objeto Usuario del usuario actual
           nivel -> int del nivel del juego
           contenido -> string con el contenido/respuesta del usuario
Retorna: string -> respuesta JSON de la IA o mensaje de error
"""
def obtener_respuesta_de_ia(usuario_obj, nivel,contenido):
    # Generamos resumen usando el objeto usuario (no el request)
    generar_resumen(usuario_obj, nivel, MODEL)
    success, prompt = armar_prompt(usuario_obj, nivel, contenido)

    if not success: 
        print("No se puedo armar prompt")
        return "No se puedo armar prompt"

    success, respuesta = usar_api(prompt, MODEL)

    if not success: 
        print("No se  pudo obtener respuesta")
        return "No se pudo obtener respuesta"
    if success: return respuesta

#  --------------- funciones para procesar y manipular datos --------------------------------

"""
Función: Guarda mensaje del usuario en BD, obtiene respuesta de IA y guarda respuesta en BD
Parámetros: data -> dict con datos del mensaje (usuario, texto, remitente, nivel_sel)
Retorna: string -> respuesta JSON de la IA 
"""
def guardar_mensaje_bd(data):
    username = data.get('usuario')  # viene como string, ej: "da@gmail.com"

    if not username:
        raise ValueError("El usuario no fue proporcionado")
    
    usuario_obj = get_user_obj(username)
    print("DEBUG guardar_mensaje_bd - username:", username, "usuario_obj:", usuario_obj, "type:", type(usuario_obj))
    nivel_sel = data.get('nivel_sel')

    if not usuario_obj:
        raise ValueError("Usuario no encontrado")

    contenido=data.get('texto')
    chat_obj= get_or_create_chat_for_user(usuario_obj)
    #Guardamos mensaje de user
    Mensaje.objects.create(chat=chat_obj, nivel=nivel_sel, remitente=data.get('remitente'), contenido=contenido)

    #Enviamos y obtenemos respuesta de modelo
    respuesta = obtener_respuesta_de_ia(usuario_obj, nivel_sel, contenido)
    print("respuesta:", respuesta, "type: ",type(respuesta))

    #Guardamos mensaje json de ia
    Mensaje.objects.create(chat=chat_obj, nivel=nivel_sel, remitente="robot", contenido=respuesta)

    return respuesta

"""
Función: Actualiza el progreso del usuario en BD (nivel y pregunta actual)
Parámetros: nivel_acabo -> bool indica si se completó el nivel
           usuario_obj -> objeto Usuario a actualizar
Retorna: bool -> True si se guardó correctamente, False si hubo error
"""
def actualizar_progreso(nivel_acabo, usuario_obj):
    # DEBUG: inspección inicial
    print("DEBUG actualizar_progreso - usuario_obj recibido:", usuario_obj, "type:", type(usuario_obj))
    progreso_obj = get_progreso_obj(usuario_obj)
    print("DEBUG actualizar_progreso - progreso_obj obtenido:", progreso_obj)
    if not progreso_obj:
        print("DEBUG actualizar_progreso - no se encontró Progreso para usuario:", usuario_obj)
        return False

    if (nivel_acabo):
        progreso_obj.nivel_actual += 1 #pasó de nivel
        #Deshabilitar input section 
        progreso_obj.pregunta_actual = 1
    else:
        progreso_obj.pregunta_actual += 1 #Actualizamos valor de preg_actual a siguiente en bd

    progreso_obj.save()
    print("DEBUG actualizar_progreso - guardado. nivel_actual:", progreso_obj.nivel_actual, "pregunta_actual:", progreso_obj.pregunta_actual)
    return True

"""
Función: Genera resumen de la conversación del nivel usando IA y lo guarda en BD
Parámetros: usuario_obj -> objeto Usuario del cual generar resumen
           nivel -> int del nivel para generar resumen
           modelo -> objeto del modelo de IA para generar resumen
Retorna: None -> guarda directamente en BD o imprime error
"""
def generar_resumen(usuario_obj, nivel, modelo):
    #Obtenemos chat del usuario, o lo creamos si no existe
    chat_obj = get_or_create_chat_for_user(usuario_obj)
    #mensajes_nivel = Mensaje.objects.filter(chat=chat_obj, nivel=
    #nivel).order_by('timestamp') 
    mensajes_nivel = get_mensajes_nivel(chat_obj, nivel)
    historial = generar_historial(mensajes_nivel)

    print("El historial essss: ", historial)

    prompt = f"""Quiero que generes un resumen únicamente basado en la conversación proporcionada a continuación. 
    IMPORTANTE:
    - No inventes información
    - No rellenes huecos
    - No agregues interpretaciones
    - Si un dato no está explícitamente en el texto, NO lo incluyas

    Tu tarea es:
    1. Extraer solo lo que realmente se mencionó
    2. Resumir de forma breve y objetiva
    3. No añadir conclusiones ni contenido nuevo

    Aquí está la conversación: {historial}

    Genera el resumen ahora, sin agregar nada que no esté en el contenido.
    """
    success, respuesta = usar_api(prompt, modelo)

    if (success):
        print("resumen: ", respuesta)
        guardar_resumen(chat_obj, nivel, respuesta)
        
    else:
        #Si success es false, respuesta contiene un error
        print(respuesta)

"""
Función: Guarda el resumen generado en el diccionario de resúmenes del chat en BD
Parámetros: chat_obj -> objeto Chat donde guardar el resumen
           nivel -> int del nivel para el cual se generó el resumen
           resumen -> string con el resumen generado por la IA
Retorna: None -> guarda directamente en BD
"""
def guardar_resumen(chat_obj, nivel, resumen):
    #Obtenemos el diccionario de resumenes
    nivel=str(nivel)
    resumen_dict = chat_obj.resumen

    #Actualizamos valor en clave "nivel" -> actualizamos diccionario general
    resumen_dict[nivel] = resumen

    #Guardamos en el atributo, el diccionario actualizado
    chat_obj.resumen = resumen_dict
    chat_obj.save()

"""
Función: Crea lista con los mensajes en orden cronológico para enviar a la IA
Parámetros: mensajes_nivel -> QuerySet con mensajes del nivel ordenados por timestamp
Retorna: list -> lista de diccionarios con remitente, contenido y timestamp de cada mensaje
"""
#Crea lista con los mensajes en orden.
def generar_historial(mensajes_nivel):
    historial=[]

    for msg in mensajes_nivel:
        historial.append({
            "remitente": msg.remitente,
            "contenido": msg.contenido,
            "timestamp": msg.timestamp.isoformat()
        })
    
    return historial

#  --------------------- Funciones auxiliares ----------------------------------------------
"""
Función: Obtiene el texto de la siguiente pregunta del nivel o string vacío si terminó
Parámetros: num_pregunta_actual -> int número de la pregunta actual
           nivel_actual -> int del nivel actual
Retorna: string -> texto de la siguiente pregunta o string vacío si no hay más preguntas
"""
def obtener_sig_pregunta(num_pregunta_actual,nivel_actual):
    num_pregunta_sig = num_pregunta_actual + 1

    #esta en ultima pregunta y ya no hay más
    if (num_pregunta_sig > 6):
        num_pregunta_sig = 0 #Para indicar a modelo que ya no hay más
    
    if (num_pregunta_sig == 0):
        pregunta_siguiente="" #Poque ya finalizó
    else:
        pregunta_siguiente= get_pregunta_nivel(nivel_actual, num_pregunta_sig).texto

    return pregunta_siguiente

"""
Función: Obtiene el último mensaje enviado por el usuario en el chat
Parámetros: usuario_obj -> objeto Usuario del cual obtener el último mensaje
Retorna: string -> contenido del último mensaje del usuario o string vacío si no hay mensajes
"""
def obtener_ult_respuesta_usuario(usuario_obj):
    #Obtenemos chat del usuario
    chat = get_or_create_chat_for_user(usuario_obj)
    mensaje = Mensaje.objects.filter(chat=chat.id, remitente='usuario').order_by('-timestamp').first().contenido
    print("ultimo mensaje de usuario: ", mensaje)
    if mensaje:
       return mensaje
    else: 
        return ""

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

#  --------------------- getters ----------------------------------------------
 
 #Obtiene registro en Progreso de un usuario especifico
def get_progreso_obj(usuario_obj):
    return Progreso.objects.filter(usuario=usuario_obj).first()

def get_mensajes_nivel(chat_obj, nivel):
    return Mensaje.objects.filter(chat=chat_obj, nivel= nivel).order_by('timestamp') 

#Obtiene los mensajes, usando un registro Usuario, en lugar de una Chat
def get_mensajes_nivel_con_usuario(usuario_obj, nivel):
    chat_obj = get_or_create_chat_for_user(usuario_obj)
    return Mensaje.objects.filter(chat=chat_obj, nivel= nivel).order_by('timestamp') 
 #Obtiene registro en Nivel de un usuario especifico

def get_nivel_obj(nivel_num):
    return Nivel.objects.get(numero=nivel_num)

# Obtiene registro en Chat de un usuario especifico

def get_user_obj(username):
    return Usuario.objects.filter(username=username).first()

# Obtiene registro en Nivel con un nivel y numero de pregunta especifico
def get_pregunta_nivel(nivel_actual, num_pregunta_actual):
    return Pregunta.objects.filter(nivel=nivel_actual, num_pregunta=num_pregunta_actual).first()

#Obtiene registro en Pregunta de una pegrunta especifica de un nivel especifico, y le saca el atributo texto
def get_pregunta_text(nivel_num, num_pregunta):
    #nivel__numero le decimos que coja el objeto Nivel que tiene como FK, y a este le obtenga el atributo numero
    preg = Pregunta.objects.filter(nivel__numero=nivel_num, num_pregunta=num_pregunta).first()
    return preg.texto if preg else None

#Obtiene o crea (aunque ya tenemos un trigger) registro en Chat asignado a un usuario
def get_or_create_chat_for_user(usuario_obj):
    chat = Chat.objects.filter(usuario=usuario_obj).first()
    if not chat:
        chat = Chat.objects.create(usuario=usuario_obj, resumen={})
    if chat.resumen is None:
        chat.resumen = {}
        print("entre a chat none, chat.resumen ahora", chat.resumen)
    return chat

#Obtiene niveles guardados en bd
# Retorna lista de numeros de los niveles, ordenandolos asc
def get_niveles():
    niveles = list(Nivel.objects.values_list('numero', flat=True).order_by('numero'))
    return niveles

def get_nivel_actual(request):
    if request.method == 'GET': 
        usuario_obj = request.user #Nos da un objeto User
        progreso_obj = get_progreso_obj(usuario_obj)
        print('nivel_act', progreso_obj.nivel_actual)
        
        return JsonResponse({
            'success': True,
            'nivel_act': progreso_obj.nivel_actual, 
        })
    
    # Si no es GET, retornar error
    return JsonResponse({"error": "Método no permitido"}, status=405)
