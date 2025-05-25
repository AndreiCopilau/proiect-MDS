from .models import Film

def salveaza_film_tmdb_daca_nu_exista(film_dict):
    id_tmdb = film_dict.get('id')
    if not id_tmdb:
        return None

    film, created = Film.objects.get_or_create(
        id_tmdb=id_tmdb,
        defaults={
            'titlu': film_dict.get('title'),
            'poster_path': film_dict.get('poster_path'),
            'genre_ids': film_dict.get('genre_ids', [])
        }
    )

    # dacă filmul există dar nu are genuri, le completăm
    if not created and not film.genre_ids and film_dict.get('genre_ids'):
        film.genre_ids = film_dict['genre_ids']
        film.save()

    return film


import requests # type: ignore
from django.conf import settings # type: ignore

def get_filme_populare():
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={settings.TMDB_API_KEY}&language=en-US&page=1"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        filme = data.get('results', [])

        for film in filme:
            salveaza_film_tmdb_daca_nu_exista(film)

        return filme  
    return []


def get_detalii_film(film_id):
    url = f"https://api.themoviedb.org/3/movie/{film_id}?api_key={settings.TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None

def cauta_filme_tmdb(query, pagina=1):
    url = 'https://api.themoviedb.org/3/search/movie'
    params = {
        'api_key': settings.TMDB_API_KEY,
        'query': query,
        'language': 'ro-RO',
        'page': pagina
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        filme = data.get('results', [])

        # 🔄 salvare filme în DB
        for film in filme:
            salveaza_film_tmdb_daca_nu_exista(film)

        return {
            'filme': data.get('results', []),
            'pagina_curenta': data.get('page', 1),
            'total_pagini': data.get('total_pages', 1)
        }
    return {'filme': [], 'pagina_curenta': 1, 'total_pagini': 1}



def get_video_film(film_id):
    url = f"https://api.themoviedb.org/3/movie/{film_id}/videos?api_key={settings.TMDB_API_KEY}&language=en-US"
    response = requests.get(url)
    if response.status_code == 200:
        videos = response.json().get('results', [])
        for video in videos:
            if video['site'] == 'YouTube' and video['type'] == 'Trailer':
                return f"https://www.youtube.com/embed/{video['key']}"
    return None

# pentru a face filtrare dupa toate filmele si sa existe paginare
def descopera_filme_tmdb(gen=None, min_rating=None, pagina=1):
    url = 'https://api.themoviedb.org/3/discover/movie'
    params = {
        'api_key': settings.TMDB_API_KEY,
        'language': 'ro-RO',
        'sort_by': 'popularity.desc',
        'page': pagina
    }

    if gen:
        params['with_genres'] = gen
    if min_rating:
        try:
            params['vote_average.gte'] = float(min_rating)
        except ValueError:
            pass

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        filme = data.get('results', [])

        # 🔄 salvare filme în DB
        for film in filme:
            salveaza_film_tmdb_daca_nu_exista(film)

        return {
            'filme': filme,
            'pagina_curenta': data.get('page', 1),
            'total_pagini': data.get('total_pages', 1)
        }
    return {'filme': [], 'pagina_curenta': 1, 'total_pagini': 1}


from collections import Counter
from .models import ViewHistory, Film

def recomandari_pe_genuri(user, top_n=3, filme_per_gen=3):
    from collections import Counter
    from .models import ViewHistory, Film

    vizionari = ViewHistory.objects.filter(user=user).select_related('film')
    toate_genurile = []

    filme_vizionate_ids = set(v.film.id_tmdb for v in vizionari)

    for viz in vizionari:
        toate_genurile.extend(viz.film.genre_ids)

    genuri_preferate = [gen for gen, _ in Counter(toate_genurile).most_common(top_n)]

    recomandari = []
    filme_recomandate_ids = set()

    for gen_id in genuri_preferate:
        rezultat = descopera_filme_tmdb(gen=gen_id)
        if rezultat and 'filme' in rezultat:
            for film in rezultat['filme']:
                if film['id'] not in filme_vizionate_ids and film['id'] not in filme_recomandate_ids:
                    recomandari.append(film)
                    filme_recomandate_ids.add(film['id'])
                    if len(recomandari) >= top_n * filme_per_gen:
                        break

    return recomandari


import requests
from .models import Film

TMDB_API_KEY = '7c4f52f7a9bfd765ee2774bb2c1ca19c'

def completeaza_genuri_filme():
    base_url = "https://api.themoviedb.org/3/movie/"
    headers = {"Accept": "application/json"}
    filme_fara_genuri = Film.objects.filter(genre_ids=[])

    for film in filme_fara_genuri:
        url = f"{base_url}{film.id_tmdb}"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "ro-RO"  # sau "en-US"
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                data = response.json()
                genuri = data.get("genres", [])
                ids = [g["id"] for g in genuri]
                film.genre_ids = ids
                film.save()
                print(f"✔ Genuri completate pentru: {film.titlu}")
            else:
                print(f"✖ Eroare la {film.titlu} (status {response.status_code})")
        except Exception as e:
            print(f"✖ Eroare la {film.titlu}: {e}")
