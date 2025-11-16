from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from game_mode.models import Progreso, Chat


# esto es como un trigger en mySQL, que se activa despues de que se guarda un
# nuevo usuario en el modelo Usuario
@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def crear_progreso_automatico(sender, instance, created, **kwargs):
    if created:
        Progreso.objects.create(usuario=instance) #Porque los demás atributos tomarán su valor default.

#Creamos registro en chat despues de que se cree un nuevo usuario
@receiver(post_save, sender = settings.AUTH_USER_MODEL)
def crear_chat_automatico(sender, instance, created, **kwargs):
    if created:
        Chat.objects.create(usuario=instance)