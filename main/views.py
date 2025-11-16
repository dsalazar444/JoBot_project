from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth
from user.models import Usuario
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def reviews(request):
    return render(request, 'reviews.html')

# ---------- LOGIN ----------
def login_view(request):
    """
    Login por email (usado como username).
    Soporta ?next=/ruta/ para redirigir después de loguear.
    """
    next_url = request.GET.get('next') or request.POST.get('next')

    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password') or ''

        if not email or not password:
            messages.error(request, 'Email y contraseña son obligatorios.')
            return render(request, 'auth/login.html', {'next': next_url}, status=400)

        # Usamos el email guardado en username
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, '¡Bienvenido de nuevo!')
            return redirect(next_url or 'home')

        messages.error(request, 'Usuario o contraseña incorrectos.')
        return render(request, 'auth/login.html', {'next': next_url}, status=401)

    # GET
    return render(request, 'auth/login.html', {'next': next_url})

# ---------- SIGNUP ----------
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
        if Usuario.objects.filter(email=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese email.')
            return render(request, 'auth/signup.html')
        
        try:
            # Crear usuario usando email como username
            user = Usuario.objects.create_user(
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

# ---------- LOGOUT ----------
def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada.')
    return redirect('home')

# ---------- OLVIDÓ CONTRASEÑA (placeholder) ----------
def forgot_view(request):
    # Página simple con “Habilitado próximamente”
    return render(request, 'auth/soon.html', {'title': 'Habilitado próximamente'})
