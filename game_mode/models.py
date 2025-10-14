from django.db import models
from django.conf import settings

class Nivel(models.Model):
    numero = models.IntegerField(unique=True)
    puntaje_minimo = models.IntegerField(default=0) #Para pasar de nivel
    tipo_entrevistador = models.CharField(max_length=50, default="general")

class Pregunta(models.Model):
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='nivel_asignado')
    texto = models.TextField()
    num_pregunta = models.IntegerField()

class Progreso(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='usuario_id')
    nivel_actual = models.IntegerField(default=1)
    pregunta_actual = models.IntegerField(default=1)
    puntuacion_niveles = models.JSONField(default=dict)

class Chat(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    creado = models.DateTimeField(auto_now_add=True)
    resumen = models.JSONField(default=dict)

class Mensaje(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    nivel = models.IntegerField()
    remitente = models.TextField(max_length=10)
    contenido = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
