from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import google.generativeai as genai
<<<<<<< HEAD
from .models import InterviewSession, Message, UserStreak
from django.conf import settings
=======
from .models import InterviewSession, Message
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
>>>>>>> origin/main

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

<<<<<<< HEAD
def get_gemini_response(messages_history, session):
    """Generate response using Google Gemini with session parameters"""
=======

def get_gemini_response(messages_history, interview_type):
    """Generate response using Google Gemini"""
>>>>>>> origin/main

    # Create the model
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Build conversation context
    conversation_text = ""
    for msg in messages_history[-10:]:  # Last 10 messages for context
<<<<<<< HEAD
        sender = "Candidato" if msg.sender == 'user' else "JoBot"
        conversation_text += f"{sender}: {msg.content}\n"

    # Get session parameters
    interview_type = session.interview_type if hasattr(session, 'interview_type') else session
    duration = getattr(session, 'duration', 'standard')
    difficulty = getattr(session, 'difficulty', 'intermediate')
    focus_area = getattr(session, 'focus_area', 'communication')
    position_level = getattr(session, 'position_level', '')

    # Duration guidelines
    duration_info = {
        'quick': 'Sesión rápida de 10 minutos - haz 3-4 preguntas clave y concisas',
        'standard': 'Sesión estándar de 20 minutos - haz 5-7 preguntas bien estructuradas',
        'extended': 'Sesión extendida de 30 minutos - haz 8-10 preguntas detalladas con seguimiento',
        'unlimited': 'Sesión sin límite - adapta el ritmo según las respuestas del candidato'
    }

    # Difficulty guidelines
    difficulty_info = {
        'beginner': 'Nivel principiante - preguntas básicas, proporciona orientación y apoyo',
        'intermediate': 'Nivel intermedio - preguntas moderadas con ejemplos prácticos',
        'advanced': 'Nivel avanzado - preguntas complejas y escenarios desafiantes'
    }

    # Focus area guidelines
    focus_info = {
        'communication': 'Enfócate en habilidades de comunicación, presentación y expresión',
        'problem_solving': 'Enfócate en resolución de problemas y pensamiento analítico',
        'teamwork': 'Enfócate en colaboración, trabajo en equipo y dinámicas grupales',
        'adaptability': 'Enfócate en flexibilidad, adaptación al cambio y resiliencia',
        'time_management': 'Enfócate en organización, priorización y gestión del tiempo',
        'conflict_resolution': 'Enfócate en manejo de conflictos y negociación'
    }

    # System prompt based on interview type
    prompts = {
        'technical': f"""Eres JoBot, un entrenador profesional de entrevistas especializando en evaluaciones técnicas.
        Ayudas a desarrollar habilidades para entrevistas técnicas con preguntas sobre tecnología, algoritmos y mejores prácticas.
        
        PARÁMETROS DE LA SESIÓN:
        - {duration_info.get(duration, '')}
        - {difficulty_info.get(difficulty, '')}
        - {focus_info.get(focus_area, '')}
        - Posición objetivo: {position_level or 'No especificada'}
        
        Proporciona feedback constructivo y mantén un tono profesional pero motivador.""",

        'behavioral': f"""Eres JoBot, un entrenador profesional especializado en entrevistas conductuales.
        Ayudas a desarrollar habilidades blandas usando la metodología STAR (Situación, Tarea, Acción, Resultado).
        
        PARÁMETROS DE LA SESIÓN:
        - {duration_info.get(duration, '')}
        - {difficulty_info.get(difficulty, '')}
        - {focus_info.get(focus_area, '')}
        - Posición objetivo: {position_level or 'No especificada'}
        
        Guía al candidato para estructurar mejor sus respuestas y desarrollar ejemplos convincentes.""",

        'leadership': f"""Eres JoBot, un entrenador especializado en entrevistas de liderazgo.
        Enfócate en habilidades de liderazgo, toma de decisiones, gestión de equipos y visión estratégica.
        
        PARÁMETROS DE LA SESIÓN:
        - {duration_info.get(duration, '')}
        - {difficulty_info.get(difficulty, '')}
        - {focus_info.get(focus_area, '')}
        - Posición objetivo: {position_level or 'No especificada'}
        
        Evalúa capacidades de liderazgo y proporciona feedback para mejorar la presencia ejecutiva.""",

        'sales': f"""Eres JoBot, un entrenador especializado en entrevistas de ventas.
        Enfócate en habilidades de persuasión, manejo de objeciones, construcción de relaciones y orientación a resultados.
        
        PARÁMETROS DE LA SESIÓN:
        - {duration_info.get(duration, '')}
        - {difficulty_info.get(difficulty, '')}
        - {focus_info.get(focus_area, '')}
        - Posición objetivo: {position_level or 'No especificada'}
        
        Ayuda a desarrollar técnicas de venta y comunicación persuasiva.""",

        'customer_service': f"""Eres JoBot, un entrenador especializado en entrevistas de atención al cliente.
        Enfócate en empatía, resolución de problemas, paciencia y habilidades de comunicación.
        
        PARÁMETROS DE LA SESIÓN:
        - {duration_info.get(duration, '')}
        - {difficulty_info.get(difficulty, '')}
        - {focus_info.get(focus_area, '')}
        - Posición objetivo: {position_level or 'No especificada'}
        
        Desarrolla habilidades para manejar clientes difíciles y brindar excelente servicio.""",

        'general': f"""Eres JoBot, un entrenador profesional de entrevistas generales.
        Ayudas a desarrollar habilidades integrales para entrevistas laborales.
        
        PARÁMETROS DE LA SESIÓN:
        - {duration_info.get(duration, '')}
        - {difficulty_info.get(difficulty, '')}
        - {focus_info.get(focus_area, '')}
        - Posición objetivo: {position_level or 'No especificada'}
        
        Mantén una conversación natural y profesional, adaptando tu enfoque según las necesidades del candidato."""
=======
        sender = "Usuario" if msg.sender == 'user' else "Entrevistador"
        conversation_text += f"{sender}: {msg.content}\n"

    # System prompt based on interview type
    prompts = {
        'technical': """Eres un entrevistador técnico profesional. Realiza preguntas técnicas sobre desarrollo de software,
        algoritmos, estructuras de datos, y mejores prácticas. Evalúa las respuestas del candidato y proporciona
        feedback constructivo. Mantén un tono profesional pero amigable.""",

        'behavioral': """Eres un entrevistador conductual profesional. Enfócate en preguntas sobre situaciones laborales
        pasadas, resolución de problemas, trabajo en equipo, y habilidades blandas. Usa la técnica STAR
        (Situación, Tarea, Acción, Resultado) para evaluar respuestas.""",

        'general': """Eres un entrevistador general para posiciones profesionales. Realiza preguntas sobre experiencia
        laboral, motivaciones, fortalezas y áreas de mejora. Mantén una conversación natural y profesional.""",

        'custom': """Eres un entrevistador versátil. Adapta tus preguntas según el flujo de la conversación.
        Mantén el foco en aspectos relevantes para el rol profesional."""
>>>>>>> origin/main
    }

    system_prompt = prompts.get(interview_type, prompts['general'])

    # Full prompt
    if not conversation_text.strip():
        # First interaction
        full_prompt = f"""{system_prompt}

<<<<<<< HEAD
Esta es la primera interacción. Saluda de forma breve y profesional, luego haz una pregunta de apertura para conocer al candidato.

IMPORTANTE: No uses asteriscos ni markdown. Escribe en texto plano con buena estructura.

Al final agrega: PUNTOS:0"""
=======
Esta es la primera interacción con el candidato. Comienza con un saludo amigable y una pregunta de apertura
para conocer mejor al candidato y su experiencia profesional."""
>>>>>>> origin/main
    else:
        # Continuing conversation
        full_prompt = f"""{system_prompt}

<<<<<<< HEAD
Historial:
{conversation_text}

ANALIZA LA ÚLTIMA RESPUESTA DEL CANDIDATO Y RESPONDE CON ESTA ESTRUCTURA:

1. Feedback específico (1-2 líneas): Comenta aspectos concretos de SU respuesta

2. Nueva pregunta: Haz UNA pregunta clara relacionada con el tema

3. Evaluación detallada:
---EVALUACION---
Claridad: X/5 (0=incomprensible, 1=muy confuso, 2=poco claro, 3=aceptable, 4=claro, 5=muy claro)
Contenido: X/5 (0=sin contenido, 1=muy pobre, 2=insuficiente, 3=adecuado, 4=bueno, 5=excelente)
Profesionalismo: X/5 (0=inapropiado, 1=muy informal, 2=poco profesional, 3=aceptable, 4=profesional, 5=muy profesional)

CRITERIOS DE EVALUACIÓN:
- Claridad: ¿La respuesta es fácil de entender? ¿Está bien estructurada?
- Contenido: ¿Responde la pregunta? ¿Tiene ejemplos concretos? ¿Es relevante?
- Profesionalismo: ¿Usa lenguaje apropiado? ¿Muestra preparación?

REGLAS IMPORTANTES:
- NO uses asteriscos, guiones ni markdown
- Evalúa HONESTAMENTE cada respuesta de forma DIFERENTE
- Si la respuesta es corta o vaga: 1-2 puntos por criterio
- Si la respuesta es buena pero sin detalles: 3 puntos
- Si la respuesta tiene ejemplos concretos: 4-5 puntos
- NO des siempre la misma puntuación

Al final agrega: PUNTOS:X (suma total de los 3 criterios)

Ejemplo de respuesta corta:
Tu respuesta es muy breve. Necesito más detalles y ejemplos específicos.

¿Puedes explicar con más detalle cómo manejaste esa situación?

---EVALUACION---
Claridad: 2/5
Contenido: 1/5
Profesionalismo: 2/5

PUNTOS:5

Ejemplo de respuesta buena:
Excelente, tu respuesta muestra experiencia real y usas ejemplos concretos.

¿Qué aprendiste de esa experiencia?

---EVALUACION---
Claridad: 4/5
Contenido: 5/5
Profesionalismo: 4/5

PUNTOS:13"""

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(full_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error con Gemini: {e}")
        return f"Error al conectar con la IA. Por favor verifica tu API key de Gemini. Error: {str(e)}"
=======
Historial de conversación:
{conversation_text}

Como entrevistador, analiza la respuesta anterior del candidato y genera la siguiente pregunta o comentario apropiado.
Mantén la conversación fluida y profesional. Si el candidato ha respondido bien, continúa con preguntas más específicas.
Si necesita mejorar, proporciona feedback constructivo."""

    try:
        # Try different models in order of preference
        models_to_try = ['gemini-1.5-flash', 'gemini-pro', 'gemini-1.0-pro']

        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content(full_prompt)
                ai_response = response.text.strip()
                # Add a note that this is AI-generated
                if "¡Hola! Soy JoBot" not in ai_response:
                    ai_response += "\n\n*Respuesta generada por IA inteligente*"
                return ai_response
            except Exception as model_error:
                print(f"Model {model_name} failed: {model_error}")
                continue

        # If all models fail, use a hybrid approach: try to get AI response first, fallback to structured conversation
        try:
            # Try to get at least one model working with a simpler prompt
            simple_model = genai.GenerativeModel('gemini-pro')
            simple_prompt = f"""Como entrevistador profesional, responde a este candidato basándote en su mensaje anterior.
Mensaje del candidato: {messages_history[-1].content if messages_history else 'Hola, me gustaría practicar una entrevista'}

Historial breve: {conversation_text[-500:] if conversation_text else 'Primera interacción'}

Genera una respuesta natural y profesional que ayude al candidato a desarrollar sus habilidades de entrevista."""

            response = simple_model.generate_content(simple_prompt)
            ai_response = response.text.strip()
            return ai_response + "\n\n*Respuesta generada por IA*"

        except Exception as e:
            print(f"Simple AI approach failed: {e}")

            # Final fallback to structured conversation
            if not conversation_text.strip():
                return "¡Hola! Soy JoBot, tu entrenador virtual de entrevistas. Me gustaría conocerte mejor para poder ayudarte a practicar tus habilidades de entrevista. ¿Podrías contarme un poco sobre tu experiencia profesional y qué tipo de puesto te interesa?"
            else:
                # Create a dynamic conversation flow that simulates AI interview training
                user_messages = [msg for msg in messages_history if msg.sender == 'user']

                if not user_messages:
                    return "¡Hola! Soy JoBot, tu entrenador virtual de entrevistas. Me gustaría conocerte mejor para poder ayudarte a practicar tus habilidades de entrevista. ¿Podrías contarme un poco sobre tu experiencia profesional y qué tipo de puesto te interesa?"

                conversation_length = len(user_messages)
                last_message = user_messages[-1].content.lower()

                # Try to analyze the content and respond contextually
                if any(word in last_message for word in ["experiencia", "trabajo", "puesto", "rol", "cargo"]):
                    return "¡Excelente! Gracias por compartir tu experiencia. Para prepararte mejor, me gustaría profundizar. ¿Podrías contarme sobre un proyecto específico o responsabilidad que hayas tenido que fue particularmente desafiante o gratificante para ti?"

                elif any(word in last_message for word in ["fortaleza", "habilidad", "bueno", "mejor"]):
                    return "¡Muy bien! Las fortalezas son clave en las entrevistas. ¿Podrías darme un ejemplo concreto de cómo has aplicado una de tus fortalezas principales en una situación real de trabajo?"

                elif any(word in last_message for word in ["desafío", "problema", "difícil", "complicado"]):
                    return "¡Interesante! Los desafíos muestran resiliencia. ¿Podrías contarme qué aprendiste de esa experiencia y cómo cambió tu enfoque profesional?"

                elif any(word in last_message for word in ["motivación", "objetivo", "meta", "futuro"]):
                    return "¡Perfecto! La motivación es fundamental. ¿Cómo mantienes esa motivación en tu día a día laboral y qué pasos concretos estás dando para alcanzar tus objetivos?"

                else:
                    # Generic progression based on conversation length
                    generic_responses = [
                        "¡Gracias por tu respuesta! ¿Podrías contarme más sobre algún aspecto específico de tu experiencia profesional que te gustaría desarrollar o mejorar?",
                        "¡Excelente! Ahora hablemos de situaciones prácticas. ¿Podrías describir una situación donde tuviste que tomar una decisión importante en el trabajo?",
                        "¡Muy bien! Las habilidades blandas son cruciales. ¿Cómo manejas la comunicación con diferentes tipos de stakeholders en tu trabajo?",
                        "¡Perfecto! ¿Podrías contarme sobre una situación donde tuviste que aprender algo nuevo rápidamente para completar una tarea?",
                        "¡Interesante! ¿Cómo contribuyes al trabajo en equipo y qué rol sueles tomar en proyectos grupales?"
                    ]

                    response_index = conversation_length % len(generic_responses)
                    return generic_responses[response_index]

    except Exception as e:
        return f"Lo siento, tuve un problema técnico. ¿Podrías repetir tu respuesta anterior? Error: {str(e)}"

>>>>>>> origin/main

@login_required
def interview(request, session_id=None):
    """Main interview view"""
    if session_id:
        session = get_object_or_404(InterviewSession, id=session_id, user=request.user)
        messages = session.messages.all()
    else:
        # Create new session if none specified
        session = InterviewSession.objects.create(
            user=request.user,
            interview_type='general',
            title='Nueva Entrevista'
        )
        messages = []

        # Generate initial bot message
<<<<<<< HEAD
        initial_response = get_gemini_response([], session)
=======
        initial_response = get_gemini_response([], session.interview_type)
>>>>>>> origin/main
        Message.objects.create(
            session=session,
            sender='bot',
            content=initial_response
        )
        messages = session.messages.all()

    # Get all user sessions for sidebar
    user_sessions = InterviewSession.objects.filter(user=request.user).order_by('-updated_at')[:5]
<<<<<<< HEAD
    
    # Get level info
    level_info = session.get_level_info()
    
    # Get user streak
    streak, created = UserStreak.objects.get_or_create(user=request.user)
    
    import json
    practice_dates_json = json.dumps(streak.practice_dates)
=======
>>>>>>> origin/main

    context = {
        'session': session,
        'messages': messages,
        'user_sessions': user_sessions,
<<<<<<< HEAD
        'total_points': session.total_points,
        'current_level': level_info['level'],
        'level_name': level_info['name'],
        'next_level_points': level_info['next'],
        'progress': level_info['progress'],
        'current_streak': streak.current_streak,
        'practice_dates': practice_dates_json,
=======
>>>>>>> origin/main
    }

    return render(request, 'interview.html', context)

<<<<<<< HEAD
=======

>>>>>>> origin/main
@csrf_exempt
@require_POST
@login_required
def send_message(request, session_id):
<<<<<<< HEAD
    """AJAX endpoint to send message and get AI response"""
=======
    """Vista que recibe el mensaje del usuario vía AJAX y devuelve la respuesta de la IA,
    calculando además el tiempo que el usuario tardó en responder a la última pregunta del bot."""
>>>>>>> origin/main
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)

<<<<<<< HEAD
        # Get or create session
        session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

        # Save user message
        Message.objects.create(
=======
        # Obtener la sesión
        session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

        # 1) Guardar mensaje del usuario
        user_msg = Message.objects.create(
>>>>>>> origin/main
            session=session,
            sender='user',
            content=user_message
        )
<<<<<<< HEAD
        
        # Update user streak
        streak, created = UserStreak.objects.get_or_create(user=request.user)
        streak_updated = streak.update_streak()

        # Get conversation history
        messages_history = list(session.messages.all())

        # Generate AI response
        ai_response = get_gemini_response(messages_history, session)

        # Extract points and evaluation from AI response
        points_awarded = 0
        clean_response = ai_response
        evaluation_html = ""
        
        if 'PUNTOS:' in ai_response:
            try:
                parts = ai_response.split('PUNTOS:')
                clean_response = parts[0].strip()
                points_str = parts[1].strip().split()[0]
                points_awarded = int(points_str)
                
                # Add points to session
                if points_awarded > 0:
                    session.add_points(points_awarded)
            except:
                pass
        
        # Extract evaluation section
        if '---EVALUACION---' in clean_response:
            parts = clean_response.split('---EVALUACION---')
            clean_response = parts[0].strip()
            eval_text = parts[1].strip()
            
            # Format evaluation as HTML
            evaluation_html = '<div class="evaluation-box">'
            evaluation_html += '<strong>📊 Evaluación:</strong><br>'
            for line in eval_text.split('\n'):
                if line.strip():
                    evaluation_html += f'{line}<br>'
            evaluation_html += '</div>'
            clean_response += '\n\n' + evaluation_html

        # Save AI response (without PUNTOS: line)
        Message.objects.create(
            session=session,
            sender='bot',
            content=clean_response
        )

        # Update session timestamp
        session.save()
        
        # Get updated level info
        level_info = session.get_level_info()

        return JsonResponse({
            'success': True,
            'ai_response': clean_response,
            'points_awarded': points_awarded,
            'total_points': session.total_points,
            'current_level': level_info['level'],
            'level_name': level_info['name'],
            'next_level_points': level_info['next'],
            'progress': level_info['progress'],
            'streak_updated': streak_updated,
            'current_streak': streak.current_streak,
            'practice_dates': streak.practice_dates
=======

        # 2) Buscar la última pregunta del bot ANTERIOR a este mensaje
        last_bot_msg = session.messages.filter(
            sender='bot',
            timestamp__lt=user_msg.timestamp
        ).order_by('-timestamp').first()

        # 3) Si existe, calcular tiempo de respuesta en segundos
        if last_bot_msg:
            delta = user_msg.timestamp - last_bot_msg.timestamp
            user_msg.response_time_seconds = delta.total_seconds()
            user_msg.save(update_fields=['response_time_seconds'])

        # 4) Obtener historial de conversación (ya incluye el mensaje del usuario)
        messages_history = list(session.messages.all())

        # 5) Generar respuesta de la IA
        ai_response = get_gemini_response(messages_history, session.interview_type)

        # 6) Guardar respuesta del bot
        Message.objects.create(
            session=session,
            sender='bot',
            content=ai_response
        )

        # Actualizar timestamp de la sesión
        session.save()

        return JsonResponse({
            'success': True,
            'ai_response': ai_response
>>>>>>> origin/main
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

<<<<<<< HEAD
=======

>>>>>>> origin/main
@login_required
def create_session(request):
    """Create new interview session"""
    if request.method == 'POST':
        interview_type = request.POST.get('interview_type', 'general')
        title = request.POST.get('title', 'Nueva Entrevista')
<<<<<<< HEAD
        duration = request.POST.get('duration', 'standard')
        difficulty = request.POST.get('difficulty', 'intermediate')
        focus_area = request.POST.get('focus_area', 'communication')
        position_level = request.POST.get('position_level', '')
=======
>>>>>>> origin/main

        session = InterviewSession.objects.create(
            user=request.user,
            interview_type=interview_type,
<<<<<<< HEAD
            title=title,
            duration=duration,
            difficulty=difficulty,
            focus_area=focus_area,
            position_level=position_level
        )

        # Generate initial message with session parameters
        initial_response = get_gemini_response([], session)
=======
            title=title
        )

        # Generate initial message
        initial_response = get_gemini_response([], session.interview_type)
>>>>>>> origin/main
        Message.objects.create(
            session=session,
            sender='bot',
            content=initial_response
        )

        return JsonResponse({
            'success': True,
            'session_id': session.id,
            'redirect_url': f'/interview/{session.id}/'
        })

    return JsonResponse({'error': 'Método no permitido'}, status=405)
<<<<<<< HEAD
=======


@login_required
def session_summary(request, session_id):
    """
    Devuelve el tiempo promedio de respuesta del usuario en la sesión
    y una recomendación para ajustar la extensión de sus respuestas.
    """
    session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

    # Usamos el helper definido en el modelo InterviewSession
    avg_seconds = session.get_average_response_time()

    if avg_seconds is None:
        return JsonResponse({
            'success': False,
            'error': 'Todavía no hay suficientes respuestas para calcular un promedio.'
        })

    # Formato mm:ss
    minutes = int(avg_seconds // 60)
    seconds = int(avg_seconds % 60)
    formatted = f"{minutes:02d}:{seconds:02d}"

    # Recomendaciones según el promedio (No estoy seguro como implementar)
    """
    if avg_seconds < 40:
        recommendation = (
            "Tus respuestas son muy cortas. En una entrevista real, intenta desarrollar más tus ideas, "
            "usando por ejemplo el esquema STAR (Situación, Tarea, Acción, Resultado) y agregando ejemplos concretos."
        )
    elif avg_seconds <= 120:
        recommendation = (
            "Estás en un rango muy bueno (entre 40 y 120 segundos por respuesta). "
            "Mantén respuestas claras, estructuradas y con ejemplos, sin extenderte demasiado."
        )
    elif avg_seconds <= 240:
        recommendation = (
            "Tus respuestas tienden a ser largas. Intenta ir más al punto: resume el contexto en una frase, "
            "enfócate en qué hiciste y qué resultados obtuviste, evitando detalles secundarios."
        )
    else:
        recommendation = (
            "Tus respuestas son demasiado extensas. En entrevistas reales, es raro que una respuesta de más de 4 minutos "
            "sea bien recibida. Recorta detalles y céntrate en el problema, tu acción y el resultado principal."
        )

    """
    return JsonResponse({
        'success': True,
        'average_seconds': avg_seconds,
        'average_formatted': formatted,
        #'recommendation': recommendation,
    })
>>>>>>> origin/main
