from django.shortcuts import render

# Funcion que llama a las otras funciones
def init(request):
    niveles_lista = niveles()
    return render(request, "modo_juego.html", {"niveles": niveles_lista})

# Funcion para pintar los niveles disponibles de forma practica
def niveles():
    # Devuelve una lista de niveles (cada nivel es un dict)
    niveles = [
        {"titulo": "Nivel 1"},
        {"titulo": "Nivel 2"},
        {"titulo": "Nivel 3"},
        {"titulo": "Nivel 4"},
        {"titulo": "Nivel 5"},
        {"titulo": "Nivel 6"},
        {"titulo": "Nivel 7"},
        {"titulo": "Nivel 8"},
        {"titulo": "Nivel 9"},
        # ... puede venir de la base de datos
    ]
    return niveles
