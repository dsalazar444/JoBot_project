from django.shortcuts import render, redirect
from django.contrib.auth import logout

# Create your views here.
def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def login_view(request):
    return render(request, 'auth/login.html')

def signup_view(request):
    return render(request, 'auth/signup.html')

def reviews(request):
    return render(request, 'reviews.html')

def logout_view(request):
    logout(request)
    return redirect("home")