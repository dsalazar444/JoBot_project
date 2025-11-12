from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from . import views as views

urlpatterns = [
    path('', login_required(views.init), name='init_multiplayer'),
]