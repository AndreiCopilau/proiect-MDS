from django.shortcuts import render, redirect # type: ignore
from .utils import get_filme_populare, get_detalii_film

from django.contrib.auth import login, authenticate # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth import logout # type: ignore

from django.shortcuts import get_object_or_404 #adaugat de radu
from .models import Film, Favorite #adagat de radu

def home(request):
    filme = get_filme_populare
    return render(request, 'filme/home.html', {'filme': filme})

def detalii_film(request, film_id):
    film = get_detalii_film(film_id)
    user_favorite_ids = []
    if request.user.is_authenticated:
        user_favorite_ids = Favorite.objects.filter(
            user=request.user,
            film__id_tmdb=film_id
        ).values_list('film__id_tmdb', flat=True)
    
    return render(request, 'filme/detalii_film.html', {
        'film': film,
        'user_favorite_ids': user_favorite_ids
    })
    #return render(request, 'filme/detalii_film.html', {'film': film})
    # if film:
    #     return render(request, 'filme/detalii_film.html', {'film': film})
    # else:
    #     return render(request, 'filme/eroare.html', {'mesaj': 'Filmul nu a fost gasit.'})
    
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # username = form.cleaned_data.get('username')
            # password = form.cleaned_data.get('password1')
            # user = authenticate(username=username, password=password)
            # login(request, user)
            # return render(request, 'filme/home.html', {'mesaj': 'Cont creat cu succes!'})
            user = form.save()  # creează utilizatorul
            login(request, user)  # îl conectează direct
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'filme/register.html', {'form': form})  

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # return render(request, 'filme/home.html', {'mesaj': 'Te-ai conectat cu succes!'})
            return redirect('home')
        else:
            return render(request, 'filme/login.html', {'mesaj': 'Username sau parola gresita!'})
    return render(request, 'filme/login.html')  

def user_logout(request):
    logout(request)
    return redirect('home')
    # return render(request, 'filme/home.html', {'mesaj': 'Te-ai deconectat cu succes!'})
    


#adaugat de radu

def adauga_favorit(request, film_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Obține sau creează filmul în baza noastră de date
    film_data = get_detalii_film(film_id)
    film, created = Film.objects.get_or_create(
        id_tmdb=film_id,
        defaults={
            'titlu': film_data['title'],
            'poster_path': film_data['poster_path']
        }
    )
    
    # Adaugă la favorite
    Favorite.objects.get_or_create(user=request.user, film=film)
    return redirect('detalii_film', film_id=film_id)

def elimina_favorit(request, film_id):
    if not request.user.is_authenticated:
        return redirect('login')
    
    film = get_object_or_404(Film, id_tmdb=film_id)
    Favorite.objects.filter(user=request.user, film=film).delete()
    return redirect('detalii_film', film_id=film_id)

def lista_favorite(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    favorite = Favorite.objects.filter(user=request.user).select_related('film')
    return render(request, 'filme/favorite.html', {'favorite': favorite})