from django.shortcuts import render, redirect # type: ignore
from .utils import get_filme_populare, get_detalii_film

from django.contrib.auth import login, authenticate # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth import logout # type: ignore

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