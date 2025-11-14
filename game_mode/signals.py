from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Mensaje, Chat
from .views import *

#Trigger para que cuando Chat se crea, se creen los 9 niveles con el texto de bienvenida
@receiver(post_save, sender=Chat)
def crear_mensajes_iniciales(sender, instance, created, **kwargs):
    if created:  # Solo cuando el Chat se crea por primera vez
        niveles = range(1, 10)  # 9 niveles (1 al 9)
        usuario_obj = instance.usuario #Obtenemos el objeto Usuario del chat acabado de crear
        for nivel in niveles:
            contenido = prompt_inicial(nivel, usuario_obj)
            Mensaje.objects.create(
                chat=instance,
                nivel=nivel,
                remitente="robot",  
                contenido=contenido,      
            )

def prompt_inicial(nivelSeleccionado, usuario_obj):
    tipo_entrevistador = get_nivel_obj(nivelSeleccionado).tipo_entrevistador
    pregunta1 = get_pregunta_text(nivelSeleccionado,1)
    mensaje_bienvenida = f"**¡Hola! Soy JoBot 👋**\nBienvenido al **nivel {nivelSeleccionado}**. En esta etapa te acompañaré como un **entrevistador {tipo_entrevistador}**, diseñado para ayudarte a ganar confianza mientras practicas tus respuestas.\n\nNo te preocupes por hacerlo perfecto desde el inicio: estoy aquí para guiarte, apoyarte y ayudarte a mejorar paso a paso. Empecemos con la primera pregunta.\n{pregunta1}"

    return mensaje_bienvenida