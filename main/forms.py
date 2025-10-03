from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Email"
        })
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Usuario"
        })
        self.fields["password1"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Contraseña"
        })
        self.fields["password2"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Repetir contraseña"
        })
        self.fields["email"].widget.attrs.update({
            "class": "form-control",
            "placeholder": "Email"
        })

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Este email ya está registrado")
        return email

#Crear Login por email y sin usuario
#class LoginForm():
