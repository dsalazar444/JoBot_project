from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views as views

urlpatterns = [
    path('index/', login_required(views.init), name='init_game_mode'),
    path('api/mensajes/', login_required(views.procesar_request_bd), name='mensajes'),
    path('api/cargarChats/', login_required(views.obtener_chats_pasados_request), name='cargar_chats'),
]
