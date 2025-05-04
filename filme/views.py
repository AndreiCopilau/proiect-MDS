from django.shortcuts import render # type: ignore
from .utils import get_filme_populare, get_detalii_film

def home(request):
    filme = get_filme_populare
    return render(request, 'filme/home.html', {'filme': filme})

def detalii_film(request, film_id):
    film = get_detalii_film(film_id)
    return render(request, 'filme/detalii_film.html', {'film': film})
    # if film:
    #     return render(request, 'filme/detalii_film.html', {'film': film})
    # else:
    #     return render(request, 'filme/eroare.html', {'mesaj': 'Filmul nu a fost gasit.'})