from django.shortcuts import render, redirect # type: ignore
from .utils import get_filme_populare, get_detalii_film

from django.contrib.auth import login, authenticate # type: ignore
from django.contrib.auth.forms import UserCreationForm # type: ignore
from django.contrib.auth import logout # type: ignore

from django.shortcuts import get_object_or_404 #adaugat de radu
from .models import Film, Favorite #adagat de radu
from .models import ViewHistory  #adagat de radu
from django.contrib.auth.decorators import login_required #adagat de radu

def home(request):
    filme = get_filme_populare
    return render(request, 'filme/home.html', {'filme': filme})

def detalii_film(request, film_id):
    film = get_detalii_film(film_id)
    user_favorite_ids = []
    
    if request.user.is_authenticated:
        # Verifică favorite
        user_favorite_ids = Favorite.objects.filter(
            user=request.user,
            film__id_tmdb=film_id
        ).values_list('film__id_tmdb', flat=True)
        
        # Obține sau creează filmul în baza noastră
        film_obj, created = Film.objects.get_or_create(
            id_tmdb=film_id,
            defaults={
                'titlu': film['title'],
                'poster_path': film['poster_path']
            }
        )
        
        # Salvează vizionarea în istoric (folosind obiectul Film)
        ViewHistory.objects.create(
            user=request.user,
            film=film_obj  # Folosim obiectul Film creat mai sus
        )
    
    return render(request, 'filme/detalii_film.html', {
        'film': film,  # Date din API
        'user_favorite_ids': user_favorite_ids
    })
    
# def register(request):
#     if request.method == 'POST':
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             # username = form.cleaned_data.get('username')
#             # password = form.cleaned_data.get('password1')
#             # user = authenticate(username=username, password=password)
#             # login(request, user)
#             # return render(request, 'filme/home.html', {'mesaj': 'Cont creat cu succes!'})
#             user = form.save()  # creează utilizatorul
#             login(request, user)  # îl conectează direct
#             return redirect('home')
#     else:
#         form = UserCreationForm()
#     return render(request, 'filme/register.html', {'form': form})  

# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         user = authenticate(request, username=username, password=password)
#         if user is not None:
#             login(request, user)
#             # return render(request, 'filme/home.html', {'mesaj': 'Te-ai conectat cu succes!'})
#             return redirect('home')
#         else:
#             return render(request, 'filme/login.html', {'mesaj': 'Username sau parola gresita!'})
#     return render(request, 'filme/login.html')  

# def user_logout(request):
#     logout(request)
#     return redirect('home')
    # return render(request, 'filme/home.html', {'mesaj': 'Te-ai deconectat cu succes!'})
    
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import mail_admins
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib.auth import login, logout
from .forms import UserCustomForm, CustomAuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
import datetime

from .models import UserCustom

failed_login_attempts = {}

def inregistrare_utilizator(request):
    if request.method == 'POST':
        form = UserCustomForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['username'].lower() == 'admin':
                messages.error(request, "Nu poti folosi acest username.")
                return redirect('inregistrare_utilizator')

            try:
                user = form.save(commit=False)
                user.cod = get_random_string(20)
                user.email_confirmat = False
                user.save()
            except Exception:
                messages.error(request, "A aparut o eroare. Te rugam sa incerci din nou.")
                return redirect('inregistrare_utilizator')

            subject = "Confirmare email - Bun venit pe site-ul nostru!"
            message = f"""
            Salut {user.first_name} {user.last_name},

            Bine ai venit pe site-ul nostru! Username-ul tau este: {user.username}.
            Te rugam sa confirmi adresa de email apasand pe linkul de mai jos:

            http://127.0.0.1:8000/confirma_mail/{user.cod}/

            Multumim ca esti alaturi de noi!
            """
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [user.email]

            try:
                from django.core.mail import send_mail
                send_mail(subject, message, from_email, recipient_list)
                messages.success(request, "Contul a fost creat cu succes! Te rugam sa confirmi adresa de email.")
            except Exception:
                messages.error(request, "Eroare la trimiterea emailului. Te rugam sa incerci din nou.")

            return redirect('login')
    else:
        form = UserCustomForm()

    return render(request, 'filme/register.html', {'form': form})


@csrf_protect
def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if not user.email_confirmat:
                messages.error(request, "Adresa de email nu este confirmata. Te rugam sa verifici emailul si sa urmezi linkul de confirmare.")
                return redirect('login')

            username = user.username
            if username in failed_login_attempts:
                del failed_login_attempts[username]

            login(request, user)
            return redirect('home')
        else:
            username = request.POST.get('username', 'necunoscut')
            failed_login_attempts[username] = failed_login_attempts.get(username, []) + [now()]

            recent_attempts = [
                attempt for attempt in failed_login_attempts[username]
                if now() - attempt < datetime.timedelta(minutes=2)
            ]

            if len(recent_attempts) >= 3:
                subject = "Logari suspecte"
                message = f"Au fost detectate 3 incercari esuate pentru utilizatorul: {username}."
                html_message = f"""
                <h1 style=\"color: red;\">Logari suspecte</h1>
                <p>Au fost detectate 3 incercari esuate pentru utilizatorul: <strong>{username}</strong>.</p>
                """
                mail_admins(subject, message, html_message=html_message)

            messages.error(request, "Autentificare esuata. Date incorecte.")

    else:
        form = CustomAuthenticationForm()

    return render(request, 'filme/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')


def confirma_mail(request, cod):
    try:
        user = UserCustom.objects.get(cod=cod)
        user.email_confirmat = True
        user.cod = None
        user.save()
        mesaj = "E-mailul a fost confirmat cu succes! Te poti autentifica acum."
    except UserCustom.DoesNotExist:
        mesaj = "Codul de confirmare este invalid sau a expirat."

    return render(request, 'filme/confirma_mail.html', {'mesaj': mesaj})


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



@login_required
def istoric_vizionari(request):
    istoric = ViewHistory.objects.filter(
        user=request.user
    ).select_related('film').order_by('-viewed_at')
    
    return render(request, 'filme/istoric.html', {
        'istoric': istoric
    })
    