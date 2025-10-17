from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import google.generativeai as genai
from .models import InterviewSession, Message
from django.conf import settings

# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_gemini_response(messages_history, interview_type):
    """Generate response using Google Gemini"""

    # Create the model
    model = genai.GenerativeModel('gemini-1.5-flash')

    # Build conversation context
    conversation_text = ""
    for msg in messages_history[-10:]:  # Last 10 messages for context
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
    }

    system_prompt = prompts.get(interview_type, prompts['general'])

    # Full prompt
    if not conversation_text.strip():
        # First interaction
        full_prompt = f"""{system_prompt}

Esta es la primera interacción con el candidato. Comienza con un saludo amigable y una pregunta de apertura
para conocer mejor al candidato y su experiencia profesional."""
    else:
        # Continuing conversation
        full_prompt = f"""{system_prompt}

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
        initial_response = get_gemini_response([], session.interview_type)
        Message.objects.create(
            session=session,
            sender='bot',
            content=initial_response
        )
        messages = session.messages.all()

    # Get all user sessions for sidebar
    user_sessions = InterviewSession.objects.filter(user=request.user).order_by('-updated_at')[:5]

    context = {
        'session': session,
        'messages': messages,
        'user_sessions': user_sessions,
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

        # Get conversation history
        messages_history = list(session.messages.all())

        # Generate AI response
        ai_response = get_gemini_response(messages_history, session.interview_type)

        # Save AI response
        Message.objects.create(
            session=session,
            sender='bot',
            content=ai_response
        )

        # Update session timestamp
        session.save()

        return JsonResponse({
            'success': True,
            'ai_response': ai_response
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def create_session(request):
    """Create new interview session"""
    if request.method == 'POST':
        interview_type = request.POST.get('interview_type', 'general')
        title = request.POST.get('title', 'Nueva Entrevista')

        session = InterviewSession.objects.create(
            user=request.user,
            interview_type=interview_type,
            title=title
        )

        # Generate initial message
        initial_response = get_gemini_response([], session.interview_type)
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
