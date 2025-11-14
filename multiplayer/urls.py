from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views as views

urlpatterns = [
    path('', login_required(views.init), name='init_multiplayer'),
    path('api/obtenerPreguntas/', login_required(views.enviar_preguntas), name='get_preguntas'),
    path('api/respuestaUser/', login_required(views.procesar_respuesta), name='procesar_respuesta'),
]