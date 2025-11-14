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
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        
        if email and password:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', '/')
                return redirect(next_url)
            else:
                messages.error(request, 'Email o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor completa todos los campos.')
    
    return render(request, 'auth/login.html')

def signup_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        # Validaciones básicas
        if not email or not username or not password:
            messages.error(request, 'Todos los campos son obligatorios.')
            return render(request, 'auth/signup.html')
        
        if len(password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return render(request, 'auth/signup.html')
        
        # Verificar si el email ya existe
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese email.')
            return render(request, 'auth/signup.html')
        
        try:
            # Crear usuario usando email como username
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=username
            )
            
            # Login automático
            login(request, user)
            messages.success(request, 'Cuenta creada exitosamente.')
            return redirect('home')
            
        except Exception as e:
            messages.error(request, 'Error al crear la cuenta. Intenta de nuevo.')
    
    return render(request, 'auth/signup.html')

def reviews(request):
    return render(request, 'reviews.html')

def logout_view(request):
    logout(request)
    return redirect("home")
