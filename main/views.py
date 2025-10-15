from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def login_view(request):
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password') or ''
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Credenciales inválidas.')
    return render(request, 'auth/login.html')

def signup_view(request):
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        name = (request.POST.get('username') or '').strip()  # tu "Nombre" visible
        password = request.POST.get('password') or ''

        # Validaciones básicas
        if not email or not password:
            messages.error(request, 'Email y contraseña son obligatorios.')
            return render(request, 'auth/signup.html', status=400)

        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, 'Ingresa un email válido.')
            return render(request, 'auth/signup.html', status=400)

        if len(password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'auth/signup.html', status=400)

        # Chequear duplicado por username (usaremos el email como username)
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese email.')
            return render(request, 'auth/signup.html', status=400)

        # Crear usuario -> username = email
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        # Guardar el "Nombre" visible en first_name (o puedes usar perfiles más tarde)
        user.first_name = name
        user.save()

        # Autologin
        auth.login(request, user)
        return redirect('home')

    # GET
    return render(request, 'auth/signup.html')

def reviews(request):
    return render(request, 'reviews.html')

def logout_view(request):
    logout(request)
    return redirect("home")