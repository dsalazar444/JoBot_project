from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages, auth
from django.contrib.auth.models import User
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
        email = (request.POST.get('email') or '').strip().lower()
        name = (request.POST.get('username') or '').strip()  # “Nombre” visible
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

        # Usamos el email como username
        if User.objects.filter(username=email).exists():
            messages.error(request, 'Ya existe una cuenta con ese email.')
            return render(request, 'auth/signup.html', status=400)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password
        )
        user.first_name = name
        user.save()

        auth.login(request, user)
        messages.success(request, 'Cuenta creada con éxito.')
        return redirect('home')

    # GET
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
