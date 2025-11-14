from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import google.generativeai as genai
from .models import InterviewSession, Message, UserStreak
from django.conf import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_gemini_response(messages_history, session):
    """Generate response using Google Gemini with session parameters"""

    # Create the model
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Build conversation context
    conversation_text = ""
    for msg in messages_history[-10:]:  # Last 10 messages for context
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
    }

    system_prompt = prompts.get(interview_type, prompts['general'])

    # Full prompt
    if not conversation_text.strip():
        # First interaction
        full_prompt = f"""{system_prompt}

Esta es la primera interacción. Saluda de forma breve y profesional, luego haz una pregunta de apertura para conocer al candidato.

IMPORTANTE: No uses asteriscos ni markdown. Escribe en texto plano con buena estructura.

Al final agrega: PUNTOS:0"""
    else:
        # Continuing conversation
        full_prompt = f"""{system_prompt}

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
        initial_response = get_gemini_response([], session)
        Message.objects.create(
            session=session,
            sender='bot',
            content=initial_response
        )
        messages = session.messages.all()

    # Get all user sessions for sidebar
    user_sessions = InterviewSession.objects.filter(user=request.user).order_by('-updated_at')[:5]
    
    # Get level info
    level_info = session.get_level_info()
    
    # Get user streak
    streak, created = UserStreak.objects.get_or_create(user=request.user)
    
    import json
    practice_dates_json = json.dumps(streak.practice_dates)

    context = {
        'session': session,
        'messages': messages,
        'user_sessions': user_sessions,
        'total_points': session.total_points,
        'current_level': level_info['level'],
        'level_name': level_info['name'],
        'next_level_points': level_info['next'],
        'progress': level_info['progress'],
        'current_streak': streak.current_streak,
        'practice_dates': practice_dates_json,
    }

    return render(request, 'interview.html', context)

@csrf_exempt
@require_POST
@login_required
def send_message(request, session_id):
    """AJAX endpoint to send message and get AI response"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()

        if not user_message:
            return JsonResponse({'error': 'Mensaje vacío'}, status=400)

        # Get or create session
        session = get_object_or_404(InterviewSession, id=session_id, user=request.user)

        # Save user message
        Message.objects.create(
            session=session,
            sender='user',
            content=user_message
        )
        
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
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def create_session(request):
    """Create new interview session"""
    if request.method == 'POST':
        interview_type = request.POST.get('interview_type', 'general')
        title = request.POST.get('title', 'Nueva Entrevista')
        duration = request.POST.get('duration', 'standard')
        difficulty = request.POST.get('difficulty', 'intermediate')
        focus_area = request.POST.get('focus_area', 'communication')
        position_level = request.POST.get('position_level', '')

        session = InterviewSession.objects.create(
            user=request.user,
            interview_type=interview_type,
            title=title,
            duration=duration,
            difficulty=difficulty,
            focus_area=focus_area,
            position_level=position_level
        )

        # Generate initial message with session parameters
        initial_response = get_gemini_response([], session)
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
